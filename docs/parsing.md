# 需求解析（W03-1）

[返回 README](../README.md) · [接口说明](api.md) · [开发指南](development.md) · [解析说明](parsing.md) · [验证与待办](verification.md)

## 版本与范围

| 项 | 内容 |
|---|---|
| 任务 | W03-1 按历史路线验证 Qwen 提示词与结构化输出 |
| 主负责人 | 尚星纬 |
| 复核 | W03-3 · 罗占勇 |
| 状态 | 真实批次已跑两轮：**prompt v1 + qwen3.8-flash**，10 条 9 条与人工期望一致；
剩余 1 条（UR-03 的 goal 措辞）已由 W03-3 口径 C-10 定为“删冗余助词”，属 W04-1 落地事项 |
| 提示词版本 | **v1**（`parsing/prompt_v1.md`，2026-09-20 按裁决 C-01/C-01b/C-02/C-17 修订）；
v0 保留为冻结基线，便于前后对比。运行记录里带版本号与 sha256 前 12 位 |
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
| `parsing/prompt_v1.md` | **当前提示词**：在 v0 基础上按裁决修正 status 判定、errors 受控词表、多书体规则、UR-08 示例 |
| `parsing/prompt_v0.md` | 提示词 v0（冻结基线）：任务、硬约束、输出格式、status 判定、追问话术、示例 |
| `parsing/parse_requirement.py` | 解析主流程：调用 → 抽 JSON → 本地校验与状态裁定 |
| `parsing/llm_client.py` | OpenAI 兼容客户端（标准库实现）与离线固定响应客户端 |
| `parsing/config.py` | 读 `.env` 与环境变量，不把密钥写进代码或日志 |
| `parsing/errors.py` | 失败分层：config / transport / format |
| `parsing/run_parse.py` | 批量跑样例，写 `parse_runs.jsonl` 并打印逐条结论 |
| `parsing/parse_runs.jsonl` | 真实批次运行记录（2026-09-20，qwen3.8-flash，10 条） |
| `parsing/parse_runs_mock.jsonl` | 离线固定响应批次运行记录（无需密钥） |
| `parsing/mock_responses.json` | 离线固定响应，仅用于无密钥时验证流程 |
| `parsing/failure_cases.md` | 失败样例、失败分层与遗留问题 |
| `try_parse.py` | 单条验证入口：输入一句话，打印需求 JSON 与能否进入规划的提示 |
| `test_parse_requirement.py` | 27 个离线单测，不联网、不需要密钥 |

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
| `MOLING_LLM_PROMPT_VERSION` | `v1` | 对应 `parsing/prompt_<版本>.md`；v0 为冻结基线 |

密钥只在请求头出现；运行记录只写模型名、主机名、提示词版本和 sha256，不写密钥。

## 运行方法

在项目根目录、已激活虚拟环境：

```bash
# 1. 单条验证：输入一句话，直接打印需求 JSON（最常用）
python try_parse.py "我是老师，每天练15分钟，想练楷书。"

# 2. 离线自检：不需要密钥，验证流程能跑通
python -m parsing.run_parse --client mock

# 3. 真实调用：先在 .env 里填好密钥
python -m parsing.run_parse --client real --tag w03-real

# 4. 单测（不联网）
python -m unittest -v test_parse_requirement

# 5. 启动调试接口，在 /docs 里试 POST /parse
python -m uvicorn main:app --reload
```

`try_parse.py` 的 JSON 走 stdout、诊断信息走 stderr，所以 `python try_parse.py "..." 2>/dev/null`
拿到的就是纯 JSON；不带参数运行会提示交互输入；`--mock` 只认识 `mock_responses.json` 里的 10 条固定输入。
它还会顺带说明该结果能否直接提交 `POST /plan`：例如“每天练20分钟”会解析成 `complete`，
但规划入口只接受 5/15/30 分钟，于是提示不能直接生成计划。

常用参数：`--samples` 换样例文件（**JSON 数组或 JSONL 都支持**），`--splits dev,val` 只跑指定分集
（先于封存检查生效），`--limit 10` 只跑前 N 条，`--out` 换输出路径，`--append` 追加而不是覆盖，
`--report 路径.md` 另写一份评测报告（分集/类型/规划侧门禁分桶 + 字段级准确率 + 失败清单）。
退出码 0 表示全部符合人工期望，1 表示有不符合项，2 表示批次无法运行。

样例里 `split` 标为 `封存`／`sealed`／`test` 的条目默认拒绝运行（退出码 2），
避免用封存题调提示词；只有最终评估时才加 `--allow-sealed`。若只想跑开发/验证集，
用 `--splits dev,val` 先把封存样本过滤掉，就不会触发这条保护。

### 接 W03-3 的 100 条样本

```bash
# 开发集 + 验证集（80 条），产出评测报告
python -m parsing.run_parse --client real --tag w03-3-dev-val \
  --samples ../moling-W03-3/samples_100.jsonl --splits dev,val \
  --out parsing/parse_runs_100.jsonl --report parsing/eval_report.md

# 封存集：仅最终评估，运行前必须按 W03-3《封存访问记录》登记
python -m parsing.run_parse --client real --samples ../moling-W03-3/samples_100.jsonl \
  --splits sealed --allow-sealed --out parsing/parse_runs_sealed.jsonl
```

