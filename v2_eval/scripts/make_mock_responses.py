"""从样本生成 mock 模型响应文件，用于不依赖密钥的流程自检。

mock 响应代表**模型原始六字段输出**，由样本的期望反推，因此 mock 批次会全绿；
它证明的是「评测流程与契约自洽」，不是模型效果。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))

from parsing.parse_requirement_v2 import FONT_ALIASES  # noqa: E402

SAMPLES = ROOT / "v2_eval" / "samples_v2.jsonl"
OUT = ROOT / "v2_eval" / "baseline" / "mock_responses_v2.json"


def model_candidate(sample: dict) -> dict:
    """还原模型原始六字段输出。

    注意 _collect_errors 的实现细节：当 font/duration 的候选原值不在支持集合内时，
    本地会**额外**补一条 invalid_value（与模型报的 conflicting_values 并存）。
    因此 mock 必须按真实候选构造，而不是简单回填标准答案。
    """
    expected = sample["expected_requirement"]
    font = expected["font"]
    duration = expected["duration_minutes"]
    errors = [dict(i) for i in sample["expected_model_errors"]]
    for item in errors:
        if item["field"] == "font":
            font = item["value"]
        elif item["field"] == "duration_minutes":
            duration = item["value"]
    return {
        "occupation": expected["occupation"],
        "scene": expected["scene"],
        "font": font,
        "duration_minutes": duration,
        "status": expected["status"],
        "errors": errors,
    }


def main() -> int:
    samples = [json.loads(l) for l in SAMPLES.read_text(encoding="utf-8").splitlines() if l.strip()]
    responses = {}
    for sample in samples:
        responses[sample["input"]] = json.dumps(model_candidate(sample), ensure_ascii=False)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"responses": responses}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"写出 {len(responses)} 条 mock 响应 → {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
