"""W03-1 解析模块的离线测试：不联网、不需要密钥。"""

import contextlib
import io
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

from requirement_rules import RequirementNotReadyError, check_requirement_ready
from schemas import UserRequirement

from parsing.config import Settings
from parsing.errors import ParseConfigError, ParseFormatError, ParseTransportError
from parsing.llm_client import DashScopeChatClient, LLMResponse, MockChatClient
from parsing.parse_requirement import (
    extract_json_object,
    finalize_requirement,
    parse_text,
)
from parsing.run_parse import DEFAULT_MOCK, DEFAULT_SAMPLES, main as run_parse_main

PROJECT_ROOT = Path(__file__).parent


def candidate(**changes):
    data = {
        "occupation": "教师",
        "scene": None,
        "style": "楷书",
        "duration_minutes": 15,
        "goal": None,
        "exclusions": [],
        "status": "complete",
        "follow_up": None,
        "errors": [],
    }
    data.update(changes)
    return data


class FakeClient:
    name = "fake"

    def __init__(self, text):
        self.text = text
        self.calls = []

    def complete(self, system_prompt, user_text):
        self.calls.append((system_prompt, user_text))
        return LLMResponse(text=self.text, model="fake-model", usage={"total_tokens": 12})


def settings(**changes):
    data = dict(
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model="qwen-plus",
        api_key="test-key",
        timeout_seconds=1.0,
        temperature=0.0,
        extra_body={},
        prompt_version="v0",
    )
    data.update(changes)
    return Settings(**data)


class ExtractJsonTests(unittest.TestCase):
    def test_plain_and_fenced_and_prose(self):
        body = json.dumps(candidate(), ensure_ascii=False)
        for text in [body, f"```json\n{body}\n```", f"以下是结果：\n{body}\n以上。"]:
            with self.subTest(text=text[:20]):
                self.assertEqual(extract_json_object(text)["style"], "楷书")

    def test_not_json(self):
        for text in ["", "我不知道", "[1, 2, 3]"]:
            with self.subTest(text=text), self.assertRaises(ParseFormatError):
                extract_json_object(text)


