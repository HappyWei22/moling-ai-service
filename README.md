# 墨灵 AI 模块

本模块提供自然语言需求解析和临摹练习计划生成，后端接入使用两个接口：

- `POST /parse/v2`：提取职业、书写场景、书体和练习时长；信息有缺失、非法值或冲突时，一次返回覆盖全部已识别问题的追问。
- `POST /plan/v2`：接收解析完成的需求，返回 `WorksheetPlan`。当前为固定模拟计划，响应中 `is_mock=true`。

v2 模型负责提取信息、识别非法值和语义冲突，不生成 `follow_up`。本地代码沿用 `errors` 汇总问题、补齐缺失项并去重，生成最终的 `message`。非法值或冲突导致字段置空时，不会再重复报缺失。

当前支持书体 **楷书、行书、行楷**，单次时长 **5、15、30 分钟**，练习形式为临摹。生成条件是书体、时长明确，且职业或书写场景至少提供一项，没有未解决的问题。状态优先级为 `invalid > conflict > needs_clarification > complete`。

计划输出沿用 v0.3 协议；尚未实现个性化选词、字帖渲染或 AI 评分，字格配额仍是暂定工程规则。旧 `/parse`、`/plan` 保留供 v1 联调和历史评测使用。

## 本地运行

建议使用 Python 3.12，在包含 `main.py` 的项目根目录执行。每台电脑自行创建虚拟环境，不要复制他人的 `.venv`。

### 1. 创建并激活环境

macOS：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

环境只需创建一次；新终端需重新激活。Windows 激活失败时见[故障排查](docs/development.md#windows-故障排查)。

### 2. 安装依赖和配置模型

```bash
python -m pip install -r requirements.txt
```

复制项目根目录的 `.env.example` 为 `.env`，填写 `DASHSCOPE_API_KEY`；模型名、调用地址、超时等使用文件中的配置。不要提交真实密钥。

v2 固定读取 `parsing/prompt_v2.md`；`.env` 中的 `MOLING_LLM_PROMPT_VERSION` 仅控制旧版解析，不影响 `/parse/v2` 或默认的 `try_parse.py`。

### 3. 验证解析

```bash
python try_parse.py
python try_parse.py "每天练-10分钟"
```

默认调用真实模型并使用 v2，输出与 `/parse/v2` 一致的 `code/message/data`。输入“每天练-10分钟”时，应同时提示书体缺失、时长非法、职业或场景缺失；问题是否识别完整仍依赖模型提取结果。

只取 JSON：`python try_parse.py "…" 2>/dev/null`。旧版解析使用 `python try_parse.py --version v1 "…"`。

没有密钥时，可用固定样例验证 v2 流程：

```bash
python try_parse.py --mock "我是学生，每天练-10分钟，想练楷书。"
python -m unittest discover -v
python try_ai.py
```

`--mock` 只支持 `parsing/mock_responses.json` 中的固定输入，不会解析任意文本。`try_ai.py` 验证模拟计划生成，不需要模型密钥。

### 4. 启动服务

```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

打开 [Swagger 调试页](http://127.0.0.1:8000/docs)，选择 `/parse/v2` 和 `/plan/v2`。停止服务按 `Ctrl + C`。

## 后端接入步骤

建议通过 HTTP 调用本服务，后端自己的语言和框架不受限制。将本仓库代码放在独立目录，按上面的步骤安装依赖、配置密钥并启动服务。

后端配置一个服务地址，例如本机联调使用 `http://127.0.0.1:8000`。跨机器或容器联调时，启动命令中的 `--host` 使用 `0.0.0.0`，调用地址改为服务实际可达的主机地址；容器内的 `127.0.0.1` 指向容器自身。部署时去掉 `--reload`。当前代码没有应用层鉴权，服务访问范围由部署环境控制。

### 1. 后端维护会话，并调用解析

本服务不生成或保存 `session_id`，请求只接受 `text`。后端负责：

1. 创建会话，保存用户每一轮回答。
2. 将本次会话的用户原话按时间顺序合并，明确保留后续补充或修正。
3. 每次收到回答后，将合并文本提交 `/parse/v2`。

不要只发送最后一句“15分钟”，否则解析服务拿不到前面的职业和书体；也不要把系统追问中的书体、时长选项当作用户选择写进文本。

第一轮示例：

```bash
curl -X POST http://127.0.0.1:8000/parse/v2 \
  -H 'Content-Type: application/json' \
  -d '{"text":"每天练-10分钟"}'
```

HTTP 200，响应示例（具体提示随识别到的问题而定）：

```json
{
  "code": 400,
  "message": "请补充或修改以下信息：1. 你想练哪种书体？目前支持楷书、行书或行楷。 2. 练习时长不符合要求（你提供的是-10），请选择5、15或30分钟。 3. 你是什么职业，或者主要在哪种场景使用书写？",
  "data": null
}
```

**这里的 `400` 是响应体中的业务码，HTTP 状态仍是 200。** 后端展示完整 `message`，等待用户补充，不调用计划接口。内部 `errors` 和未完成的字段不会通过这个响应返回。

用户回答“我是学生，练楷书，时长改成15分钟”后，后端再次提交：

```json
{
  "text": "第1轮用户：每天练-10分钟。\n第2轮用户：我是学生，练楷书，时长改成15分钟。"
}
```

模型按提示词将后续明确修正用于当前需求，信息完整时返回：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "occupation": "学生",
    "scene": null,
    "font": "楷书",
    "duration_minutes": 15,
    "status": "complete"
  }
}
```

### 2. 将完成的 data 提交计划接口

仅当 HTTP 200、`code=0` 且 `data.status=complete` 时，将 **`data` 对象本身**提交 `/plan/v2`，不要提交外层 `code/message/data`。

```bash
curl -X POST http://127.0.0.1:8000/plan/v2 \
  -H 'Content-Type: application/json' \
  -d '{"occupation":"学生","scene":null,"font":"楷书","duration_minutes":15,"status":"complete"}'
