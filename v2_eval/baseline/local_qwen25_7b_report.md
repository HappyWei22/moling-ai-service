# v2 需求解析评测报告

- 批次：`20261023T060422Z-local-qwen25-7b`
- 样本 SHA256：`b1c1f82a0bfe2a825ff2247948829b84a6d041ea5538281d70c0e2c37b1c99f7`
- 模型：`qwen2.5:7b-instruct-q4_k_m`；提示词 SHA256：`97664f29304af5ccdd37653b455ec1bdc7cb98f59ce0206de2180ca83c3f3bce`
- 调用：`real`；代码提交：`2b6ff9ba7fc4dcc038a5662d750e0eb6c64dd381`

> 本报告的 API 比较由解析结果构造，未发起 HTTP 请求；真实 HTTP 契约另由接口测试验证。
> 自动检查不等于追问语义验收；pending 项需人工检查 required/forbidden，并统计漏问、重复问、多余问。

## dev

- 输入 63 条；语义组 56；独立会话 7。
- 自动检查全部一致：17/63（27.0%）
- 完整问题集合一致：50/63（79.4%）
- 错误放行率：4/44（9.1%）
- 模型错误召回率：13/41（31.7%）
- 模型错误精确率：13/14（92.9%）
- 技术失败：{}
- 端到端已确认成功：8/63（12.7%）；语义待复核 9 条（未复核不能作为最终成功率）。

| 字段 | 成功解析样本准确率 | 非空答案准确率 |
|---|---|---|
| occupation | 62/63（98.4%） | 45/46（97.8%） |
| scene | 44/63（69.8%） | 3/22（13.6%） |
| font | 59/63（93.7%） | 36/36（100.0%） |
| duration_minutes | 61/63（96.8%） | 32/32（100.0%） |
| status | 56/63（88.9%） | 56/63（88.9%） |

| 分桶 | 自动一致 / 全部（包含技术失败） |
|---|---|
| source:migrated | 4/12（33.3%） |
| source:new | 13/51（25.5%） |
| status:complete | 8/19（42.1%） |
| status:invalid | 0/26（0.0%） |
| status:needs_clarification | 9/18（50.0%） |
| tag:alias | 0/2（0.0%） |
| tag:boundary | 0/3（0.0%） |
| tag:chinese_number | 1/2（50.0%） |
| tag:colloquial | 1/2（50.0%） |
| tag:complete | 8/19（42.1%） |
| tag:conflict | 0/10（0.0%） |
| tag:conflict_duration | 0/3（0.0%） |
| tag:conflict_font | 0/8（0.0%） |
| tag:dispute | 0/2（0.0%） |
| tag:full | 0/4（0.0%） |
| tag:invalid | 0/17（0.0%） |
| tag:invalid_duration | 0/11（0.0%） |
| tag:invalid_font | 0/7（0.0%） |
| tag:missing | 8/17（47.1%） |
| tag:missing_all | 2/2（100.0%） |
| tag:missing_duration | 7/11（63.6%） |
| tag:missing_font | 3/8（37.5%） |
| tag:missing_personalization | 1/7（14.3%） |
| tag:multi_invalid | 0/1（0.0%） |
| tag:multi_issue | 1/21（4.8%） |
| tag:multi_missing | 1/6（16.7%） |
| tag:multi_turn | 6/14（42.9%） |
| tag:multi_value | 0/1（0.0%） |
| tag:needs_clarification | 1/2（50.0%） |
| tag:negation | 0/1（0.0%） |
| tag:no_inference | 2/5（40.0%） |
| tag:occupation_only | 2/2（100.0%） |
| tag:scene_only | 1/2（50.0%） |
| tag:short_list | 1/1（100.0%） |
| tag:unclear | 0/1（0.0%） |
| tag:variation | 2/5（40.0%） |

### 自动检查失败与语义复核清单

