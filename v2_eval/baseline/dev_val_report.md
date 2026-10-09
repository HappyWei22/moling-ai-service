# v2 需求解析评测报告

- 批次：`20261009T145849Z-v2-baseline`
- 样本 SHA256：`ca5f19a047af59e373fe53e8df8e69be705e26b39abdc326608c3dfd3482f967`
- 模型：`qwen3.8-flash`；提示词 SHA256：`97664f29304af5ccdd37653b455ec1bdc7cb98f59ce0206de2180ca83c3f3bce`
- 调用：`real`；代码提交：`e4387953f502463aa93b24c25c4a1add19841bc0`

> 本报告的 API 比较由解析结果构造，未发起 HTTP 请求；真实 HTTP 契约另由接口测试验证。
> 自动检查不等于追问语义验收；pending 项需人工检查 required/forbidden，并统计漏问、重复问、多余问。

> **样本哈希说明（2026-10-09 补记）**：本批次跑在 `ca5f19a0…` 版本上。
> 事后发现 `build_samples.py::forbidden_topics` 用 set 迭代生成 `forbidden` 清单，
> 受 Python 字符串哈希随机化影响，同一份声明在不同进程下产出的 `forbidden` 元素**顺序不同**，
> 导致样本文件 SHA 不稳定。已修复为固定字段顺序，修复后重建得到 `b1c1f82a…`。
>
> **该修复不影响本报告的任何数字**：`required`/`forbidden` 属人工语义要求，
> `parsing/eval_v2.py:143` 明确**不参与自动判分**。改动仅涉及 10 条样本 `forbidden` 数组中
> 两个元素的位置互换，语义完全等价（两者仍均为 forbidden）。样本内容、期望答案、
> 分集、覆盖均无变化。如需完全对齐，可用 `b1c1f82a…` 版本重跑，结果应逐条一致。

## dev

- 输入 63 条；语义组 56；独立会话 7。
- 自动检查全部一致：29/63（46.0%）
- 完整问题集合一致：50/63（79.4%）
- 错误放行率：0/44（0.0%）
- 模型错误召回率：28/41（68.3%）
- 模型错误精确率：28/30（93.3%）
- 技术失败：{}
- 端到端已确认成功：8/63（12.7%）；语义待复核 21 条（未复核不能作为最终成功率）。

| 字段 | 成功解析样本准确率 | 非空答案准确率 |
|---|---|---|
| occupation | 62/63（98.4%） | 45/46（97.8%） |
| scene | 51/63（81.0%） | 10/22（45.5%） |
| font | 63/63（100.0%） | 36/36（100.0%） |
| duration_minutes | 62/63（98.4%） | 32/32（100.0%） |
| status | 53/63（84.1%） | 53/63（84.1%） |

| 分桶 | 自动一致 / 全部（包含技术失败） |
|---|---|
| source:migrated | 7/12（58.3%） |
| source:new | 22/51（43.1%） |
| status:complete | 8/19（42.1%） |
| status:invalid | 4/26（15.4%） |
| status:needs_clarification | 17/18（94.4%） |
| tag:alias | 1/2（50.0%） |
| tag:boundary | 1/3（33.3%） |
| tag:chinese_number | 1/2（50.0%） |
| tag:colloquial | 1/2（50.0%） |
| tag:complete | 8/19（42.1%） |
| tag:conflict | 0/10（0.0%） |
| tag:conflict_duration | 0/3（0.0%） |
| tag:conflict_font | 0/8（0.0%） |
| tag:dispute | 1/2（50.0%） |
| tag:full | 3/4（75.0%） |
| tag:invalid | 3/17（17.6%） |
| tag:invalid_duration | 1/11（9.1%） |
| tag:invalid_font | 2/7（28.6%） |
| tag:missing | 16/17（94.1%） |
| tag:missing_all | 2/2（100.0%） |
| tag:missing_duration | 10/11（90.9%） |
| tag:missing_font | 7/8（87.5%） |
| tag:missing_personalization | 6/7（85.7%） |
| tag:multi_invalid | 0/1（0.0%） |
| tag:multi_issue | 5/21（23.8%） |
| tag:multi_missing | 3/6（50.0%） |
| tag:multi_turn | 7/14（50.0%） |
| tag:multi_value | 0/1（0.0%） |
| tag:needs_clarification | 2/2（100.0%） |
| tag:negation | 0/1（0.0%） |
| tag:no_inference | 4/5（80.0%） |
| tag:occupation_only | 1/2（50.0%） |
| tag:scene_only | 0/2（0.0%） |
| tag:short_list | 1/1（100.0%） |
| tag:unclear | 0/1（0.0%） |
| tag:variation | 2/5（40.0%） |

### 自动检查失败与语义复核清单

