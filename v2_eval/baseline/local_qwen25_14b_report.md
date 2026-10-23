# v2 需求解析评测报告

- 批次：`20261023T070709Z-local-qwen25-14b`
- 样本 SHA256：`b1c1f82a0bfe2a825ff2247948829b84a6d041ea5538281d70c0e2c37b1c99f7`
- 模型：`qwen2.5:14b-instruct-q4_k_m`；提示词 SHA256：`97664f29304af5ccdd37653b455ec1bdc7cb98f59ce0206de2180ca83c3f3bce`
- 调用：`real`；代码提交：`2b6ff9ba7fc4dcc038a5662d750e0eb6c64dd381`

> 本报告的 API 比较由解析结果构造，未发起 HTTP 请求；真实 HTTP 契约另由接口测试验证。
> 自动检查不等于追问语义验收；pending 项需人工检查 required/forbidden，并统计漏问、重复问、多余问。

## dev

- 输入 63 条；语义组 56；独立会话 7。
- 自动检查全部一致：29/63（46.0%）
- 完整问题集合一致：50/63（79.4%）
- 错误放行率：0/44（0.0%）
- 模型错误召回率：27/41（65.9%）
- 模型错误精确率：27/31（87.1%）
- 技术失败：{}
- 端到端已确认成功：10/63（15.9%）；语义待复核 19 条（未复核不能作为最终成功率）。

| 字段 | 成功解析样本准确率 | 非空答案准确率 |
|---|---|---|
| occupation | 62/63（98.4%） | 45/46（97.8%） |
| scene | 54/63（85.7%） | 13/22（59.1%） |
| font | 61/63（96.8%） | 34/36（94.4%） |
| duration_minutes | 61/63（96.8%） | 31/32（96.9%） |
| status | 56/63（88.9%） | 56/63（88.9%） |

| 分桶 | 自动一致 / 全部（包含技术失败） |
|---|---|
| source:migrated | 6/12（50.0%） |
| source:new | 23/51（45.1%） |
| status:complete | 10/19（52.6%） |
| status:invalid | 3/26（11.5%） |
| status:needs_clarification | 16/18（88.9%） |
| tag:alias | 1/2（50.0%） |
| tag:boundary | 1/3（33.3%） |
| tag:chinese_number | 1/2（50.0%） |
| tag:colloquial | 1/2（50.0%） |
| tag:complete | 10/19（52.6%） |
| tag:conflict | 0/10（0.0%） |
| tag:conflict_duration | 0/3（0.0%） |
| tag:conflict_font | 0/8（0.0%） |
| tag:dispute | 1/2（50.0%） |
| tag:full | 2/4（50.0%） |
| tag:invalid | 2/17（11.8%） |
| tag:invalid_duration | 0/11（0.0%） |
| tag:invalid_font | 2/7（28.6%） |
| tag:missing | 15/17（88.2%） |
| tag:missing_all | 2/2（100.0%） |
| tag:missing_duration | 10/11（90.9%） |
| tag:missing_font | 6/8（75.0%） |
| tag:missing_personalization | 6/7（85.7%） |
| tag:multi_invalid | 0/1（0.0%） |
| tag:multi_issue | 4/21（19.0%） |
| tag:multi_missing | 3/6（50.0%） |
| tag:multi_turn | 8/14（57.1%） |
| tag:multi_value | 0/1（0.0%） |
| tag:needs_clarification | 2/2（100.0%） |
| tag:negation | 0/1（0.0%） |
| tag:no_inference | 4/5（80.0%） |
| tag:occupation_only | 1/2（50.0%） |
| tag:scene_only | 2/2（100.0%） |
| tag:short_list | 1/1（100.0%） |
| tag:unclear | 0/1（0.0%） |
| tag:variation | 2/5（40.0%） |

### 自动检查失败与语义复核清单

