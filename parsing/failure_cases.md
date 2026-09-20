# W03-1 失败样例与失败层说明

本文件记录解析模块会遇到的失败类型、当前处理方式和复现方法。
证据来源分三类，逐条标注：

- **单测证据**：`python -m unittest -v test_parse_requirement` 覆盖，可无密钥复现。
- **离线固定响应**：`python -m parsing.run_parse --client mock`，结果在 `parse_runs_mock.jsonl`，只证明流程，不是真实模型行为。
- **真实调用**：`python -m parsing.run_parse --client real`，结果在 `parse_runs.jsonl`。

当前仓库内 `parse_runs.jsonl` 是 **2026-09-20 真实批次**（qwen3.8-flash，10 条 9 条与人工期望一致），
`parse_runs_mock.jsonl` 是离线固定响应批次。

## 1. 失败层划分

| 层 | 异常 | 触发条件 | 是否进入规划 | 复现方式 |
|---|---|---|---|---|
| config | `ParseConfigError` | 未配置密钥、提示词文件缺失、mock 文件缺该输入 | 否 | 单测 `test_missing_key_raises_config_error` |
| transport | `ParseTransportError` | 网络失败、超时、HTTP 非 200、响应不是 JSON | 否 | 单测 `test_transport_errors_are_classified` |
| format | `ParseFormatError` | 模型文本里找不到 JSON 对象、空输出、协议字段全缺 | 否 | 单测 `test_junk_output_raises_format_error` |
| 本地修复 | 记入 `warnings` | 代码围栏、多余说明、字符串时长、非法值、不支持书体 | 修好后按业务状态处理 | 见第 3 节 |

区分这三层的意义：模型慢（transport）和模型乱输出（format）是两类问题，
排查入口和修复责任不同；`run_parse.py` 会把层名写进运行记录的 `error_layer`。

## 2. 真实批次观察（2026-09-20，qwen3.8-flash，10 条）

命令：`python -m parsing.run_parse --client real --tag w03-real`（`.env`：`MOLING_LLM_MODEL=qwen3.8-flash`、`MOLING_LLM_PROMPT_VERSION=v1`）
结果：9/10 与人工期望一致，单次调用、用量齐全、`format` 层零失败。
与 prompt v0 批次对比：差异样本同为 UR-03（goal 措辞），**UR-08 由 conflict 改为缺时长追问并已符合**。

### 2.1 唯一不符合项：UR-03 的 goal 措辞（标注口径争议）

- 输入：“我想改善字的工整度，每天练15分钟，想练楷书。”
- 人工期望：`"goal": "改善工整度"`
- 模型实际：`"goal": "改善字的工整度"`，其余字段与 `complete` 状态全部正确。
- 判断与结论（2026-09-20 已裁决）：W03-3 的口径 C-10 已定为“**只删虚词与冗余助词 + 词表映射，不做同义替换**”，同一句在 W03-3 里的标准答案是 `goal="改善工整度"`（样本 S045/S046）。
  即：这不是模型错误，而是提示词缺少规范化词表。
- 处理：本地仍不做删减式规范化（避免代码替用户改写意愿），改由 **W04-1 把词表写进提示词**；同一口径还影响 11 条 scene 样本（`板书→课堂板书`、`写病历→病历书写` 等），合计 17 条。

同一个模型跑出的这条，说明**当前的期望值本身需要复核**，而不是提示词需要调。

### 2.1b 裁决落地：UR-08 从 conflict 改为缺时长追问（C-01b）

- 输入：“我想练行书，但目前系统只支持楷书。”
- v0 批次（旧口径）：判 `conflict`（沿用 W02-1 UR-08 的写法），与 v0.3 §6“v0 支持行书”矛盾。
- v1 批次（新口径）：`style=行书` + 缺时长追问，`errors=[]`；提示词 v1 与 `examples_v0.3.json` 的 UR-08 已同步修订。
- 相关硬编码修复：`finalize_requirement()` 不再让模型把“枚举外书体”自报成 `conflict`（裁决 C-01），
  且 `errors` 点名的字段一律置 `null`（裁决 C-04，此前会保留合法值 15）。

### 2.2 模型自报状态不可信：UR-07 被本地纠正

- 输入：“我是学生，想练行书，每天15分钟。”——字段齐全，可直接生成。
- 模型自报：`status = needs_clarification`（还带了一句多余的追问）。
- 本地结果：纠正为 `complete` 并清空 `follow_up`（`warnings` 记录“字段已满足生成条件，状态已修正为 complete”）。
- 意义：10 条里有 1 条（qwen-plus 批次里是 2 条）状态自报错误。若直接信任模型状态，用户会被无意义地多问一轮。
  这正是本地 `finalize_requirement()` 必须存在的原因，也是第 4 周做字段评估时要单独统计“状态判定”这一列的依据。

### 2.3 transport：HTTP 400 账号欠费

- 现象：`GET /models` 正常（认证通过），但任何 `chat/completions` 都返回
  `HTTP 400 {"type":"Arrearage", ... overdue-payment}`；`qwen-plus`、`qwen-flash`、`qwen3.8-flash`、
  `qwen3.5-flash`、`qwen3-max`、`qwen-turbo` 六个模型全部同一错误。
