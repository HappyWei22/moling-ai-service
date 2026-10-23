# v2 需求解析评测报告

- 批次：`20261023T061234Z-local-qwen25-7b-scenePrompt`
- 样本 SHA256：`b1c1f82a0bfe2a825ff2247948829b84a6d041ea5538281d70c0e2c37b1c99f7`
- 模型：`qwen2.5:7b-instruct-q4_k_m`；提示词 SHA256：`e76672e213dbe88a0662cddf4822f0b278ba28d97d0b60d73670c50903b2b495`
- 调用：`real`；代码提交：`2b6ff9ba7fc4dcc038a5662d750e0eb6c64dd381`

> 本报告的 API 比较由解析结果构造，未发起 HTTP 请求；真实 HTTP 契约另由接口测试验证。
> 自动检查不等于追问语义验收；pending 项需人工检查 required/forbidden，并统计漏问、重复问、多余问。

## dev

- 输入 63 条；语义组 56；独立会话 7。
- 自动检查全部一致：22/63（34.9%）
- 完整问题集合一致：50/63（79.4%）
- 错误放行率：3/44（6.8%）
- 模型错误召回率：12/41（29.3%）
- 模型错误精确率：12/13（92.3%）
- 技术失败：{}
- 端到端已确认成功：10/63（15.9%）；语义待复核 12 条（未复核不能作为最终成功率）。

| 字段 | 成功解析样本准确率 | 非空答案准确率 |
|---|---|---|
| occupation | 62/63（98.4%） | 45/46（97.8%） |
| scene | 52/63（82.5%） | 11/22（50.0%） |
| font | 61/63（96.8%） | 36/36（100.0%） |
| duration_minutes | 60/63（95.2%） | 32/32（100.0%） |
| status | 57/63（90.5%） | 57/63（90.5%） |

| 分桶 | 自动一致 / 全部（包含技术失败） |
|---|---|
| source:migrated | 5/12（41.7%） |
| source:new | 17/51（33.3%） |
| status:complete | 10/19（52.6%） |
| status:invalid | 2/26（7.7%） |
| status:needs_clarification | 10/18（55.6%） |
| tag:alias | 1/2（50.0%） |
| tag:boundary | 0/3（0.0%） |
| tag:chinese_number | 1/2（50.0%） |
| tag:colloquial | 1/2（50.0%） |
| tag:complete | 10/19（52.6%） |
| tag:conflict | 0/10（0.0%） |
| tag:conflict_duration | 0/3（0.0%） |
| tag:conflict_font | 0/8（0.0%） |
| tag:dispute | 0/2（0.0%） |
| tag:full | 1/4（25.0%） |
| tag:invalid | 2/17（11.8%） |
| tag:invalid_duration | 0/11（0.0%） |
| tag:invalid_font | 2/7（28.6%） |
| tag:missing | 9/17（52.9%） |
| tag:missing_all | 2/2（100.0%） |
| tag:missing_duration | 9/11（81.8%） |
| tag:missing_font | 3/8（37.5%） |
| tag:missing_personalization | 2/7（28.6%） |
| tag:multi_invalid | 0/1（0.0%） |
| tag:multi_issue | 3/21（14.3%） |
| tag:multi_missing | 2/6（33.3%） |
| tag:multi_turn | 9/14（64.3%） |
| tag:multi_value | 0/1（0.0%） |
| tag:needs_clarification | 1/2（50.0%） |
| tag:negation | 0/1（0.0%） |
| tag:no_inference | 2/5（40.0%） |
| tag:occupation_only | 2/2（100.0%） |
| tag:scene_only | 1/2（50.0%） |
| tag:short_list | 0/1（0.0%） |
| tag:unclear | 0/1（0.0%） |
| tag:variation | 1/5（20.0%） |

### 自动检查失败与语义复核清单