class FinalizeTests(unittest.TestCase):
    def test_clean_output_is_complete(self):
        requirement, warnings = finalize_requirement(candidate())
        self.assertEqual(requirement.status, "complete")
        self.assertEqual(warnings, [])
        check_requirement_ready(requirement)

    def test_model_cannot_mark_complete_without_style(self):
        requirement, _ = finalize_requirement(candidate(style=None))
        self.assertEqual(requirement.status, "needs_clarification")
        self.assertIn("书体", requirement.follow_up)
        with self.assertRaises(RequirementNotReadyError):
            check_requirement_ready(requirement)

    def test_model_cannot_mark_complete_without_personalization(self):
        requirement, _ = finalize_requirement(candidate(occupation=None))
        self.assertEqual(requirement.status, "needs_clarification")
        self.assertIn("场景", requirement.follow_up)

    def test_missing_duration_when_model_says_complete(self):
        requirement, _ = finalize_requirement(candidate(duration_minutes=None))
        self.assertEqual(requirement.status, "needs_clarification")
        self.assertIn("几分钟", requirement.follow_up)

    def test_illegal_values_never_reach_expected(self):
        requirement, _ = finalize_requirement(candidate(duration_minutes=-10))
        self.assertIsNone(requirement.duration_minutes)
        self.assertEqual(requirement.status, "invalid")
        self.assertEqual(requirement.errors[0].type, "invalid_value")
        self.assertEqual(requirement.errors[0].value, -10)
        with self.assertRaises(RequirementNotReadyError):
            check_requirement_ready(requirement)

    def test_unsupported_style_keeps_original_value_in_errors(self):
        requirement, _ = finalize_requirement(candidate(style="草书"))
        self.assertIsNone(requirement.style)
        self.assertEqual(requirement.status, "invalid")
        self.assertEqual(requirement.errors[0].type, "unsupported_style_value")
        self.assertEqual(requirement.errors[0].value, "草书")

    def test_model_conflict_cannot_override_unsupported_style(self):
        """裁决 C-01：枚举外书体一律 invalid，不再跟随模型自报 conflict。"""
        requirement, warnings = finalize_requirement(candidate(
            style="草书", status="conflict", follow_up="是否改用楷书？",
            errors=[{"type": "unsupported_style_value", "field": "style", "value": "草书"}],
        ))
        self.assertIsNone(requirement.style)
        self.assertEqual(requirement.status, "invalid")
        self.assertTrue(any("C-01" in item for item in warnings))

    def test_same_field_invalid_value_nulls_the_field(self):
        """裁决 C-04：errors 点名的字段一律置 null，合法值也不保留。"""
        requirement, warnings = finalize_requirement(candidate(
            errors=[{"type": "invalid_value", "field": "duration_minutes", "value": -10}],
        ))
        self.assertIsNone(requirement.duration_minutes)
        self.assertEqual(requirement.status, "invalid")
        self.assertTrue(any("C-04" in item for item in warnings))

    def test_multi_style_conflict(self):
        """裁决 C-02：多个合法书体并列 → style=null + conflict + conflicting_values。"""
        requirement, _ = finalize_requirement(candidate(
            style=None, status="conflict",
            follow_up="你提到多种书体，请确认本次先练哪一种？目前可以按楷书、行书或行楷来规划。",
            errors=[{"type": "conflicting_values", "field": "style", "value": "楷书和行书"}],
        ))
        self.assertIsNone(requirement.style)
        self.assertEqual(requirement.status, "conflict")
        self.assertEqual(requirement.errors[0].type, "conflicting_values")

    def test_exclusion_conflict_keeps_user_wish(self):
        """裁决 C-08b：书体与排除项重合，双方都是合法表达 → conflict 且 errors 为空。"""
        requirement, _ = finalize_requirement(candidate(
            exclusions=["楷书"], status="conflict", errors=[],
        ))
        self.assertEqual(requirement.style, "楷书")
        self.assertEqual(requirement.status, "conflict")
        self.assertEqual(requirement.errors, [])
        self.assertIn("排除", requirement.follow_up)

    def test_status_without_detail_is_repaired(self):
        requirement, _ = finalize_requirement(candidate(status="conflict"))
        self.assertEqual(requirement.status, "invalid")
        self.assertEqual(requirement.errors[0].type, "unresolved_conflict")

    def test_aliases_and_type_repairs(self):
        requirement, warnings = finalize_requirement(candidate(
            occupation="老师", style="楷体", duration_minutes="15",
        ))
        self.assertEqual(requirement.occupation, "教师")
        self.assertEqual(requirement.style, "楷书")
        self.assertEqual(requirement.duration_minutes, 15)
        self.assertTrue(any("字符串" in item for item in warnings))

    def test_exclusions_and_errors_are_cleaned(self):
        requirement, warnings = finalize_requirement(candidate(
            exclusions=["不要生僻字", "", 3],
            errors=[{"type": "x", "field": "style", "value": 1}, {"type": "x", "field": "style", "value": 1}, "bad"],
        ))
        self.assertEqual(requirement.exclusions, ["不要生僻字"])
        self.assertEqual(len(requirement.errors), 1)
        self.assertTrue(warnings)

    def test_complete_clears_follow_up(self):
        requirement, _ = finalize_requirement(candidate(follow_up="随便问一句"))
        self.assertIsNone(requirement.follow_up)


class ParseTextTests(unittest.TestCase):
    def test_parse_uses_client_and_records_metadata(self):
        client = FakeClient(json.dumps(candidate(), ensure_ascii=False))
        outcome = parse_text("我是老师，每天练15分钟，想练楷书。", client=client, settings=settings())
        self.assertIsInstance(outcome.requirement, UserRequirement)
        self.assertEqual(outcome.client, "fake")
        self.assertEqual(outcome.prompt_version, "v0")
        self.assertEqual(len(outcome.prompt_sha256), 12)
        self.assertEqual(outcome.usage, {"total_tokens": 12})
        self.assertFalse(outcome.usage_missing)
        self.assertIn("需求解析器", client.calls[0][0])
        self.assertEqual(client.calls[0][1], "我是老师，每天练15分钟，想练楷书。")

    def test_junk_output_raises_format_error(self):
        client = FakeClient("抱歉，我不明白。")
        with self.assertRaises(ParseFormatError):
            parse_text("随便", client=client, settings=settings())

    def test_missing_key_raises_config_error(self):
        with self.assertRaises(ParseConfigError):
            parse_text("我是老师，每天练15分钟，想练楷书。", settings=settings(api_key=None))

    def test_transport_errors_are_classified(self):
        client = DashScopeChatClient(settings())
        request_info = urllib.error.HTTPError(
            "https://example.com", 400, "Bad Request", {}, io.BytesIO(b'{"error":"bad param"}')
        )
        with patch("urllib.request.urlopen", side_effect=request_info):
            with self.assertRaises(ParseTransportError) as caught:
                parse_text("我是老师", client=client, settings=settings())
        self.assertEqual(caught.exception.status_code, 400)
        self.assertEqual(caught.exception.layer, "transport")

    def test_payload_contains_json_mode_without_secret(self):
        client = DashScopeChatClient(settings())
        payload = client.build_payload("SYS", "USER")
        self.assertEqual(payload["response_format"], {"type": "json_object"})
        self.assertEqual(payload["model"], "qwen-plus")
        self.assertEqual(payload["messages"][0]["role"], "system")
        self.assertNotIn("test-key", json.dumps(payload, ensure_ascii=False))


