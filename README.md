# 墨灵 AI 模块

## 当前能力

接收 UserRequirement 对象，返回 WorksheetPlan 对象。
目前使用固定假数据，尚未接入真实大模型。
输入已接入 UserRequirement v0.3 约定及生成前检查。
输出仍为教学版 WorksheetPlan，尚未接入任务三的正式计划协议。
当前不验证模拟内容是否满足书体、场景、目标和排除项，也不包含 AI 评测或打分。

## 文件说明

- schemas.py：需求与计划的数据模型
- ai_service.py：生成计划的核心函数
- try_ai.py：直接调用模块的示例
- try_schema.py：旧版单字段校验练习，尚未适配完整需求模型
- requirement_rules.py：生成前检查和 RequirementNotReadyError
- try_requirement.py：需求模型与业务检查练习
- check_examples.py：批量验证 v0.3 的 10 组需求样例
- user_requirement/examples_v0.3.json：当前验证使用的新版样例
- user_requirement/需求字段说明_v0.3.md：新版需求说明；同目录旧版文件仅供历史参考
- main.py：FastAPI 调试入口

## 环境准备

建议使用 Python 3.12，与当前开发环境保持一致。

先下载项目代码，打开终端并进入项目根目录
（即包含 main.py 的文件夹）。

每台电脑都需要创建自己的虚拟环境，不要复制别人的 .venv 文件夹。


### Windows（PowerShell）

首次使用时创建虚拟环境：

```powershell
py -3.12 -m venv .venv
```

每次打开新终端后激活：

```powershell
.\.venv\Scripts\Activate.ps1
```

#### 如果提示“禁止运行脚本”

部分电脑的 PowerShell 执行策略会阻止运行 `Activate.ps1`；是否遇到此问题取决于电脑配置。
如果激活时报此错误，可以在普通 PowerShell 中执行以下命令，通常不需要管理员权限：

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

如果出现确认提示，输入 `Y` 并回车。然后重新执行：

```powershell
.\.venv\Scripts\Activate.ps1
```

- `CurrentUser`：为当前 Windows 用户保存设置，关闭窗口后仍然生效，通常只需设置一次。
- `RemoteSigned`：允许本地创建的脚本运行，从网上下载的脚本仍可能需要可信签名。
- 此设置适用于当前用户的 PowerShell 脚本，不仅影响本项目。虚拟环境应在本机创建。
- 学校或单位的组策略可能优先于此设置；如果仍被阻止，使用下文“不激活虚拟环境”的方式即可。

如果只想在当前窗口临时允许，可改用：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

`Process` 设置在关闭窗口后失效。也可以完全不修改执行策略，直接使用虚拟环境中的 Python，示例见下文。

### Windows（CMD）

首次使用时创建虚拟环境：

```bat
py -3.12 -m venv .venv
```

每次打开新终端后激活：

```bat
.venv\Scripts\activate.bat
```

### macOS

首次使用时创建虚拟环境：

```bash
python3 -m venv .venv
```

每次打开新终端后激活：

```bash
source .venv/bin/activate
```
## 安装依赖

激活虚拟环境后，首次运行前执行：

```bash
python -m pip install -r requirements.txt
```



## 运行项目

激活虚拟环境后，macOS 和 Windows 均使用以下命令。

直接调用模块：

```bash
python try_ai.py
```

启动调试服务：

```bash
python -m uvicorn main:app --reload
```

浏览器打开 http://127.0.0.1:8000/docs 进行测试。
停止服务：在运行服务的终端中按 Ctrl + C。

### Windows 不激活虚拟环境的运行方式

如果无法激活，可在项目根目录直接执行：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe try_ai.py
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

## 当前接口示例

在文档页通过 `POST /plan` 提交完整需求。所有字段都需要出现，未知值写 `null`，无排除项或错误时使用 `[]`。
旧版只提交 `duration_minutes` 的请求已不适用，会因缺字段返回 422。

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

成功时返回 200，当前固定模拟响应为：

```json
{
  "duration_minutes": 15,
  "is_mock": true,
  "items": [{"text": "教师", "repeat": 3}]
}
```

把请求中的 `occupation` 改为 `null`（场景、目标仍为 `null`），将返回 422：

```json
{
  "detail": {
    "code": "REQUIREMENT_NOT_READY",
    "message": "职业、使用场景、练习目标至少需要明确一项"
  }
}
```

模块通过 `RequirementNotReadyError` 报告需求未就绪；调试入口将其映射为上述 HTTP 响应。
字段缺失或类型错误仍使用 FastAPI 默认的 422 错误列表，与业务错误格式尚未统一。

## UserRequirement v0.3 接入验证

`generate_plan()` 当前执行以下前置检查：

- 状态必须为 `complete`。
- `errors` 必须为空。
- 书体和练习时长必须明确。
- 职业、场景、目标至少一项包含非空白文字。

模型要求时长为正整数或 `null`；目前尚未在规划入口限制为 5/15/30 分钟，也未验证字体资源的实际支持情况。

激活虚拟环境后运行：

```bash
python check_examples.py
```

Windows 不激活环境时运行：

```powershell
.\.venv\Scripts\python.exe check_examples.py
```

2026-09-13 验证结果：10/10 通过。
`UR-01`、`UR-02`、`UR-03`、`UR-07` 返回模拟计划，其余 6 条被正确拦截。
验证读取的是样例的 `expected`，不执行自然语言解析，也不调用模型。
本次覆盖需求结构和生成入口放行/拦截，不代表全部边界条件或个性化计划生成已验证。
当前脚本以打印汇总为准，尚未用非零退出码标记验证失败。

## 环境验证情况

- macOS + Python 3.12.6：此前基础版运行成功；v0.3 接入后已验证上述 10 组样例，以及 HTTP 正常请求 200 和个性化信息缺失请求 422。
- Windows：用户已在自己的 Windows 电脑运行过此前基础版；本轮 v0.3 改动尚未在 Windows 复核。
- 另一名成员独立按 README 运行的验收仍待完成。

## 尚未完成

- 接入正式 WorksheetPlan、训练量规则与输出需求符合性检查。
- 与团队确认错误格式、版本约定及接口契约。
- 提供可替换的模型调用入口。
- 补充更多边界验证并整理旧版练习文件。
- 请另一名成员独立运行并复核本轮版本。
