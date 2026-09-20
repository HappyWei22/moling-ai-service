# 需求解析（W03-1）

[返回 README](../README.md) · [接口说明](api.md) · [开发指南](development.md) · [解析说明](parsing.md) · [验证与待办](verification.md)

## 版本与范围

| 项 | 内容 |
|---|---|
| 任务 | W03-1 按历史路线验证 Qwen 提示词与结构化输出 |
| 主负责人 | 尚星纬 |
| 复核 | W03-3 · 罗占勇 |
| 状态 | 真实批次已跑：qwen3.8-flash，10 条 9 条与人工期望一致，剩余 1 条为标注口径争议（见验收证据） |
| 提示词版本 | v0（`parsing/prompt_v0.md`，运行记录里带 sha256 前 12 位） |
| 模型入口 | 阿里云百炼 DashScope OpenAI 兼容接口，`qwen3.8-flash`，`response_format=json_object`，temperature 0，`enable_thinking=false` |

一句话目标：**让模型把自然语言填进需求表**，填完的结果必须能直接当 `UserRequirement` 用，
缺信息要给追问，非法值不能进入规划。

## 输入与输出

- 输入：一句用户原话，例如“我是老师，每天练15分钟，想练楷书。”
- 输出：第 2 周协议 `UserRequirement`（9 个字段），状态为 `complete` / `needs_clarification` / `conflict` / `invalid`。
- 解析结果永远合法：本地 `finalize_requirement()` 会收敛模型输出，非法值置 `null` 并写入 `errors`，
  信息不足自动转成追问，所以格式问题不会带进 `WorksheetPlan`。

## 文件说明

| 文件 | 作用 |
|---|---|
| `parsing/prompt_v0.md` | 提示词 v0：任务、硬约束、输出格式、status 判定、追问话术、4 个示例 |
| `parsing/parse_requirement.py` | 解析主流程：调用 → 抽 JSON → 本地校验与状态裁定 |
| `parsing/llm_client.py` | OpenAI 兼容客户端（标准库实现）与离线固定响应客户端 |
| `parsing/config.py` | 读 `.env` 与环境变量，不把密钥写进代码或日志 |
| `parsing/errors.py` | 失败分层：config / transport / format |
| `parsing/run_parse.py` | 批量跑样例，写 `parse_runs.jsonl` 并打印逐条结论 |
| `parsing/parse_runs.jsonl` | 真实批次运行记录（2026-09-20，qwen3.8-flash，10 条） |
| `parsing/parse_runs_mock.jsonl` | 离线固定响应批次运行记录（无需密钥） |
| `parsing/mock_responses.json` | 离线固定响应，仅用于无密钥时验证流程 |
| `parsing/failure_cases.md` | 失败样例、失败分层与遗留问题 |
| `test_parse_requirement.py` | 24 个离线单测，不联网、不需要密钥 |

## 配置

复制 `.env.example` 为 `.env` 并填入密钥。`.env` 已被 `.gitignore` 忽略。

| 变量 | 默认 | 说明 |
|---|---|---|
| `DASHSCOPE_API_KEY` / `MOLING_LLM_API_KEY` | 无 | 必填，真实调用需要 |
| `MOLING_LLM_BASE_URL` | `https://dashscope.aliyuncs.com/compatible-mode/v1` | 换成其他 OpenAI 兼容入口即可 |
| `MOLING_LLM_MODEL` | 代码默认 `qwen-plus` | 实际模型名，会写进运行记录；项目当前用 `qwen3.8-flash` |
| `MOLING_LLM_TEMPERATURE` | `0` | 抽取任务建议 0 |
| `MOLING_LLM_TIMEOUT` | `60` | 秒；超时算 transport 失败，不重试（重试归 W03-4） |
| `MOLING_LLM_EXTRA_BODY` | 空 | JSON 对象，追加到请求体；qwen3 思考模型建议 `{"enable_thinking": false}`，报 400 时改为 `{}` |
| `MOLING_LLM_PROMPT_VERSION` | `v0` | 对应 `parsing/prompt_<版本>.md` |

密钥只在请求头出现；运行记录只写模型名、主机名、提示词版本和 sha256，不写密钥。

## 运行方法

在项目根目录、已激活虚拟环境：

```bash
# 1. 离线自检：不需要密钥，验证流程能跑通
python -m parsing.run_parse --client mock

# 2. 真实调用：先在 .env 里填好密钥
python -m parsing.run_parse --client real --tag w03-real

# 3. 单测（不联网）
python -m unittest -v test_parse_requirement

# 4. 启动调试接口，在 /docs 里试 POST /parse
python -m uvicorn main:app --reload
```

常用参数：`--samples` 换样例文件，`--limit 10` 只跑前 N 条，`--out` 换输出路径，
`--append` 追加而不是覆盖。退出码 0 表示全部符合人工期望，1 表示有不符合项，2 表示批次无法运行。

样例里 `split` 标为 `封存`／`sealed`／`test` 的条目默认拒绝运行（退出码 2），
避免用封存题调提示词；只有最终评估时才加 `--allow-sealed`。

