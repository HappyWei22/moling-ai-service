"""新追问协议的离线契约测试。"""

import json
import io
from contextlib import redirect_stdout, redirect_stderr
import unittest
from unittest.mock import patch

from fastapi import Response

import main
from ai_service import generate_plan_v2
from parsing.config import Settings
from parsing.llm_client import LLMResponse
from parsing.parse_requirement_v2 import finalize_v2, parse_text_v2


class FakeClient:
    name = "fake"

    def __init__(self, answer):
        self.answer = answer
        self.input = None

    def complete(self, prompt, user_text):
        self.input = user_text
        return LLMResponse(text=json.dumps(self.answer, ensure_ascii=False), model="fake", usage=None)


def settings():
    return Settings(
        base_url="https://example.com", model="fake", api_key=None,
        timeout_seconds=1, temperature=0, extra_body={}, prompt_version="v2",
    )


class V2Tests(unittest.TestCase):
    def test_complete_and_plan_mapping(self):
        answer = {"occupation": "学生", "scene": "作业", "font": "楷书",
                  "duration_minutes": 15, "status": "complete", "follow_up": None, "errors": []}
        client = FakeClient(answer)
        outcome = parse_text_v2("我是学生。后来补充：作业用，楷书，每次15分钟。",
                                client=client, settings=settings())
        self.assertEqual(client.input, "我是学生。后来补充：作业用，楷书，每次15分钟。")
        self.assertEqual(outcome.requirement.font, "楷书")
        self.assertEqual(outcome.requirement.status, "complete")
        self.assertEqual(set(outcome.requirement.model_dump()),
                         {"occupation", "scene", "font", "duration_minutes", "status"})
        plan = generate_plan_v2(outcome.requirement)
        self.assertEqual(plan.style, "楷书")
        self.assertEqual(plan.duration_minutes, 15)

    def test_missing_information_requires_user_answer(self):
        result, message = finalize_v2({"occupation": "学生", "font": "楷书",
                                       "duration_minutes": None, "status": "complete"})
        self.assertEqual(result.status, "needs_clarification")
        self.assertIn("几分钟", message)

    def test_unsupported_values_do_not_complete(self):
        for answer in [
            {"occupation": "学生", "font": "草书", "duration_minutes": 15, "status": "complete"},
            {"occupation": "学生", "font": "楷书", "duration_minutes": 20, "status": "complete"},
        ]:
            with self.subTest(answer=answer):
                result, _ = finalize_v2(answer)
                self.assertEqual(result.status, "invalid")

    def test_missing_and_invalid_are_both_reported(self):
        result, message = finalize_v2({
            "font": None, "duration_minutes": None, "status": "invalid",
            "errors": [{"type": "invalid_value", "field": "duration_minutes", "value": -10}],
            "follow_up": "只修改时长即可。",
        })
        self.assertEqual(result.status, "invalid")
        self.assertIsNone(result.duration_minutes)
        self.assertIn("哪种书体", message)
        self.assertIn("-10", message)
        self.assertIn("职业", message)
        self.assertNotIn("几分钟", message)
        self.assertNotIn("只修改", message)

    def test_all_missing_is_not_invalid(self):
        result, message = finalize_v2({"status": "complete", "errors": []})
        self.assertEqual(result.status, "needs_clarification")
        for text in ("哪种书体", "几分钟", "职业"):
            self.assertIn(text, message)
        self.assertEqual(message.count("职业"), 1)

    def test_conflict_invalid_and_missing_reported_together(self):
        result, message = finalize_v2({
            "font": None, "duration_minutes": -10, "status": "conflict",
            "errors": [{"type": "conflicting_values", "field": "font", "value": ["楷书", "行书"]}],
        })
        self.assertEqual(result.status, "invalid")
        for text in ("书体存在冲突", "-10", "职业"):
            self.assertIn(text, message)
        self.assertNotIn("哪种书体", message)

    def test_conflict_does_not_turn_valid_duration_into_invalid(self):
        result, message = finalize_v2({
            "occupation": "学生", "font": "楷书", "duration_minutes": 15,
            "errors": [{"type": "conflicting_values", "field": "duration_minutes", "value": [5, 15]}],
        })
        self.assertEqual(result.status, "conflict")
        self.assertIsNone(result.duration_minutes)
        self.assertIn("练习时长存在冲突", message)
        self.assertNotIn("不符合要求", message)

    def test_local_validation_and_model_errors_are_deduplicated(self):
        result, message = finalize_v2({
            "occupation": "学生", "font": "草书", "duration_minutes": 20,
            "errors": [{"type": "invalid_value", "field": "font", "value": "草书"}] * 2,
        })
        self.assertEqual(result.status, "invalid")
        self.assertIsNone(result.font)
        self.assertIsNone(result.duration_minutes)
        self.assertEqual(message.count("书体不在支持范围内"), 1)
        self.assertIn("20", message)

    def test_occupation_or_scene_is_sufficient(self):
        for field in ("occupation", "scene"):
            result, message = finalize_v2({field: "学习", "font": "楷体", "duration_minutes": "15"})
            self.assertEqual(result.status, "complete")
            self.assertEqual(message, "ok")

    def test_cli_defaults_to_v2_and_reports_all_problems(self):
        import try_parse

        outcome = parse_text_v2("每天练-10分钟", client=FakeClient({
            "duration_minutes": -10, "font": None, "occupation": None, "scene": None,
        }), settings=settings())
        output = io.StringIO()
        diagnostics = io.StringIO()
        with patch.object(try_parse, "parse_text_v2", return_value=outcome) as parse, \
                redirect_stdout(output), redirect_stderr(diagnostics):
            self.assertEqual(try_parse.main(["每天练-10分钟"]), 0)
        parse.assert_called_once_with("每天练-10分钟", client=None)
        response = json.loads(output.getvalue())
        self.assertEqual(response["code"], 400)
        self.assertIsNone(response["data"])
        for text in ("书体", "-10", "职业"):
            self.assertIn(text, response["message"])
        self.assertIn("提示词 v2", diagnostics.getvalue())

    def test_cli_mock_supports_v2_and_legacy_v1(self):
        import try_parse

        for version in ("v1", "v2"):
            output = io.StringIO()
            with redirect_stdout(output), redirect_stderr(io.StringIO()):
                code = try_parse.main(["--version", version, "--mock", "我是学生，每天练-10分钟，想练楷书。"])
            self.assertEqual(code, 0)
            response = json.loads(output.getvalue())
            if version == "v2":
                self.assertEqual(response["code"], 400)
                self.assertIn("-10", response["message"])
            else:
                self.assertEqual(response["status"], "invalid")
                self.assertIn("follow_up", response)

    def test_endpoint_wraps_follow_up(self):
        outcome = parse_text_v2("我是学生", client=FakeClient({
            "occupation": "学生", "scene": None, "font": None,
            "duration_minutes": None, "status": "needs_clarification",
            "follow_up": "你想练哪种书体？", "errors": [],
        }), settings=settings())
        with patch.object(main, "parse_text_v2", return_value=outcome):
            response = main.parse_requirement_v2(Response(), main.ParseRequest(text="我是学生"))
        self.assertEqual(response.code, 400)
        self.assertIsNone(response.data)
        self.assertIn("哪种书体", response.message)
        self.assertIn("几分钟", response.message)

    def test_endpoint_returns_complete_data_and_plan(self):
        outcome = parse_text_v2("学生，作业，楷书，15分钟", client=FakeClient({
            "occupation": "学生", "scene": "作业", "font": "楷书",
            "duration_minutes": 15, "status": "complete", "follow_up": None, "errors": [],
        }), settings=settings())
        with patch.object(main, "parse_text_v2", return_value=outcome):
            response = main.parse_requirement_v2(Response(), main.ParseRequest(text="学生，作业，楷书，15分钟"))
        self.assertEqual(response.code, 0)
        self.assertEqual(response.data.font, "楷书")
        self.assertEqual(main.create_plan_v2(response.data).style, "楷书")


if __name__ == "__main__":
    unittest.main()