- `V2-D001`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D008`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D009`：`{"field_diff": ["scene", "font", "status"], "missing_issues": [], "extra_issues": [["invalid_value", "font"]], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D013`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D014`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D016`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D017`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D019`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D021`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D023`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D024`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D025`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D027`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D028`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D030`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D031`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D033`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D034`：`{"field_diff": [], "missing_issues": [["conflicting_values", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D035`：`{"field_diff": [], "missing_issues": [["conflicting_values", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D036`：`{"field_diff": ["status"], "missing_issues": [["invalid_value", "duration_minutes"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D039`：`{"field_diff": [], "missing_issues": [["conflicting_values", "font"], ["invalid_value", "font"]], "extra_issues": [["missing_field", "font"]], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D041`：`{"field_diff": ["scene", "status"], "missing_issues": [["invalid_value", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D043`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D044`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D045`：`{"field_diff": ["duration_minutes"], "missing_issues": [["conflicting_values", "font"], ["invalid_value", "duration_minutes"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D047`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D049`：`{"field_diff": [], "missing_issues": [["conflicting_values", "duration_minutes"], ["conflicting_values", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D050`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D052`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D054`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D056`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D058`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D060`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D062`：`{"field_diff": ["font", "status"], "missing_issues": [], "extra_issues": [["conflicting_values", "font"]], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D063`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D064`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D065`：`{"field_diff": [], "missing_issues": [["conflicting_values", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D067`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D068`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D069`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D074`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D075`：`{"field_diff": ["scene", "duration_minutes", "status"], "missing_issues": [], "extra_issues": [["conflicting_values", "duration_minutes"]], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D078`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D082`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D084`：`{"field_diff": ["status"], "missing_issues": [["invalid_value", "font"]], "extra_issues": [["conflicting_values", "font"]], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D086`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D087`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D088`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D090`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D092`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D094`：`{"field_diff": ["status"], "missing_issues": [["invalid_value", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D096`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D098`：`{"field_diff": ["occupation"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`

## val

- 输入 35 条；语义组 32；独立会话 3。
- 自动检查全部一致：7/35（20.0%）
- 完整问题集合一致：22/35（62.9%）
- 错误放行率：0/27（0.0%）
- 模型错误召回率：19/28（67.9%）
- 模型错误精确率：19/24（79.2%）
- 技术失败：{}
- 端到端已确认成功：2/35（5.7%）；语义待复核 5 条（未复核不能作为最终成功率）。

| 字段 | 成功解析样本准确率 | 非空答案准确率 |
|---|---|---|
| occupation | 35/35（100.0%） | 28/28（100.0%） |
| scene | 20/35（57.1%） | 6/21（28.6%） |
| font | 33/35（94.3%） | 15/17（88.2%） |
| duration_minutes | 34/35（97.1%） | 16/17（94.1%） |
| status | 26/35（74.3%） | 26/35（74.3%） |

| 分桶 | 自动一致 / 全部（包含技术失败） |
|---|---|
| source:migrated | 1/2（50.0%） |
| source:new | 6/33（18.2%） |
| status:complete | 2/8（25.0%） |
| status:invalid | 0/17（0.0%） |
| status:needs_clarification | 5/10（50.0%） |
| tag:alias | 0/1（0.0%） |
| tag:boundary | 0/2（0.0%） |
| tag:complete | 2/8（25.0%） |
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
| tag:missing_duration | 2/6（33.3%） |
| tag:missing_font | 2/6（33.3%） |
| tag:missing_personalization | 1/2（50.0%） |
| tag:multi_invalid | 0/1（0.0%） |
| tag:multi_issue | 2/13（15.4%） |
| tag:multi_missing | 2/4（50.0%） |
| tag:multi_turn | 0/6（0.0%） |
| tag:needs_clarification | 2/2（100.0%） |
| tag:negation | 0/1（0.0%） |
| tag:no_inference | 1/3（33.3%） |
| tag:no_inference_default | 0/1（0.0%） |
| tag:occupation_only | 1/1（100.0%） |
| tag:reordered | 1/1（100.0%） |
| tag:scene_only | 0/1（0.0%） |
| tag:unclear | 0/1（0.0%） |
| tag:variation | 1/3（33.3%） |

### 自动检查失败与语义复核清单

- `V2-V006`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-V010`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-V012`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-V015`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V018`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V020`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V022`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V026`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V029`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V032`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V037`：`{"field_diff": ["status"], "missing_issues": [["invalid_value", "duration_minutes"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V038`：`{"field_diff": ["scene"], "missing_issues": [["conflicting_values", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V040`：`{"field_diff": [], "missing_issues": [["invalid_value", "duration_minutes"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V042`：`{"field_diff": ["scene", "status"], "missing_issues": [["invalid_value", "duration_minutes"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V046`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V048`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V051`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V053`：`{"field_diff": [], "missing_issues": [["conflicting_values", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V055`：`{"field_diff": ["scene"], "missing_issues": [["conflicting_values", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V057`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V070`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V071`：`{"field_diff": ["scene", "font", "status"], "missing_issues": [], "extra_issues": [["invalid_value", "font"]], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V072`：`{"field_diff": ["status"], "missing_issues": [["invalid_value", "duration_minutes"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V073`：`{"field_diff": ["duration_minutes", "status"], "missing_issues": [], "extra_issues": [["conflicting_values", "duration_minutes"]], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V076`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V077`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V083`：`{"field_diff": ["status"], "missing_issues": [["missing_field", "font"]], "extra_issues": [["invalid_value", "font"]], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V085`：`{"field_diff": ["scene", "font", "status"], "missing_issues": [], "extra_issues": [["invalid_value", "font"]], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V089`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V091`：`{"field_diff": ["status"], "missing_issues": [["invalid_value", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V093`：`{"field_diff": ["status"], "missing_issues": [["missing_field", "duration_minutes"]], "extra_issues": [["invalid_value", "duration_minutes"]], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V095`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V097`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`