class MockBatchTests(unittest.TestCase):
    def test_mock_covers_all_samples_and_stays_out_of_planning(self):
        client = MockChatClient.from_file(DEFAULT_MOCK)
        samples = json.loads(DEFAULT_SAMPLES.read_text(encoding="utf-8"))
        self.assertEqual(len(samples), 10)
        statuses = set()
        for sample in samples:
            outcome = parse_text(sample["input"], client=client, settings=settings(api_key=None))
            statuses.add(outcome.requirement.status)
            self.assertIsInstance(outcome.requirement, UserRequirement)
            if outcome.requirement.status != "complete":
                with self.subTest(sample=sample["id"]), self.assertRaises(RequirementNotReadyError):
                    check_requirement_ready(outcome.requirement)
        # 裁决 C-01b 后 UR-08 由 conflict 改为缺时长追问，10 条里不再有 conflict 样本
        self.assertEqual(statuses, {"complete", "needs_clarification", "invalid"})

    def test_run_parse_writes_jsonl_and_matches(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "parse_runs.jsonl"
            with contextlib.redirect_stdout(io.StringIO()):
                code = run_parse_main([
                    "--client", "mock", "--samples", str(DEFAULT_SAMPLES), "--out", str(out), "--tag", "test",
                ])
            self.assertEqual(code, 0)
            records = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(records), 10)
            self.assertTrue(all(record["expectation_match"] for record in records))
            self.assertTrue(all(record["mock"] for record in records))
            self.assertTrue(all(record["prompt_version"] == "v1" for record in records))

    def test_run_parse_refuses_sealed_samples(self):
        with tempfile.TemporaryDirectory() as folder:
            folder_path = Path(folder)
            samples = folder_path / "samples.json"
            samples.write_text(json.dumps([{
                "id": "SEAL-01", "split": "封存", "input": "我是老师，每天练15分钟，想练楷书。",
                "expected": candidate(),
            }], ensure_ascii=False), encoding="utf-8")
            out = folder_path / "parse_runs.jsonl"
            with contextlib.redirect_stderr(io.StringIO()):
                code = run_parse_main([
                    "--client", "mock", "--samples", str(samples), "--out", str(out),
                ])
            self.assertEqual(code, 2)
            self.assertFalse(out.exists())


class EndpointTests(unittest.TestCase):
    """直接调用路由函数，不经过网络端口，也不需要 httpx。"""

    def test_endpoint_returns_requirement_and_version_headers(self):
        import main as app_module
        from fastapi import Response
        from parsing.parse_requirement import ParseOutcome

        requirement, _ = finalize_requirement(candidate())
        outcome = ParseOutcome(
            requirement=requirement, raw_text="{}", client="mock", model="mock-qwen",
            prompt_version="v0", prompt_sha256="0" * 12, temperature=None, latency_ms=1,
        )
        response = Response()
        with patch.object(app_module, "parse_text", return_value=outcome):
            returned = app_module.parse_requirement(response, app_module.ParseRequest(text="我是老师"))
        self.assertEqual(returned.status, "complete")
        self.assertEqual(response.headers["X-Moling-Prompt-Version"], "v0")
        self.assertEqual(response.headers["X-Moling-Client"], "mock")

    def test_endpoint_maps_missing_config_to_503(self):
        import main as app_module
        from fastapi import HTTPException, Response

        with patch.object(app_module, "parse_text", side_effect=ParseConfigError("缺少模型密钥", hint="配置 .env")):
            with self.assertRaises(HTTPException) as caught:
                app_module.parse_requirement(Response(), app_module.ParseRequest(text="我是老师"))
        self.assertEqual(caught.exception.status_code, 503)
        self.assertEqual(caught.exception.detail["code"], "PARSE_CONFIG_ERROR")

    def test_endpoint_maps_junk_output_to_422(self):
        import main as app_module
        from fastapi import HTTPException, Response

        with patch.object(app_module, "parse_text", side_effect=ParseFormatError("不是 JSON", missing_keys=["style"])):
            with self.assertRaises(HTTPException) as caught:
                app_module.parse_requirement(Response(), app_module.ParseRequest(text="我是老师"))
        self.assertEqual(caught.exception.status_code, 422)
        self.assertEqual(caught.exception.detail["code"], "PARSE_FORMAT_ERROR")
        self.assertEqual(caught.exception.detail["fields"][0].field, "style")


if __name__ == "__main__":
    unittest.main()