- `V2-D001`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D004`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D005`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D009`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D013`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D014`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D016`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D017`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D019`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D021`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D023`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D024`：`{"field_diff": ["duration_minutes", "status"], "missing_issues": [["invalid_value", "duration_minutes"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D025`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D027`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D028`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D030`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D031`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D033`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D034`：`{"field_diff": ["status"], "missing_issues": [["invalid_value", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D035`：`{"field_diff": ["status"], "missing_issues": [["invalid_value", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D036`：`{"field_diff": ["scene", "status"], "missing_issues": [["invalid_value", "duration_minutes"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D039`：`{"field_diff": [], "missing_issues": [["invalid_value", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D041`：`{"field_diff": ["scene", "status"], "missing_issues": [["conflicting_values", "font"], ["invalid_value", "font"]], "extra_issues": [["missing_field", "font"]], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D043`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D044`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D045`：`{"field_diff": ["scene"], "missing_issues": [["invalid_value", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D047`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D049`：`{"field_diff": ["status"], "missing_issues": [["invalid_value", "duration_minutes"], ["invalid_value", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D050`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D052`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D054`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D056`：`{"field_diff": [], "missing_issues": [], "extra_issues": [["conflicting_values", "font"]], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D058`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D060`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D061`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D062`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D063`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D064`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D065`：`{"field_diff": ["scene", "status"], "missing_issues": [["invalid_value", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D066`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D067`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D068`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D069`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D074`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D078`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D082`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D084`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D086`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D087`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D088`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D090`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D092`：`{"field_diff": ["status"], "missing_issues": [["invalid_value", "font"]], "extra_issues": [["missing_field", "font"]], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D094`：`{"field_diff": ["status"], "missing_issues": [["invalid_value", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D096`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D098`：`{"field_diff": ["occupation", "scene", "status"], "missing_issues": [], "extra_issues": [["conflicting_values", "occupation"]], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`

## val

- 输入 35 条；语义组 32；独立会话 3。
- 自动检查全部一致：18/35（51.4%）
- 完整问题集合一致：26/35（74.3%）
- 错误放行率：0/27（0.0%）
- 模型错误召回率：18/28（64.3%）
- 模型错误精确率：18/19（94.7%）
- 技术失败：{}
- 端到端已确认成功：5/35（14.3%）；语义待复核 13 条（未复核不能作为最终成功率）。

| 字段 | 成功解析样本准确率 | 非空答案准确率 |
|---|---|---|
| occupation | 35/35（100.0%） | 28/28（100.0%） |
| scene | 33/35（94.3%） | 19/21（90.5%） |
| font | 35/35（100.0%） | 17/17（100.0%） |
| duration_minutes | 35/35（100.0%） | 17/17（100.0%） |
| status | 29/35（82.9%） | 29/35（82.9%） |

| 分桶 | 自动一致 / 全部（包含技术失败） |
|---|---|
| source:migrated | 1/2（50.0%） |
| source:new | 17/33（51.5%） |
| status:complete | 5/8（62.5%） |
| status:invalid | 4/17（23.5%） |
| status:needs_clarification | 9/10（90.0%） |
| tag:alias | 0/1（0.0%） |
| tag:boundary | 0/2（0.0%） |
| tag:complete | 5/8（62.5%） |
| tag:conflict | 1/10（10.0%） |
| tag:conflict_duration | 1/5（20.0%） |
| tag:conflict_font | 0/5（0.0%） |
| tag:dispute | 0/2（0.0%） |
| tag:full | 2/2（100.0%） |
| tag:invalid | 4/9（44.4%） |
| tag:invalid_duration | 1/5（20.0%） |
| tag:invalid_font | 3/5（60.0%） |
| tag:missing | 7/9（77.8%） |
| tag:missing_all | 2/2（100.0%） |
| tag:missing_duration | 4/6（66.7%） |
| tag:missing_font | 5/6（83.3%） |
| tag:missing_personalization | 1/2（50.0%） |
| tag:multi_invalid | 0/1（0.0%） |
| tag:multi_issue | 4/13（30.8%） |
| tag:multi_missing | 2/4（50.0%） |
| tag:multi_turn | 5/6（83.3%） |
| tag:needs_clarification | 2/2（100.0%） |
| tag:negation | 0/1（0.0%） |
| tag:no_inference | 2/3（66.7%） |
| tag:no_inference_default | 0/1（0.0%） |
| tag:occupation_only | 0/1（0.0%） |
| tag:reordered | 1/1（100.0%） |
| tag:scene_only | 0/1（0.0%） |
| tag:unclear | 1/1（100.0%） |
| tag:variation | 1/3（33.3%） |

### 自动检查失败与语义复核清单

- `V2-V003`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-V006`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-V015`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V018`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V020`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V022`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V026`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V029`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V032`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V037`：`{"field_diff": ["status"], "missing_issues": [["conflicting_values", "duration_minutes"], ["invalid_value", "duration_minutes"]], "extra_issues": [["missing_field", "duration_minutes"]], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V038`：`{"field_diff": ["status"], "missing_issues": [["invalid_value", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V040`：`{"field_diff": [], "missing_issues": [["invalid_value", "duration_minutes"]], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V042`：`{"field_diff": [], "missing_issues": [["conflicting_values", "duration_minutes"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V046`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V048`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V051`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V053`：`{"field_diff": [], "missing_issues": [["invalid_value", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V055`：`{"field_diff": ["status"], "missing_issues": [["invalid_value", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V057`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V070`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V072`：`{"field_diff": ["status"], "missing_issues": [["invalid_value", "duration_minutes"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V076`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V077`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V083`：`{"field_diff": ["status"], "missing_issues": [["missing_field", "font"]], "extra_issues": [["invalid_value", "font"]], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V085`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-V089`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V091`：`{"field_diff": ["status"], "missing_issues": [["conflicting_values", "font"], ["invalid_value", "font"]], "extra_issues": [["missing_field", "font"]], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V093`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V095`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V097`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`