- `V2-D005`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D007`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D008`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D009`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D013`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D014`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D016`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D017`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D019`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D021`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D023`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D024`：`{"field_diff": ["duration_minutes", "status"], "missing_issues": [["invalid_value", "duration_minutes"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D025`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D027`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D028`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D030`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D031`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D033`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D034`：`{"field_diff": [], "missing_issues": [["conflicting_values", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D035`：`{"field_diff": [], "missing_issues": [["conflicting_values", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D036`：`{"field_diff": ["status"], "missing_issues": [["invalid_value", "duration_minutes"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D039`：`{"field_diff": [], "missing_issues": [["conflicting_values", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D041`：`{"field_diff": ["scene", "status"], "missing_issues": [["conflicting_values", "font"], ["invalid_value", "font"]], "extra_issues": [["missing_field", "font"]], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D043`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D044`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D045`：`{"field_diff": ["duration_minutes"], "missing_issues": [["conflicting_values", "font"], ["invalid_value", "duration_minutes"]], "extra_issues": [["conflicting_values", "requirement"]], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D047`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D049`：`{"field_diff": [], "missing_issues": [["conflicting_values", "duration_minutes"], ["conflicting_values", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D050`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D052`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D054`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D056`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D058`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D060`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D063`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D065`：`{"field_diff": [], "missing_issues": [["conflicting_values", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D067`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D068`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D069`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D074`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D075`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D078`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D080`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D082`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-D084`：`{"field_diff": ["font", "status"], "missing_issues": [["invalid_value", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D086`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D087`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D088`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D090`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D092`：`{"field_diff": ["font", "status"], "missing_issues": [["invalid_value", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D094`：`{"field_diff": [], "missing_issues": [["conflicting_values", "font"], ["missing_field", "duration_minutes"]], "extra_issues": [["invalid_value", "duration_minutes"]], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D096`：`{"field_diff": ["duration_minutes", "status"], "missing_issues": [["invalid_value", "duration_minutes"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D098`：`{"field_diff": ["occupation"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`

## val

- 输入 35 条；语义组 32；独立会话 3。
- 自动检查全部一致：9/35（25.7%）
- 完整问题集合一致：24/35（68.6%）
- 错误放行率：1/27（3.7%）
- 模型错误召回率：6/28（21.4%）
- 模型错误精确率：6/7（85.7%）
- 技术失败：{}
- 端到端已确认成功：2/35（5.7%）；语义待复核 7 条（未复核不能作为最终成功率）。

| 字段 | 成功解析样本准确率 | 非空答案准确率 |
|---|---|---|
| occupation | 35/35（100.0%） | 28/28（100.0%） |
| scene | 19/35（54.3%） | 5/21（23.8%） |
| font | 33/35（94.3%） | 17/17（100.0%） |
| duration_minutes | 34/35（97.1%） | 17/17（100.0%） |
| status | 27/35（77.1%） | 27/35（77.1%） |

| 分桶 | 自动一致 / 全部（包含技术失败） |
|---|---|
| source:migrated | 1/2（50.0%） |
| source:new | 8/33（24.2%） |
| status:complete | 2/8（25.0%） |
| status:invalid | 0/17（0.0%） |
| status:needs_clarification | 7/10（70.0%） |
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
| tag:missing | 5/9（55.6%） |
| tag:missing_all | 2/2（100.0%） |
| tag:missing_duration | 3/6（50.0%） |
| tag:missing_font | 3/6（50.0%） |
| tag:missing_personalization | 1/2（50.0%） |
| tag:multi_invalid | 0/1（0.0%） |
| tag:multi_issue | 2/13（15.4%） |
| tag:multi_missing | 2/4（50.0%） |
| tag:multi_turn | 0/6（0.0%） |
| tag:needs_clarification | 2/2（100.0%） |
| tag:negation | 1/1（100.0%） |
| tag:no_inference | 2/3（66.7%） |
| tag:no_inference_default | 0/1（0.0%） |
| tag:occupation_only | 1/1（100.0%） |
| tag:reordered | 1/1（100.0%） |
| tag:scene_only | 0/1（0.0%） |
| tag:unclear | 1/1（100.0%） |
| tag:variation | 2/3（66.7%） |

### 自动检查失败与语义复核清单

- `V2-V006`：`{"field_diff": ["scene", "status"], "missing_issues": [], "extra_issues": [["missing_field", "personalization"]], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V010`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-V012`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-V015`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V018`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V020`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V022`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V026`：`{"field_diff": ["duration_minutes", "status"], "missing_issues": [["invalid_value", "duration_minutes"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V029`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V032`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V037`：`{"field_diff": ["status"], "missing_issues": [["invalid_value", "duration_minutes"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V038`：`{"field_diff": ["scene", "font", "status"], "missing_issues": [["conflicting_values", "font"], ["invalid_value", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V040`：`{"field_diff": [], "missing_issues": [["invalid_value", "duration_minutes"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V042`：`{"field_diff": ["scene", "status"], "missing_issues": [["invalid_value", "duration_minutes"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V046`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V048`：`{"field_diff": ["status"], "missing_issues": [["invalid_value", "duration_minutes"]], "extra_issues": [["conflicting_values", "duration_minutes"]], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V051`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V053`：`{"field_diff": [], "missing_issues": [["conflicting_values", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V055`：`{"field_diff": ["scene", "font", "status"], "missing_issues": [["conflicting_values", "font"], ["invalid_value", "font"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V057`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V070`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V071`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-V072`：`{"field_diff": ["scene"], "missing_issues": [["conflicting_values", "duration_minutes"]], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V073`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-V076`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V077`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V083`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V085`：`{"field_diff": ["scene"], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": false, "message_literal_match": true, "message_review": "not_needed", "failure_reason": null}`
- `V2-V089`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V091`：`{"field_diff": ["status"], "missing_issues": [["conflicting_values", "font"], ["invalid_value", "font"]], "extra_issues": [["missing_field", "font"]], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V093`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V095`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": false, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V097`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": false, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`