报告的读法（与 W03-3 的约定一致）：

- **按分集**：dev 用于定位失败、val 用于前后对比；封存集结果必须单独成节，不与前两者混算。
- **按规划侧门禁**：`block` 是契约边界（非标准时长、非空 exclusions），
  下游算准确率时不能把它当成"模型理解错误"，否则基线被压低约 16 个百分点。
- **字段级准确率**：分母是成功解析的样本数；`follow_up` 同时给"逐字一致"和"仅要求该问就问"两行。
- **失败清单**：全部列出（不豁免），每行标出解析失败层或差异字段。

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

- 单测：`python -m unittest -v test_parse_requirement` → **27 个方法全部通过**（离线，可复跑），
  含裁决新增用例：枚举外书体不得判 conflict（C-01）、errors 点名字段一律置 null（C-04）、
  多书体并列判 conflict（C-02）、书体与排除项重合保留 conflict（C-08b）。
- 离线批次：`python -m parsing.run_parse --client mock` → 10/10 与人工期望一致，记录在 `parse_runs_mock.jsonl`。
- **真实批次（prompt v1）：`python -m parsing.run_parse --client real --tag w03-real`
  → 10 条中 9 条与人工期望一致**，记录在 `parse_runs.jsonl`：`mock=false`、`model=qwen3.8-flash`、
  提示词 v1 + sha256 `9655d603c46e`、单次调用、用量齐全。
  唯一不符合项仍是 UR-03 的 `goal` 措辞（模型照抄“改善字的工整度”），
  该口径已由 W03-3 裁决 C-10 定为“删冗余助词 + 词表映射、不做同义替换”，
  **属 W04-1 的提示词落地事项**（见下“约束与遗留问题”）。
- 裁决落地效果：UR-08（「我想练行书，但目前系统只支持楷书」）由 `conflict` 改为
  `style=行书` + 缺时长追问，真实批次已符合；提示词 v0 批次该条为 conflict（错误口径），
  两轮记录可直接对比。
- **100 条样本首批评测（2026-09-20，dev+val 80 条，封存集未跑）**：
  `python -m parsing.run_parse --client real --tag w03-3-dev-val --samples ../moling-W03-3/samples_100.jsonl
  --splits dev,val --out parsing/parse_runs_100.jsonl --report parsing/eval_report.md`
  → **完全一致 57/80（71.2%）**，dev 70.0% / val 75.0%，零解析失败。
  字段级：duration 100% · style 98.8% · exclusions 98.8% · occupation 97.5% · status 97.5% ·
  errors 95.0% · goal 93.8% · scene 85.0%；`follow_up` 逐字 91.2%、"该问就问" **100%**。
  23 条失败全部是提示词缺口径（scene 词表、goal 删冗余助词等 9 类），清单见
  [失败样例](../parsing/failure_cases.md)第 2c 节。报告按 `split`、`category`、`plan_gate` 分桶，
  `plan_gate=block` 单独列出，避免下游把契约边界计成模型错误。
- 两条真实结论：① 模型自报状态不可信（UR-07 误报 `needs_clarification`、UR-03 在 v0 批次误报），
  被本地收敛纠正，说明 `finalize_requirement()` 的收口是必需环节；
  ② 结构化输出本身没有格式失败，`format` 层零失败。
- 接口：`main.py` 已加 `POST /parse`，`/docs` 可试；导入服务不需要密钥，缺少密钥时只在调用时返回 503。
- 真实接口连通性：无效密钥返回 401 `invalid_api_key`、账号欠费返回 400 `Arrearage`，
  都被正确分类为 `ParseTransportError` 并保留原始报错，说明地址、请求头、请求体与错误分层可用。

## 约束与遗留问题

- 本任务不重试、不做高级监控，只提供单次调用、超时和一条耗时记录；重试、脱敏日志、批量重放归 W03-4。
- **W04-1 首要事项：把 W03-3 的口径搬进 `prompt_v2.md`**。首批评测的 23 条失败已归成 9 类规则
  （scene 词表、goal 删冗余助词、书写工具不是书体、区间时长按未提供、`errors.value` 形式、
  exclusions 去修饰、多职业 `/` 连接、场景词出现在 goal 中不算 scene、书体与排除项重合的写法），
  逐条清单见[失败样例](../parsing/failure_cases.md)第 2c 节。改完跑同一条命令对比 val 桶分数即可。
- 样例仍是第 2 周的 10 条（UR-01～UR-10）；扩到 100 条、按 `split` 分桶评测归 W03-3 + W04-3，
  届时换 `--samples` 并支持 JSONL 格式后重跑。
- 注意：裁决 C-01b 之后，这 10 条开发样例里**已没有 conflict 样本**（原 UR-08 改为缺时长追问）；
  conflict 类的评估样本在 W03-3 的 S068(dev)、S069/S070(val)。
- 解析只判“信息是否够生成”，不判 5/15/30 的业务范围：用户说 20 分钟会解析成 `complete` + `duration_minutes=20`，
  由 Planner 决定映射（W02-1 §13 未决问题 2）。
- 追问话术由本地兜底与提示词共同决定，措辞差异用 `follow_up_check=text_differs` 标注，口径以 W03-3 标注指南为准。
- 未接通 `/parse` → `/plan` 的自动串联，集成属于 W04-4 / W05-1。