- 当前处理：分类为 `ParseTransportError`，`status_code=400`，原始报错写进 `failure_reason`，
  不产生需求对象、不进入规划。
- 与模型无关：换密钥/充值后即恢复；排查看 `error_layer` 是 `transport` 还是 `format`。

### 2.4 transport：密钥无效

- 现象：`HTTP 401 invalid_api_key`。
- 当前处理：同样是 `ParseTransportError`（`status_code=401`），提示检查 `.env` 的 `DASHSCOPE_API_KEY`。

## 2b. 其它失败形态（单测/离线证据，真实批次尚未出现）

### format：模型返回解释文字而不是 JSON

- 输入示例：“我是老师，每天练15分钟，想练楷书。”
- 模型原始输出（示例）：`好的，我来帮你解析这个需求。`
- 当前处理：抛 `ParseFormatError`，该条记录 `status=format_error`、`raw_text` 保留原文，不生成需求对象。
- 单测证据：`test_junk_output_raises_format_error`。

### transport：接口参数不被支持

- 触发：`MOLING_LLM_EXTRA_BODY` 里带了模型不支持的参数（例如对非思考模型传 `enable_thinking`），接口返回 400。
- 当前处理：抛 `ParseTransportError`，记录 `status_code=400` 和截断后的响应体；提示改用 `.env` 修正配置。
- 说明：qwen3.8-flash 已实测接受 `{"enable_thinking": false}`，未触发此错误。

### transport：超时

- 触发：网络慢或模型排队超过 `MOLING_LLM_TIMEOUT`（默认 60 秒）。
- 当前处理：抛 `ParseTransportError`，该条记为失败，不重试。**重试、耗时统计和调用日志是 W03-4（杨新）的交付**，
  本任务只保证超时后不崩溃、不把失败当成解析结果。

## 3. 模型输出的常见瑕疵与本地修复（记入 warnings，不算失败）

| 现象 | 样例 | 处理 | 单测 |
|---|---|---|---|
| Markdown 代码围栏 | 输出被 ` ```json ` 包住 | 去围栏后再解析 | `test_plain_and_fenced_and_prose` |
| 结果前后有说明文字 | `{...}\n以上为解析结果。` | 取第一个 `{` 到最后一个 `}` | `test_plain_and_fenced_and_prose` |
| 时长为字符串 | `"duration_minutes": "15"` | 转成整数并记 warning | `test_aliases_and_type_repairs` |
| 非法时长 | `"duration_minutes": -10` | 置 `null`，原始值进 `errors`，状态 `invalid` | `test_illegal_values_never_reach_expected` |
| 不支持书体 | `"style": "草书"` | 置 `null`，原始值进 `errors`，状态 `invalid` | `test_unsupported_style_keeps_original_value_in_errors` |
| 别名 | `老师`、`楷体` | 规范化成 `教师`、`楷书` | `test_aliases_and_type_repairs` |
| exclusions 混入空值/非字符串 | `["不要生僻字", "", 3]` | 丢弃脏项并记 warning | `test_exclusions_and_errors_are_cleaned` |

## 4. 状态不一致的兜底

模型自己给的状态不被直接信任，本地会按第 2 周协议重判：

| 模型输出 | 本地结果 | 单测 |
|---|---|---|
| 状态 `complete`，但 `style` 为 null | 改为 `needs_clarification`，补追问话术 | `test_model_cannot_mark_complete_without_style` |
| 状态 `complete`，但职业/场景/目标全空 | 改为 `needs_clarification` | `test_model_cannot_mark_complete_without_personalization` |
| 状态 `conflict`，但没有错误明细 | 改为 `invalid` 并补 `unresolved_conflict` 错误 | `test_status_without_detail_is_repaired` |
| 状态 `needs_clarification`，但字段齐全 | 改为 `complete` 并清空追问 | 见 `finalize_requirement` |

副作用是这一步能保证：**凡是解析结果，要么是合法 `complete`，要么带明确状态和追问，绝不会把非法格式当正常需求传给规划。**

## 5. 交给后续任务的遗留问题

- **W03-3（罗占勇）**：① ~~裁决 UR-03 的 goal 口径~~ **已于 2026-09-20 完成**（C-10：删冗余助词+词表映射，
  结论已写入《W03-3_口径裁决确认.md》并落入样本 v1.2）；② 100 条样本已交付并冻结（v1.2），
  按样本编号把第 2 节的观察扩成失败清单可在 W04-1 展开；③ 追问措辞口径由标注指南统一。
- **W03-4（杨新）**：超时上限、有限重试、重试次数单独记录、脱敏日志、批量重放入口。
  本任务的调用层只有单次调用和一条 `latency_ms`（真实批次 2088–3574 ms，中位 2597 ms）。
- **W04-1（尚星纬）**：① 把 W03-3 的规范化词表（C-10）搬进提示词——影响 17 条标准答案；
  ② 字段漏提取、错误补全（把没说的信息补上）、模型自报状态错误（UR-07 一类）；
  ③ “20 分钟”这类非 5/15/30 时长的映射。
- **评估表格**：第 4 周的字段评估要把“状态判定”作为单独一列统计，本批次它是唯一出错的一列（1/10）。
