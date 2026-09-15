# 墨灵 AI 模块

## 当前能力

接收 UserRequirement 对象，返回 WorksheetPlan 对象。
目前使用固定假数据，尚未接入真实大模型。
输入已接入 UserRequirement v0.3 约定及生成前检查。
输出已接入 WorksheetPlan v0.3 修订稿，仅支持临摹，尚待队友复核。
输出书体和时长沿用输入，按暂定字格配额生成固定假数据；尚未实现职业/场景/目标选词，非空排除项暂时拒绝。不包含 AI 评测或打分。

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

成功时返回 200，当前模拟响应示例（plan_id 每次生成不同）：

```json
{
  "schema_version": "0.3",
  "plan_id": "9fe08366-39a8-4072-a52d-f959ef911a38",
  "plan_name": "临摹字帖联调样例",
  "style": "楷书",
  "duration_minutes": 15,
  "is_mock": true,
  "items": [
    {
      "text": "课堂",
      "repeat": 9,
      "task_type": "临摹",
      "instruction": "观察范字，注意字的大小和间距。"
    },
    {
      "text": "学习",
      "repeat": 9,
      "task_type": "临摹",
      "instruction": "观察范字，注意字的大小和间距。"
    }
  ]
}
```

把请求中的 `occupation` 改为 `null`（场景、目标仍为 `null`），将返回 422：

```json
{
  "detail": {
    "code": "REQUIREMENT_NOT_READY",
    "message": "职业、使用场景、练习目标至少需要明确一项",
    "fields": []
  }
}
```

模块通过 `RequirementNotReadyError` 报告需求未就绪；调试入口将其映射为上述 HTTP 响应。
### 统一的 422 错误格式

字段缺失、类型错误、非法值及无法解析的 JSON 均返回 `VALIDATION_ERROR`。
例如把完整请求中的 `duration_minutes` 改为 `"abc"`：

```json
{
  "detail": {
    "code": "VALIDATION_ERROR",
    "message": "请求字段不符合要求",
    "fields": [
      {
        "field": "duration_minutes",
        "message": "Input should be a valid integer, unable to parse string as an integer"
      }
    ]
  }
}
```

两类错误均返回 HTTP 422，统一包含：

- `detail.code`：错误码，供调用方判断错误类型。
- `detail.message`：整体错误说明，供调用方展示。
- `detail.fields`：字段错误列表；需求未就绪时为 `[]`。

字段路径移除开头的 `body`，嵌套位置用点连接（例如 `exclusions.0`）；
请求体整体错误使用 `body`，JSON 解析错误的位置可能是数字偏移。
字段级 `message` 沿用校验库的原始说明，可能为英文；调用方应按 `code` 分支，不要依赖说明文字。
响应不回传校验库的原始 `input` 或 `ctx`。`/docs` 的 422 响应模型也已同步。
此约定覆盖请求校验和需求未就绪，不将服务内部错误或输出校验失败伪装成 422。

**调用方迁移**：旧版字段错误的 `detail` 是列表，现在统一为对象；
请改为读取 `detail.message`，字段明细读取 `detail.fields`。

## UserRequirement v0.3 接入验证

`generate_plan()` 当前执行以下前置检查：

- 状态必须为 `complete`。
- `errors` 必须为空。
- 书体和练习时长必须明确。
- 职业、场景、目标至少一项包含非空白文字。

需求模型允许正整数或 `null`，规划入口仅接受 5/15/30 分钟，不自动映射；非空 exclusions 暂时拒绝。字体资源的实际支持情况仍待确认。

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

- 复核 WorksheetPlan v0.3 修订稿并实练校准字格配额；接入真实候选内容及排除过滤。
- 与团队确认错误格式、版本约定及接口契约。
- 提供可替换的模型调用入口。
- 补充更多边界验证并整理旧版练习文件。
- 请另一名成员独立运行并复核本轮版本。

## WorksheetPlan v0.3 修订与验证

修订资料在 WorkSheetPlan/；原文件在 WorkSheetPlan/history/original-v0.2/，不再用于当前接口。
新 Schema 为 worksheet_plan.schema.json，正常样例为 plans.json，异常测试说明为异常样例.json。
规则详见训练量规则.md。text 每项是一个字或词，repeat 为整项重复次数；仅临摹，instruction 可选。
当前暂定 5/15/30 分钟分别为 12/36/72 个填写字格，不含范字；这只是联调假设，不是经过教学验证的耗时保证。
总格数约束由 Python 校验器执行，纯 JSON Schema 无法覆盖该跨字段规则。

```bash
python -m unittest -v test_worksheet_plan
python check_examples.py
```

本轮本机验证：5 个输出测试方法（含多种边界子案例）通过，原 10 组需求样例仍全部通过。
另检查了调试路由函数的正常返回、20 分钟的 422 映射及 OpenAPI 生成；未重新进行真实浏览器 HTTP 或 Windows 验证。
本轮未更新分享 ZIP，旧 ZIP 不包含这些修改。

## 维护输出 JSON Schema

以 schemas.py 的 WorksheetPlan / WorksheetItem 为唯一生成来源，不直接修改导出的 JSON。
模型中声明了 JSON Schema 2020-12 标准版本、模型说明和各字段的中文名称与解释。
$schema 是格式标准版本，schema_version 是业务协议版本；$defs 存放复用结构，$ref 引用它。

修改模型后运行（已激活虚拟环境，Windows/macOS 相同）：

```bash
python export_schemas.py
python export_schemas.py --check
```

第一条只更新 WorkSheetPlan/worksheet_plan.schema.json，不覆盖同学一的原始协议或历史文件。
第二条不写文件，若导出内容过期则以非零状态退出。无需安装新依赖。
字段展示名称、description 和 $comment 仅为说明；字格总量等 Python 业务校验仍需执行，不能只依赖 JSON Schema。
