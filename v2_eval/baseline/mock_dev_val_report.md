# v2 需求解析评测报告

- 批次：`20261009T111728Z`
- 样本 SHA256：`b1c1f82a0bfe2a825ff2247948829b84a6d041ea5538281d70c0e2c37b1c99f7`
- 模型：`mock-qwen`；提示词 SHA256：`97664f29304af5ccdd37653b455ec1bdc7cb98f59ce0206de2180ca83c3f3bce`
- 调用：`mock`；代码提交：`None`

> 本报告的 API 比较由解析结果构造，未发起 HTTP 请求；真实 HTTP 契约另由接口测试验证。
> 自动检查不等于追问语义验收；pending 项需人工检查 required/forbidden，并统计漏问、重复问、多余问。

> 本批使用 mock 固定响应，只验证评测流程，不是模型效果证据。

## dev

- 输入 63 条；语义组 56；独立会话 7。
- 自动检查全部一致：63/63（100.0%）
- 完整问题集合一致：63/63（100.0%）
- 错误放行率：0/44（0.0%）
- 模型错误召回率：41/41（100.0%）
- 模型错误精确率：41/41（100.0%）
- 技术失败：{}
- 端到端已确认成功：19/63（30.2%）；语义待复核 44 条（未复核不能作为最终成功率）。

| 字段 | 成功解析样本准确率 | 非空答案准确率 |
|---|---|---|
| occupation | 63/63（100.0%） | 46/46（100.0%） |
| scene | 63/63（100.0%） | 22/22（100.0%） |
| font | 63/63（100.0%） | 36/36（100.0%） |
| duration_minutes | 63/63（100.0%） | 32/32（100.0%） |
| status | 63/63（100.0%） | 63/63（100.0%） |

| 分桶 | 自动一致 / 全部（包含技术失败） |
|---|---|
| source:migrated | 12/12（100.0%） |
| source:new | 51/51（100.0%） |
| status:complete | 19/19（100.0%） |
| status:invalid | 26/26（100.0%） |
| status:needs_clarification | 18/18（100.0%） |
| tag:alias | 2/2（100.0%） |
| tag:boundary | 3/3（100.0%） |
| tag:chinese_number | 2/2（100.0%） |
| tag:colloquial | 2/2（100.0%） |
| tag:complete | 19/19（100.0%） |
| tag:conflict | 10/10（100.0%） |
| tag:conflict_duration | 3/3（100.0%） |
| tag:conflict_font | 8/8（100.0%） |
| tag:dispute | 2/2（100.0%） |
| tag:full | 4/4（100.0%） |
| tag:invalid | 17/17（100.0%） |
| tag:invalid_duration | 11/11（100.0%） |
| tag:invalid_font | 7/7（100.0%） |
| tag:missing | 17/17（100.0%） |
| tag:missing_all | 2/2（100.0%） |
| tag:missing_duration | 11/11（100.0%） |
| tag:missing_font | 8/8（100.0%） |
| tag:missing_personalization | 7/7（100.0%） |
| tag:multi_invalid | 1/1（100.0%） |
| tag:multi_issue | 21/21（100.0%） |
| tag:multi_missing | 6/6（100.0%） |
| tag:multi_turn | 14/14（100.0%） |
| tag:multi_value | 1/1（100.0%） |
| tag:needs_clarification | 2/2（100.0%） |
| tag:negation | 1/1（100.0%） |
| tag:no_inference | 5/5（100.0%） |
| tag:occupation_only | 2/2（100.0%） |
| tag:scene_only | 2/2（100.0%） |
| tag:short_list | 1/1（100.0%） |
| tag:unclear | 1/1（100.0%） |
| tag:variation | 5/5（100.0%） |

### 自动检查失败与语义复核清单

- `V2-D013`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D014`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D016`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D017`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D019`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D021`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D023`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D024`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D025`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D027`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D028`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D030`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D031`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D033`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D034`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D035`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D036`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D039`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D041`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D043`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D044`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D045`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D047`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D049`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D050`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D052`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D054`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D056`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D058`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D060`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D063`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D065`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D067`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D068`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D069`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D074`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D084`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D086`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D087`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D088`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D090`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D092`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D094`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-D096`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`

## val

- 输入 35 条；语义组 32；独立会话 3。
- 自动检查全部一致：35/35（100.0%）
- 完整问题集合一致：35/35（100.0%）
- 错误放行率：0/27（0.0%）
- 模型错误召回率：28/28（100.0%）
- 模型错误精确率：28/28（100.0%）
- 技术失败：{}
- 端到端已确认成功：8/35（22.9%）；语义待复核 27 条（未复核不能作为最终成功率）。

| 字段 | 成功解析样本准确率 | 非空答案准确率 |
|---|---|---|
| occupation | 35/35（100.0%） | 28/28（100.0%） |
| scene | 35/35（100.0%） | 21/21（100.0%） |
| font | 35/35（100.0%） | 17/17（100.0%） |
| duration_minutes | 35/35（100.0%） | 17/17（100.0%） |
| status | 35/35（100.0%） | 35/35（100.0%） |

| 分桶 | 自动一致 / 全部（包含技术失败） |
|---|---|
| source:migrated | 2/2（100.0%） |
| source:new | 33/33（100.0%） |
| status:complete | 8/8（100.0%） |
| status:invalid | 17/17（100.0%） |
| status:needs_clarification | 10/10（100.0%） |
| tag:alias | 1/1（100.0%） |
| tag:boundary | 2/2（100.0%） |
| tag:complete | 8/8（100.0%） |
| tag:conflict | 10/10（100.0%） |
| tag:conflict_duration | 5/5（100.0%） |
| tag:conflict_font | 5/5（100.0%） |
| tag:dispute | 2/2（100.0%） |
| tag:full | 2/2（100.0%） |
| tag:invalid | 9/9（100.0%） |
| tag:invalid_duration | 5/5（100.0%） |
| tag:invalid_font | 5/5（100.0%） |
| tag:missing | 9/9（100.0%） |
| tag:missing_all | 2/2（100.0%） |
| tag:missing_duration | 6/6（100.0%） |
| tag:missing_font | 6/6（100.0%） |
| tag:missing_personalization | 2/2（100.0%） |
| tag:multi_invalid | 1/1（100.0%） |
| tag:multi_issue | 13/13（100.0%） |
| tag:multi_missing | 4/4（100.0%） |
| tag:multi_turn | 6/6（100.0%） |
| tag:needs_clarification | 2/2（100.0%） |
| tag:negation | 1/1（100.0%） |
| tag:no_inference | 3/3（100.0%） |
| tag:no_inference_default | 1/1（100.0%） |
| tag:occupation_only | 1/1（100.0%） |
| tag:reordered | 1/1（100.0%） |
| tag:scene_only | 1/1（100.0%） |
| tag:unclear | 1/1（100.0%） |
| tag:variation | 3/3（100.0%） |

### 自动检查失败与语义复核清单

- `V2-V015`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V018`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V020`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V022`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V026`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V029`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V032`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V037`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V038`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V040`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V042`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V046`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V048`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V051`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V053`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V055`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V057`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V070`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V072`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V076`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V077`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V083`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V089`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V091`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V093`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V095`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`
- `V2-V097`：`{"field_diff": [], "missing_issues": [], "extra_issues": [], "model_errors_match": true, "model_status_match": true, "raw_contract_match": true, "api_match": true, "message_literal_match": true, "message_review": "pending", "failure_reason": null}`

