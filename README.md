# 墨灵 AI 模块

接收结构化的 `UserRequirement`，返回 `WorksheetPlan`，并提供 FastAPI 调试接口。
当前采用 **v0.3 协议修订稿和固定假数据**，已支持替换生成器。
第 3 周新增 `POST /parse`：把用户自然语言解析成 `UserRequirement`（提示词 v1 + Qwen 结构化输出 + 本地校验）。

第一版仅支持临摹和 5/15/30 分钟；非空排除项暂时拒绝。
尚未实现个性化选词、字帖渲染或 AI 评分，协议和暂定字格配额仍待团队确认。
真实模型调用需要 `.env` 里的密钥；没有密钥时可以用离线固定响应跑通流程。

## 快速开始

建议使用 Python 3.12。打开终端，进入包含 `main.py` 的项目根目录。
每台电脑自行创建虚拟环境，不要复制他人的 `.venv`。

### 1. 创建并激活环境

Windows PowerShell：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS（确认 `python3` 为所需版本）：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

环境只需创建一次；每次打开新终端需重新激活。
Windows 激活失败或使用 CMD 时，见[故障排查](docs/development.md#windows-故障排查)。

### 2. 安装依赖并运行示例

```bash
python -m pip install -r requirements.txt
python try_ai.py
```

成功时会打印包含 `is_mock: true` 的计划，练习内容为“课堂”和“学习”。
计划生成仍不需要 API Key。

### 3. 自然语言解析（第 3 周 W03-1）

输入一句话看输出 JSON（需要 `.env` 里的真实密钥）：

```bash
python try_parse.py "我是老师，每天练15分钟，想练楷书。"
```

`try_parse.py` 默认走 v2，与 `/parse/v2` 一样返回 `code/message/data`；所有已识别问题合并到 `message`。验证旧版时使用 `python try_parse.py --version v1 "…"`。

只取 JSON、不显示诊断信息：`python try_parse.py "…" 2>/dev/null`。
先离线验证流程、不需要密钥：

```bash
python -m parsing.run_parse --client mock
```

要跑真实模型，把 `.env.example` 复制为 `.env`（默认已填 `MOLING_LLM_MODEL=qwen3.8-flash`）并填入
`DASHSCOPE_API_KEY`，然后：

```bash
python -m parsing.run_parse --client real --tag w03-real
python -m unittest -v test_parse_requirement
```

接 W03-3 的 100 条样本跑评测（dev+val 80 条，封存集不跑）：

```bash
python -m parsing.run_parse --client real --tag w03-3-dev-val \
  --samples ../moling-W03-3/samples_100.jsonl --splits dev,val \
  --out parsing/parse_runs_100.jsonl --report parsing/eval_report.md
```

结果写入 `parsing/parse_runs.jsonl`（当前为 2026-09-20 真实批次，qwen3.8-flash，10 条 9 条符合）；
离线批次保存在 `parsing/parse_runs_mock.jsonl`。细节见[解析说明](docs/parsing.md)。

### 4. 启动调试接口

```bash
python -m uvicorn main:app --reload
```

打开 [接口调试页](http://127.0.0.1:8000/docs)，展开 `POST /plan`，
点击 **Try it out**，填入下面的请求，再点击 **Execute**：

```json
{
  "occupation": "教师",
  "scene": null,
  "style": "楷书",
  "duration_minutes": 15,
  "goal": null,
  "exclusions": [],
  "status": "complete",
  "follow_up": null,
  "errors": []
}
```

预期返回 HTTP 200 和模拟计划；停止服务按 `Ctrl + C`。
完整响应、422 错误说明见[接口文档](docs/api.md)。

在同一个调试页里，`POST /parse` 接收 `{"text": "我是老师，每天练15分钟，想练楷书。"}`，
返回解析后的需求对象；业务状态看响应体的 `status`。

后端追问联调使用 `POST /parse/v2`：后端保存 `session_id` 和对话历史，
每次用户回答后将本次会话的完整用户信息合并为 `text` 传入。解析服务本身无会话状态，
返回 `occupation`、`scene`、`font`（书体名）、`duration_minutes`、`status`；
需要追问时响应体的 `code` 为 400，`message` 是追问句，`data` 为 null。
完成后可把 `data` 提交到 `POST /plan/v2`，计划输出暂沿用 `style` 字段。
详细示例见[接口说明](docs/api.md)。旧 `/parse` 和 `/plan` 继续用于 v1 联调及历史评测。

## 按需阅读

| 文档 | 内容 |
|---|---|
| [接口说明](docs/api.md) | 请求与响应、统一错误格式、生成条件、字格规则 |
| [解析说明](docs/parsing.md) | W03-1：配置、提示词版本、`/parse`、运行记录字段、失败分层、验收证据 |
| [失败样例](parsing/failure_cases.md) | 解析失败层、常见模型瑕疵与本地修复、遗留问题 |
| [开发指南](docs/development.md) | 文件说明、替换生成器、Schema 维护、验证命令、Windows 故障排查 |
| [验证记录与待办](docs/verification.md) | 已验证结果、未验证环境、团队待确认事项、分享包状态 |
