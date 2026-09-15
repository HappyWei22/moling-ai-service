# 墨灵 AI 模块

接收结构化的 `UserRequirement`，返回 `WorksheetPlan`，并提供 FastAPI 调试接口。
当前采用 **v0.3 协议修订稿和固定假数据**，已支持替换生成器，尚未接入真实模型。

第一版仅支持临摹和 5/15/30 分钟；非空排除项暂时拒绝。
尚未实现个性化选词、字帖渲染或 AI 评分，协议和暂定字格配额仍待团队确认。

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
当前不需要 API Key。

### 3. 启动调试接口

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

## 按需阅读

| 文档 | 内容 |
|---|---|
| [接口说明](docs/api.md) | 请求与响应、统一错误格式、生成条件、字格规则 |
| [开发指南](docs/development.md) | 文件说明、替换生成器、Schema 维护、验证命令、Windows 故障排查 |
| [验证记录与待办](docs/verification.md) | 已验证结果、未验证环境、团队待确认事项、分享包状态 |
