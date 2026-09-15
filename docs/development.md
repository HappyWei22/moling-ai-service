# 开发指南

[返回 README](../README.md) · [接口说明](api.md) · [开发指南](development.md) · [验证与待办](verification.md)

下列命令均在项目根目录执行，先按 README 创建虚拟环境并安装依赖。

## 文件说明

- schemas.py：需求与计划的数据模型
- ai_service.py：需求检查、可替换生成器入口及输出校验
- plan_generators.py：固定假数据生成器，返回待校验的计划字典
- try_ai.py：直接调用模块的示例
- try_schema.py：旧版单字段校验练习，尚未适配完整需求模型
- requirement_rules.py：生成前检查和 RequirementNotReadyError
- try_requirement.py：需求模型与业务检查练习
- check_examples.py：批量验证 v0.3 的 10 组需求样例
- user_requirement/examples_v0.3.json：当前验证使用的新版样例
- user_requirement/需求字段说明_v0.3.md：新版需求说明；同目录旧版文件仅供历史参考
- main.py：FastAPI 调试入口

## 可替换的计划生成器

`generate_plan(requirement, generator=mock_generate)` 接收结构化的 `UserRequirement`，
默认调用 `plan_generators.py` 中的固定假数据生成器；`POST /plan` 的调用方式不变。
当前不需要 API Key，不进行网络或真实模型调用。

调用流程：需求就绪检查 → 生成器 → `WorksheetPlan.model_validate()` → 输入输出书体、时长一致性检查。
服务层向生成器传入需求的深拷贝，避免生成器修改调用方的原始对象。
现有 5/15/30 分钟限制和非空排除项拒绝规则仍然生效，替换生成器不会绕过这些检查。

生成器约定：同步函数，接收一个 `UserRequirement`，返回完整计划的 Python 字典
（`dict[str, Any]`），字段遵守 WorksheetPlan v0.3。若未来模型返回 JSON 文本，
适配函数需先解析成字典再返回；不要直接返回字符串或协程。

下面的示例可保存为项目目录内的 Python 脚本运行，演示如何替换生成器；它仍然是假数据：

```python
from ai_service import generate_plan
from plan_generators import mock_generate
from schemas import UserRequirement


def demo_generate(requirement):
    data = mock_generate(requirement)
    data["plan_name"] = "替换生成器演示"
    data["items"][0]["text"] = "板书"
    return data


requirement = UserRequirement(
    occupation="教师", scene=None, style="楷书", duration_minutes=15,
    goal=None, exclusions=[], status="complete", follow_up=None, errors=[],
)
plan = generate_plan(requirement, generator=demo_generate)
print(plan.model_dump_json(indent=2))
```

未来实现真实模型函数后，在 Python 调用处传入 `generator=model_generate`。
目前未提供按 HTTP 请求选择模型的参数，也未实现真实模型适配器。
固定或演示数据必须保留 `is_mock=true`。

需求不满足条件时，生成器不会执行，仍通过 `RequirementNotReadyError` 映射为 422。
生成器的非法输出会触发 Pydantic `ValidationError`；书体或时长与输入不符会触发
`ValueError`。生成器调用异常原样向上抛出，属于服务内部失败，不转换为用户输入的 422。
真实模型的超时、重试和对外错误映射后续接入时再补充。

验证命令：`python -m unittest -v test_worksheet_plan`。
新增覆盖替换生成器生效、非法输出拒绝、输入输出约束一致、未就绪时不调用生成器及调用异常传播。

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

## 验证命令

```bash
python -m unittest -v test_worksheet_plan
python check_examples.py
python export_schemas.py --check
```

`check_examples.py` 读取样例的 `expected`，不执行自然语言解析或调用模型。
目前该脚本以打印汇总为准，尚未用非零退出码标记验证失败，请检查是否显示 10/10 通过。
验证结果与环境限制见[验证记录](verification.md)。

## Windows 故障排查

### 不激活虚拟环境运行

如果无法激活，可在项目根目录直接执行：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe try_ai.py
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

验证样例也可使用 `.\.venv\Scripts\python.exe check_examples.py`。

### PowerShell 提示“禁止运行脚本”

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
- 学校或单位的组策略可能优先于此设置；如果仍被阻止，使用上文“不激活虚拟环境运行”的方式即可。

如果只想在当前窗口临时允许，可改用：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

`Process` 设置在关闭窗口后失效。也可以完全不修改执行策略，直接使用虚拟环境中的 Python，示例见上文。

### 使用 Windows CMD

首次使用时创建虚拟环境：

```bat
py -3.12 -m venv .venv
```

每次打开新终端后激活：

```bat
.venv\Scripts\activate.bat
```
