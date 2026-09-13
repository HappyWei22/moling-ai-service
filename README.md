# 墨灵 AI 模块

## 当前能力

接收 UserRequirement 对象，返回 WorksheetPlan 对象。
目前使用固定假数据，尚未接入真实大模型。
字段为假字段，待与任务一、任务三对齐。

## 文件说明

- schemas.py：需求与计划的数据模型
- ai_service.py：生成计划的核心函数
- try_ai.py：直接调用模块的示例
- try_schema.py：需求校验练习
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

## 环境验证情况

- macOS + Python 3.12.6：已运行并完成四种接口请求验证。
- Windows：已提供运行说明，尚待队友实际验证。

## 已完成的手动验证

| 请求正文 | 状态码 | 结果 |
|---|---|---|
| {"duration_minutes": 15} | 200 | 返回模拟计划 |
| {"duration_minutes": -5} | 422 | greater_than |
| {} | 422 | missing |
| {"duration_minutes": "十五分钟"} | 422 | int_parsing |

## 尚未完成

- 对齐正式 UserRequirement 和 WorksheetPlan
- 明确模块错误约定与 HTTP 错误映射
- 提供可替换的模型调用入口
- 补充全新环境安装说明与依赖清单
- 请另一名成员独立运行并复核