```

成功返回 HTTP 200，响应直接是 `WorksheetPlan`，没有 `code/message/data` 外层包装。包含 `plan_id`、`style`、`duration_minutes`、`is_mock`、`items` 等字段。解析中的 `font` 在服务内部映射为计划中的 `style`，后端不需要自行转换。

当前生成的是模拟临摹计划，后端应保留 `is_mock` 标识；计划请求不需要模型密钥。完整结构见[接口说明](docs/api.md)和 Swagger。

### 3. 区分业务追问与服务错误

| 接口 / HTTP 状态 | 判断依据 | 后端处理 |
|---|---|---|
| `/parse/v2` / 200 | `code=400`、`data=null` | 展示完整 `message`，保存用户下一轮回答，再解析 |
| `/parse/v2` / 200 | `code=0`、`data.status=complete` | 保存完成需求，将 `data` 提交计划接口 |
| `/parse/v2` / 422 | `detail.code=VALIDATION_ERROR` 或 `PARSE_FORMAT_ERROR` | 检查请求，或记录模型输出格式失败；不能当作业务追问 |
| `/parse/v2` / 502 | `detail.code=PARSE_TRANSPORT_ERROR` | 模型网络、超时或接口失败，按后端重试策略处理 |
| `/parse/v2` / 503 | `detail.code=PARSE_CONFIG_ERROR` | 检查服务端模型配置 |
| `/plan/v2` / 200 | 响应为计划对象 | 保存并交给后续字帖渲染流程 |
| `/plan/v2` / 422 | `VALIDATION_ERROR` 或 `REQUIREMENT_NOT_READY` | 检查提交结构、状态、书体、时长与职业或场景 |

错误响应结构示例：

```json
{
  "detail": {
    "code": "PARSE_CONFIG_ERROR",
    "message": "缺少模型密钥，无法进行真实调用",
    "fields": []
  }
}
```

后端应先检查 HTTP 状态，再读取业务码；不要对所有响应都读取 `data`。模型超时默认 60 秒，后端调用解析服务的等待时间应留出额外的网络和处理余量，避免服务仍在解析而后端提前超时。调用失败时保留会话历史，重试沿用同一份完整用户信息。

联调时还可查看响应头 `X-Moling-Client`、`X-Moling-Model`、`X-Moling-Prompt-Version`；新解析接口的提示词版本应显示 `v2`。

## 旧版评测与更多文档

批量脚本已支持 v2，显式使用 `--protocol v2` 和 v2 标准答案：

```bash
python -m parsing.run_parse --protocol v2 --client real \
  --samples v2_eval/samples_v2.jsonl --splits dev,val \
  --out /tmp/moling-v2-runs.jsonl --report /tmp/moling-v2-report.md
```

正式样本由建集任务交付。可先使用仓库的两条 smoke 样本验证流程：

```bash
python -m parsing.run_parse --protocol v2 --client mock \
  --samples parsing/fixtures/v2_smoke_samples.jsonl \
  --mock-file parsing/fixtures/v2_smoke_responses.json \
  --out /tmp/moling-v2-smoke-runs.jsonl --report /tmp/moling-v2-smoke-report.md
```

v2 检查五字段、模型错误、全部问题及业务响应。追问语义需人工复核，退出码 0 仅表示自动检查通过；mock 不能作为真实模型成绩。详细格式与指标见 [v2 评测集建设任务说明](docs/v2评测集建设任务说明.md)。

以下不带 `--protocol v2` 的历史命令仍使用 v1：

```bash
python -m parsing.run_parse --client mock
python -m parsing.run_parse --client real --tag w03-real
```

历史运行记录和评测口径见[解析说明](docs/parsing.md)。v2 离线契约测试可单独运行：

```bash
python -m unittest -v test_parse_v2
```

| 文档 | 内容 |
|---|---|
| [接口说明](docs/api.md) | v2 接入协议、旧版请求与响应、统一错误格式、字格规则 |
| [解析说明](docs/parsing.md) | v1 配置、提示词、批处理评测、运行记录与失败分层 |
| [失败样例](parsing/failure_cases.md) | 常见模型瑕疵、本地修复和遗留问题 |
| [开发指南](docs/development.md) | 文件说明、替换生成器、Schema 维护、验证命令、Windows 故障排查 |
| [验证记录与待办](docs/verification.md) | 历史验证结果、未验证环境与团队待确认事项 |
