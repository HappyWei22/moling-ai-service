# 接口说明

## 后端追问联调：v2

后端负责生成和保存 `session_id`、保留用户各轮回答，并在每轮回答后调用本服务。
本服务不保存会话；`POST /parse/v2` 只接收合并后的完整用户信息：

```json
{"text": "我是学生。想练楷书。每次练15分钟，用于写作业。"}
```

信息完整时返回 HTTP 200：

```json
{"code": 0, "message": "ok", "data": {"occupation": "学生", "scene": "写作业", "font": "楷书", "duration_minutes": 15, "status": "complete"}}
```

缺少信息、冲突或非法值时仍返回 HTTP 200，但业务 `code` 为 400，`message` 为本轮追问，`data` 为 null。
例如只提供“我是学生”时会一次追问书体和练习时长。v2 模型只提取字段并记录非法值、冲突，不生成 `follow_up`；本地代码沿用 `errors`，补齐 `missing_field`、去重，并把全部问题合并为 `message`。已因非法值或冲突置空的字段不会重复报缺失。职业和场景只需提供一项，两者均缺失时作为一条组合问题提示。内部状态优先级为 `invalid > conflict > needs_clarification`，接口结构保持不变，不对外返回错误列表。只有 `status=complete` 的 `data` 可以提交 `POST /plan/v2`。
`font` 是书体名，仅支持楷书、行书、行楷；计划协议尚使用 `style`，`/plan/v2` 在服务内完成映射。
解析时长只接受 5、15、30 分钟。模型调用、格式、配置失败分别使用 HTTP 502、422、503，区别于业务追问。
后端对外的 `/api/nlp/parse`、`session_id` 和窗口展示由后端实现，此服务的 `/parse/v2` 不创建或保存会话。

以下为保留的 v1 接口说明。

[返回 README](../README.md) · [接口说明](api.md) · [解析说明](parsing.md) · [开发指南](development.md) · [验证与待办](verification.md)

## 请求与响应

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
        "message": "Input should be a valid integer"
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

## 生成条件

`generate_plan()` 当前执行以下前置检查：

- 状态必须为 `complete`。
- `errors` 必须为空。
- 书体和练习时长必须明确。
- 职业、场景、目标至少一项包含非空白文字。

需求模型允许正整数或 `null`，规划入口仅接受 5/15/30 分钟，不自动映射；非空 exclusions 暂时拒绝。字体资源的实际支持情况仍待确认。

## 计划与字格规则

修订资料在 WorkSheetPlan/；原文件在 WorkSheetPlan/history/original-v0.2/，不再用于当前接口。
新 Schema 为 worksheet_plan.schema.json，正常样例为 plans.json，异常测试说明为异常样例.json。
规则详见训练量规则.md。text 每项是一个字或词，repeat 为整项重复次数；仅临摹，instruction 可选。
当前暂定 5/15/30 分钟分别为 12/36/72 个填写字格，不含范字；这只是联调假设，不是经过教学验证的耗时保证。
总格数约束由 Python 校验器执行，纯 JSON Schema 无法覆盖该跨字段规则。

- [需求字段说明](../user_requirement/需求字段说明_v0.3.md)
- [输出 Schema](../WorkSheetPlan/worksheet_plan.schema.json)
- [正常计划样例](../WorkSheetPlan/plans.json)
- [异常样例说明](../WorkSheetPlan/异常样例.json)
- [训练量规则](../WorkSheetPlan/训练量规则.md)
- [协议修改说明与待确认事项](../WorkSheetPlan/修改说明与待确认事项.md)

## 需求解析接口（第 3 周 W03-1）

`POST /parse` 接收 `{"text": "用户原话"}`，返回 `UserRequirement`。
只要文本能解析成协议，一律返回 200，业务状态看响应体的 `status`
（`complete` / `needs_clarification` / `conflict` / `invalid`），响应头带
`X-Moling-Client`、`X-Moling-Model`、`X-Moling-Prompt-Version`。

错误沿用上面的统一格式，码为：`PARSE_FORMAT_ERROR`（422）、
`PARSE_TRANSPORT_ERROR`（502）、`PARSE_CONFIG_ERROR`（503，缺少密钥）。
完整说明、配置与运行记录见[解析说明](parsing.md)。