- `V2-D005`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D007`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D008`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D009`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D011`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D013`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D014`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D016`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D017`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D019`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D021`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D023`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D024`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D025`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D027`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D028`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D030`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D031`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D033`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D034`：`{"field_diff": [], "missing_issues": [["conflicting_values", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D035`：`{"field_diff": [], "missing_issues": [["conflicting_values", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D036`：`{"field_diff": ["scene", "status"], "missing_issues": [["invalid_value", "duration_minutes"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D039`：`{"field_diff": [], "missing_issues": [["conflicting_values", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D041`：`{"field_diff": ["scene", "font", "status"], "missing_issues": [["conflicting_values", "font"], ["invalid_value", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D043`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D044`：`{"field_diff": [], "missing_issues": [], "extra_issues": [["conflicting_values", "duration_minutes"]], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D045`：`{"field_diff": ["scene", "font", "duration_minutes", "status"], "missing_issues": [["conflicting_values", "font"], ["invalid_value", "duration_minutes"], ["invalid_value", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D047`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D049`：`{"field_diff": [], "missing_issues": [["conflicting_values", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D050`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D052`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D054`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D056`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D058`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D060`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D061`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D063`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D065`：`{"field_diff": ["scene"], "missing_issues": [["conflicting_values", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D066`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D067`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D068`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D069`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D074`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D075`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D078`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D082`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D084`：`{"field_diff": ["font", "status"], "missing_issues": [["invalid_value", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D086`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D087`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D088`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D090`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D092`：`{"field_diff": ["font", "status"], "missing_issues": [["invalid_value", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D094`：`{"field_diff": ["status"], "missing_issues": [["invalid_value", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D096`：`{"field_diff": ["duration_minutes", "status"], "missing_issues": [["invalid_value", "duration_minutes"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D098`：`{"field_diff": ["occupation", "scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`

## val

- 输入 35 条；语义组 32；独立会话 3。
- 自动检查全部一致：5/35（14.3%）
- 完整问题集合一致：23/35（65.7%）
- 错误放行率：1/27（3.7%）
- 模型错误召回率：8/28（28.6%）
- 模型错误精确率：8/9（88.9%）
- 技术失败：{}
- 端到端已确认成功：1/35（2.9%）；语义待复核 4 条（未复核不能作为最终成功率）。

| 字段 | 成功解析样本准确率 | 非空答案准确率 |
|---|---|---|
| occupation | 34/35（97.1%） | 27/28（96.4%） |
| scene | 14/35（40.0%） | 0/21（0.0%） |
| font | 31/35（88.6%） | 16/17（94.1%） |
| duration_minutes | 35/35（100.0%） | 17/17（100.0%） |
| status | 27/35（77.1%） | 27/35（77.1%） |

| 分桶 | 自动一致 / 全部（包含技术失败） |
|---|---|
| source:migrated | 1/2（50.0%） |
| source:new | 4/33（12.1%） |
| status:complete | 1/8（12.5%） |
| status:invalid | 0/17（0.0%） |
| status:needs_clarification | 4/10（40.0%） |
| tag:alias | 0/1（0.0%） |
| tag:boundary | 0/2（0.0%） |
| tag:complete | 1/8（12.5%） |
| tag:conflict | 0/10（0.0%） |
| tag:conflict_duration | 0/5（0.0%） |
| tag:conflict_font | 0/5（0.0%） |
| tag:dispute | 0/2（0.0%） |
| tag:full | 0/2（0.0%） |
| tag:invalid | 0/9（0.0%） |
| tag:invalid_duration | 0/5（0.0%） |
| tag:invalid_font | 0/5（0.0%） |
| tag:missing | 3/9（33.3%） |
| tag:missing_all | 2/2（100.0%） |
| tag:missing_duration | 1/6（16.7%） |
| tag:missing_font | 1/6（16.7%） |
| tag:missing_personalization | 1/2（50.0%） |
| tag:multi_invalid | 0/1（0.0%） |
| tag:multi_issue | 1/13（7.7%） |
| tag:multi_missing | 1/4（25.0%） |
| tag:multi_turn | 0/6（0.0%） |
| tag:needs_clarification | 1/2（50.0%） |
| tag:negation | 0/1（0.0%） |
| tag:no_inference | 1/3（33.3%） |
| tag:no_inference_default | 0/1（0.0%） |
| tag:occupation_only | 1/1（100.0%） |
| tag:reordered | 0/1（0.0%） |
| tag:scene_only | 0/1（0.0%） |
| tag:unclear | 0/1（0.0%） |
| tag:variation | 0/3（0.0%） |

### 自动检查失败与语义复核清单

- `V2-V006`：`{"field_diff": ["scene", "status"], "missing_issues": [], "extra_issues": [["missing_field", "personalization"]], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V010`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-V012`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-V015`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V018`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V020`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V022`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V026`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V029`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V032`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V037`：`{"field_diff": ["status"], "missing_issues": [["invalid_value", "duration_minutes"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V038`：`{"field_diff": ["scene", "font", "status"], "missing_issues": [["conflicting_values", "font"], ["invalid_value", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V040`：`{"field_diff": [], "missing_issues": [["invalid_value", "duration_minutes"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V042`：`{"field_diff": ["scene", "status"], "missing_issues": [["invalid_value", "duration_minutes"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V046`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V048`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [["conflicting_values", "requirement"]], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V051`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V053`：`{"field_diff": [], "missing_issues": [["conflicting_values", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V055`：`{"field_diff": ["scene", "font", "status"], "missing_issues": [["conflicting_values", "font"], ["invalid_value", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V057`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V070`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V071`：`{"field_diff": ["scene", "font", "status"], "missing_issues": [], "extra_issues": [["invalid_value", "font"]], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V072`：`{"field_diff": ["scene"], "missing_issues": [["conflicting_values", "duration_minutes"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V073`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-V076`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V077`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V081`：`{"field_diff": ["occupation", "scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-V083`：`{"field_diff": ["font", "status"], "missing_issues": [["missing_field", "font"]], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V085`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-V089`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V091`：`{"field_diff": ["status"], "missing_issues": [["conflicting_values", "font"], ["invalid_value", "font"]], "extra_issues": [["missing_field", "font"]], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V093`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V095`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V097`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`

