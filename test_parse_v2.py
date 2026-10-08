"""新追问协议的离线契约测试。"""

import json
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
        self.assertEqual(response.message, "你想练哪种书体？")

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