离线固定响应只用于验证流程；**真实模型效果必须用 `--client real` 重跑**，
`parse_runs.jsonl` 里 `mock=true` 的记录不能当作模型效果证据。

## 接口

`POST /parse`

```json
{"text": "我是老师，每天练15分钟，想练楷书。"}
```

返回 200 和 `UserRequirement`；业务状态看响应体 `status`，不是 HTTP 状态码。
响应头带 `X-Moling-Client`、`X-Moling-Model`、`X-Moling-Prompt-Version`，方便对照运行记录。
失败时沿用统一错误格式：`PARSE_FORMAT_ERROR`（422）、`PARSE_TRANSPORT_ERROR`（502）、`PARSE_CONFIG_ERROR`（503）。

示例（缺书体，返回追问）：

```json
{
  "occupation": "教师",
  "scene": null,
  "style": null,
  "duration_minutes": 15,
  "goal": null,
  "exclusions": [],
  "status": "needs_clarification",
  "follow_up": "你想练哪种书体？目前可以按楷书、行书和行楷来规划。",
  "errors": []
}
```

## 运行记录字段

`parse_runs.jsonl` 每行一条样例，关键字段：

| 字段 | 含义 |
|---|---|
| `sample_id` / `category` / `input` / `expected` | 样例编号、类型、原话与人工期望 |
| `actual` | 本地收敛后的需求对象，可直接比对 |
| `status` | `ok_complete`、`ok_needs_clarification`、`ok_conflict`、`ok_invalid`，或 `config_error` / `transport_error` / `format_error` |
| `failure_reason` / `error_layer` / `error_detail` | 失败原因与所在层（配置、调用、格式） |
| `field_diff` | 与人工期望不一致的字段名 |
| `follow_up_check` | `ok` / `text_differs`（措辞不同但都追问）/ `missing` / `present` |
| `expectation_match` / `strict_match` | 字段与状态是否一致 / 追问措辞是否也逐字一致 |
| `client` / `mock` / `model` | 调用渠道、是否固定响应、实际模型名 |
| `prompt_version` / `prompt_sha256` / `temperature` | 可复现性信息 |
| `latency_ms` / `attempts` / `usage` / `usage_missing` | 耗时、调用次数、用量；用量拿不到时标 `usage_missing=true` |
| `warnings` / `missing_keys` / `raw_text` | 本地修复记录、模型漏掉的字段、模型原始输出（超 2000 字符截断） |

## 验收证据

- 单测：`python -m unittest -v test_parse_requirement` → 24 个方法全部通过（离线，可复跑）。
- 离线批次：`python -m parsing.run_parse --client mock` → 10/10 与人工期望一致，记录在 `parse_runs_mock.jsonl`。
- **真实批次：`python -m parsing.run_parse --client real --tag w03-real`（qwen3.8-flash，temperature 0，
  enable_thinking=false，批次 `20260920T085924Z-w03-real`）
  → 10 条中 9 条与人工期望一致**，记录在 `parse_runs.jsonl`：`mock=false`、`model=qwen3.8-flash`、
  提示词 v0 + sha256 `79d2b88b5c00`、单次调用、用量齐全、耗时 2088–3574 ms（中位 2597 ms）、
  单条 total_tokens 1585–1632。同一配置连跑两次结果一致（9/10，差异样本同为 UR-03）。
  唯一不符合项是 UR-03 的 `goal` 措辞（模型照抄原话“改善字的工整度”，标注为“改善工整度”），
  属标注口径争议，见[失败样例](../parsing/failure_cases.md)第 2.1 节，交 W03-3 裁决。
- 两条真实结论：① 10 条里 1 条模型自报状态错误（UR-07 误报 `needs_clarification`），被本地收敛纠正为 `complete`；
  ② 结构化输出本身没有格式失败，`format` 层零失败。
- 接口：`main.py` 已加 `POST /parse`，`/docs` 可试；导入服务不需要密钥，缺少密钥时只在调用时返回 503。
- 真实接口连通性：无效密钥返回 401 `invalid_api_key`、账号欠费返回 400 `Arrearage`，
  都被正确分类为 `ParseTransportError` 并保留原始报错，说明地址、请求头、请求体与错误分层可用。

## 约束与遗留问题

- 本任务不重试、不做高级监控，只提供单次调用、超时和一条耗时记录；重试、脱敏日志、批量重放归 W03-4。
- 样例仍是第 2 周的 10 条（UR-01～UR-10）；扩到 100 条、划分 60/20/20 归 W03-3，届时换 `--samples` 重跑同一脚本。
- UR-03 的 `goal` 口径待 W03-3 裁决；在裁决前**不改 Prompt、不做删减式规范化**，避免把改写用户意愿写进代码。
- 解析只判“信息是否够生成”，不判 5/15/30 的业务范围：用户说 20 分钟会解析成 `complete` + `duration_minutes=20`，
  由 Planner 决定映射（W02-1 §13 未决问题 2）。
- 追问话术由本地兜底与提示词共同决定，措辞差异用 `follow_up_check=text_differs` 标注，口径以 W03-3 标注指南为准。
- 未接通 `/parse` → `/plan` 的自动串联，集成属于 W04-4 / W05-1。
