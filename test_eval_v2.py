"""v2 批评测的协议切换、评分、失败分层和封存保护回归测试。"""
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest.mock import patch

from parsing.eval_v2 import evaluate, validate_samples
from parsing.errors import ParseConfigError, ParseTransportError
from parsing.llm_client import MockChatClient
from parsing.parse_requirement_v2 import parse_text_v2
from parsing.run_parse import main
from test_parse_v2 import settings


def sample():
    return {
        "id": "V2-D001", "protocol_version": "v2", "split": "dev", "semantic_group": "G1",
        "input": "每天练-10分钟。", "tags": ["multi_issue"],
        "expected_requirement": {"occupation": None, "scene": None, "font": None,
                                 "duration_minutes": None, "status": "invalid"},
        "expected_model_errors": [{"type": "invalid_value", "field": "duration_minutes", "value": -10}],
        "expected_issues": [{"type": "missing_field", "field": "font", "value": None},
                            {"type": "invalid_value", "field": "duration_minutes", "value": -10},
                            {"type": "missing_field", "field": "personalization", "value": None}],
        "expected_api": {"http_status": 200, "code": 400, "data": None},
        "message_check": {"required": ["询问书体"], "forbidden": ["重复询问时长缺失"],
                          "contains": ["-10"], "not_contains": ["你每次想练几分钟"]},
    }


def candidate():
    s = sample()
    return {**s["expected_requirement"], "errors": s["expected_model_errors"]}


class EvalV2Tests(unittest.TestCase):
    def outcome(self, answer=None):
        s = sample()
        client = MockChatClient({s["input"]: json.dumps(answer if answer is not None else candidate(), ensure_ascii=False)})
        return parse_text_v2(s["input"], client=client, settings=settings())

    def test_all_issues_and_semantic_review_is_pending(self):
        s = sample()
        validate_samples([s])
        record = evaluate(s, self.outcome(), None)
        self.assertTrue(record["automated_match"])
        self.assertEqual(len(record["actual_issues"]), 3)
        self.assertIsNone(record["end_to_end_match"])
        self.assertEqual(record["message_review"], "pending")
        self.assertIsNone(record["actual_api"]["data"])

    def test_omitted_model_error_and_wrong_value_fail(self):
        answer = candidate()
        answer["errors"] = []
        self.assertFalse(evaluate(sample(), self.outcome(answer), None)["automated_match"])
        answer = candidate()
        answer["errors"][0]["value"] = 20
        self.assertFalse(evaluate(sample(), self.outcome(answer), None)["model_values_match"])

    def test_missing_labels_and_cross_split_group_rejected(self):
        s = sample()
        del s["expected_requirement"]["scene"]
        with self.assertRaises(ParseConfigError):
            validate_samples([s])
        s = sample()
        other = {**sample(), "id": "V2-V001", "split": "val"}
        with self.assertRaises(ParseConfigError):
            validate_samples([s, other])

    def test_invalid_answer_and_duplicate_missing_rejected(self):
        for mutate in (lambda s: s["expected_requirement"].update(duration_minutes=20),
                       lambda s: s["expected_issues"].append({"type": "missing_field", "field": "duration_minutes", "value": None})):
            s = sample()
            mutate(s)
            with self.assertRaises(ParseConfigError):
                validate_samples([s])

    def test_transport_failure_is_recorded(self):
        r = evaluate(sample(), None, ParseTransportError("timeout"))
        self.assertFalse(r["automated_match"])
        self.assertFalse(r["end_to_end_match"])
        self.assertEqual(r["error_layer"], "transport")

    def test_local_repair_does_not_hide_model_status_failure(self):
        answer = candidate()
        answer["status"] = "complete"
        r = evaluate(sample(), self.outcome(answer), None)
        self.assertEqual(r["actual"]["status"], "invalid")
        self.assertFalse(r["model_status_match"])
        self.assertFalse(r["automated_match"])

    def test_cross_split_exact_input_with_different_group_rejected(self):
        other = {**sample(), "id": "V2-V001", "split": "val", "semantic_group": "other"}
        with self.assertRaises(ParseConfigError):
            validate_samples([sample(), other])

    def test_complete_result_and_wrong_release(self):
        s = sample()
        answer = {"occupation": "学生", "scene": None, "font": "楷书", "duration_minutes": 15,
                  "status": "complete", "errors": []}
        outcome = self.outcome(answer)
        r = evaluate(s, outcome, None)
        self.assertTrue(r["wrong_release"])
        self.assertFalse(r["automated_match"])
        s.update(expected_requirement={k: v for k, v in answer.items() if k != "errors"},
                 expected_model_errors=[], expected_issues=[], message_check={})
        s["expected_api"] = {"http_status": 200, "code": 0, "message": "ok", "data": s["expected_requirement"]}
        validate_samples([s])
        r = evaluate(s, outcome, None)
        self.assertTrue(r["automated_match"])
        self.assertTrue(r["end_to_end_match"])

    def run_cli(self, split="dev", extra=(), answer=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            s = sample()
            s["split"] = split
            samples = root / "samples.jsonl"
            samples.write_text(json.dumps(s, ensure_ascii=False) + "\n")
            mocks = root / "mock.json"
            mocks.write_text(json.dumps({"responses": {s["input"]: json.dumps(answer if answer is not None else candidate(), ensure_ascii=False)}}))
            out, report = root / "runs.jsonl", root / "report.md"
            with patch("parsing.eval_v2.get_settings", return_value=(settings(), [])), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                code = main(["--protocol", "v2", "--client", "mock", "--samples", str(samples),
                             "--mock-file", str(mocks), "--out", str(out), "--report", str(report), *extra])
            return code, out.read_text() if out.exists() else None, report.read_text() if report.exists() else None

    def test_cli_v2_and_metadata(self):
        code, raw, report = self.run_cli()
        self.assertEqual(code, 0)
        r = json.loads(raw)
        self.assertEqual(r["prompt_version"], "v2")
        self.assertEqual(len(r["samples_sha256"]), 64)
        self.assertEqual(len(r["prompt_sha256"]), 64)
        self.assertTrue(r["automated_match"])
        self.assertIn("语义待复核 1", report)
        self.assertIn("mock", report)

    def test_sealed_blocked_before_model_calls_and_no_partial_run(self):
        with patch("parsing.eval_v2.parse_text_v2") as parse:
            for extra in ((), ("--allow-sealed", "--limit", "1"), ("--allow-sealed", "--append")):
                code, raw, _ = self.run_cli("sealed", extra)
                self.assertEqual(code, 2)
                self.assertIsNone(raw)
            parse.assert_not_called()

    def test_sealed_explicit_whole_batch_reports_separately(self):
        code, raw, report = self.run_cli("sealed", ("--allow-sealed",))
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(raw)["split"], "sealed")
        self.assertIn("封存集一次性最终评估", report)

    def test_format_failure_record_and_nonzero_exit(self):
        code, raw, report = self.run_cli(answer={"foo": "bar"})
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(raw)["error_layer"], "format")
        self.assertIn("format", report)

    def test_no_default_v1_samples_for_v2(self):
        with redirect_stderr(io.StringIO()), patch("parsing.eval_v2.get_settings") as config:
            self.assertEqual(main(["--protocol", "v2", "--client", "mock"]), 2)
            config.assert_not_called()


if __name__ == "__main__":
    unittest.main()
