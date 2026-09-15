import copy
import json
import unittest
from pathlib import Path
from unittest.mock import Mock
from pydantic import ValidationError
from schemas import UserRequirement, WorksheetPlan
from ai_service import generate_plan
from plan_generators import mock_generate
from requirement_rules import RequirementNotReadyError


def requirement(**changes):
    data = dict(occupation='教师', scene=None, style='楷书', duration_minutes=15,
                goal=None, exclusions=[], status='complete', follow_up=None, errors=[])
    data.update(changes)
    return UserRequirement(**data)


class PlanTests(unittest.TestCase):
    def test_replaceable_generator(self):
        req = requirement()
        raw = mock_generate(req)
        raw['plan_name'] = '替换生成器样例'
        raw['items'][0]['text'] = '板书'
        generator = Mock(return_value=raw)
        plan = generate_plan(req, generator=generator)
        generator.assert_called_once_with(req)
        self.assertIsInstance(plan, WorksheetPlan)
        self.assertEqual(plan.plan_name, '替换生成器样例')
        self.assertEqual(plan.items[0].text, '板书')

    def test_invalid_generator_output(self):
        for changes in [dict(items=[]), dict(schema_version='0.2')]:
            with self.subTest(changes=changes):
                generator = Mock(return_value=mock_generate(requirement()) | changes)
                with self.assertRaises(ValidationError):
                    generate_plan(requirement(), generator=generator)

    def test_generator_cannot_change_constraints(self):
        for changes in [dict(style='行书'), dict(duration_minutes=5)]:
            with self.subTest(changes=changes):
                raw = mock_generate(requirement(**changes))
                with self.assertRaisesRegex(ValueError, '书体和时长'):
                    generate_plan(requirement(), generator=Mock(return_value=raw))

    def test_unready_requirement_does_not_call_generator(self):
        generator = Mock()
        with self.assertRaises(RequirementNotReadyError):
            generate_plan(requirement(status='needs_clarification'), generator=generator)
        generator.assert_not_called()

    def test_generator_failure_propagates(self):
        with self.assertRaises(TimeoutError):
            generate_plan(requirement(), generator=Mock(side_effect=TimeoutError('超时')))

    def test_budgets_styles_and_ids(self):
        for duration, count in [(5, 12), (15, 36), (30, 72)]:
            for style in ['楷书', '行书', '行楷']:
                with self.subTest(duration=duration, style=style):
                    plan = generate_plan(requirement(duration_minutes=duration, style=style))
                    self.assertEqual(plan.style, style)
                    self.assertEqual(plan.duration_minutes, duration)
                    self.assertEqual(sum(len(i.text)*i.repeat for i in plan.items), count)
                    self.assertTrue(plan.is_mock)
                    self.assertTrue(all(i.task_type == '临摹' for i in plan.items))
        self.assertNotEqual(generate_plan(requirement()).plan_id, generate_plan(requirement()).plan_id)

    def test_optional_personalization(self):
        for changes in [dict(occupation=None, scene='板书'), dict(occupation=None, goal='工整')]:
            generate_plan(requirement(**changes))

    def test_unsupported_inputs(self):
        for changes in [dict(duration_minutes=20), dict(exclusions=['不要生僻字'])]:
            with self.subTest(changes=changes), self.assertRaises(RequirementNotReadyError):
                generate_plan(requirement(**changes))

    def test_invalid_outputs(self):
        original = generate_plan(requirement()).model_dump()
        for field, value in [('text', ''), ('text', '重点、例题'), ('repeat', -1),
                             ('repeat', '9'), ('task_type', '描红'), ('evaluation', '通过')]:
            data = copy.deepcopy(original)
            data['items'][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValidationError):
                WorksheetPlan.model_validate(data)
        for change in [dict(items=[]), dict(duration_minutes=20), dict(duration_minutes=5)]:
            with self.subTest(change=change), self.assertRaises(ValidationError):
                WorksheetPlan.model_validate(original | change)

    def test_saved_samples_and_schema(self):
        folder = Path(__file__).parent / 'WorkSheetPlan'
        for sample in json.loads((folder/'plans.json').read_text()):
            self.assertTrue(WorksheetPlan.model_validate(sample).is_mock)
        self.assertEqual(json.loads((folder/'worksheet_plan.schema.json').read_text()), WorksheetPlan.model_json_schema())


if __name__ == '__main__':
    unittest.main()
