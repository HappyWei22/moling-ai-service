# 验证记录与待确认事项

[返回 README](../README.md) · [接口说明](api.md) · [解析说明](parsing.md) · [开发指南](development.md) · [验证与待办](verification.md)

## 2026-09-20：第 3 周 W03-1 需求解析

- `python -m unittest -v test_parse_requirement`：24 个测试方法全部通过（离线，不联网、不需要密钥）。
  覆盖代码围栏/前后文字抽取、非法时长与不支持书体的修复、状态与字段不一致的重判、
  别名规范化、失败分层（config / transport / format）、请求体不含密钥、mock 批次写盘。
- `python -m parsing.run_parse --client mock`：第 2 周 10 组样例 10/10 与人工期望一致，
  状态覆盖 complete 4、needs_clarification 3、conflict 1、invalid 2，结果在 `parsing/parse_runs_mock.jsonl`。
- `main.py` 新增 `POST /parse`，应用可正常导入且导入时不要求密钥；`/docs` 中可见 `/parse`。
- 真实接口连通性：无效密钥返回 HTTP 401 `invalid_api_key`；账号欠费期间返回 HTTP 400 `Arrearage`
  （`GET /models` 仍正常，六个模型全部同一错误，确认是账号计费问题而非模型名或请求格式）。
  两者都被正确分类为 `ParseTransportError` 并保留原始报错。恢复额度后 `qwen3.8-flash` 调用成功。
- **真实批次（2026-09-20，qwen3.8-flash，temperature 0，enable_thinking=false，批次 `20260920T085924Z-w03-real`）**：
  `python -m parsing.run_parse --client real --tag w03-real` → **10 条中 9 条与人工期望一致**，
  结果在 `parsing/parse_runs.jsonl`（`mock=false`、`model=qwen3.8-flash`、提示词 v0 sha256 `79d2b88b5c00`、
  单次调用、`usage_missing=false`、耗时 2088–3574 ms，中位 2597 ms，单条 total_tokens 1585–1632）。
  连跑两次结果一致。完成状态 4、需要追问 3、冲突 1、非法 2；`format` 层零失败。
- 真实批次的两条发现：
  1. **唯一不符合项是标注口径争议**：UR-03「我想改善字的工整度…」模型输出 `goal="改善字的工整度"`，
     人工期望 `"改善工整度"`。模型照抄原话、未违反“不补造”，需由 W03-3 裁决口径，暂不改 Prompt。
  2. **模型自报状态不可信**：UR-07「我是学生，想练行书，每天15分钟。」字段齐全，模型误报
     `needs_clarification`，被本地 `finalize_requirement()` 纠正为 `complete` 并清空追问（1/10 条）。
     该发现说明本地收敛是必需环节，也提示第 4 周字段评估要单列“状态判定”。

## 2026-09-15：当前代码验证

- 可替换生成器改动后：10 个测试方法通过，覆盖原有规则、替换生成器生效、非法输出拒绝、书体/时长一致性、未就绪时不调用生成器及调用异常传播。
- 10 组需求样例通过；UR-01、UR-02、UR-03、UR-07 返回模拟计划，其余 6 条被正确拦截。
- `export_schemas.py --check` 通过，输出 Schema 与模型一致。
- `try_ai.py` 正常生成模拟计划。
- 统一错误格式改动后、生成器拆分前：通过 ASGI 应用层验证了正常请求、类型错误、缺失字段、非法值、需求未就绪、不支持时长、非法 JSON 共 7 种场景，OpenAPI 422 模型检查通过。这不是浏览器或真实网络端口测试。

以上不代表真实模型、个性化选词、字帖渲染或教学效果已经验证。
2026-09-15 打包前再次运行：10 个测试方法、10 组需求样例及 Schema 一致性检查全部通过。

## 历史验证与环境边界

- 2026-09-13：需求样例 10/10 通过；输出协议初版的 5 个测试方法通过。当前测试数量已更新为上面的 10 个。
- 旧 README 记录：macOS + Python 3.12.6 基础版运行成功，v0.3 接入后正常 HTTP 请求为 200、个性化信息缺失请求为 422。
- 旧 README 记录：用户在自己的 Windows 电脑运行过基础版；当前 v0.3 及后续改动尚未在 Windows 复核。
- 另一名成员独立按 README 运行当前版本的验收仍待完成。

## 待完成与团队确认

- 复核 WorksheetPlan v0.3 修订稿并实练校准字格配额；接入真实候选内容及排除过滤。
- 与团队确认错误格式、版本约定及接口契约。
- 接入真实模型生成器及其配置、超时和调用错误处理；可替换入口已完成。
- W03-1 解析：真实批次已跑（qwen3.8-flash，9/10），失败与观察已补进 `parsing/failure_cases.md`；
  待 W03-3 裁决 UR-03 的 `goal` 口径，并在 100 条标注完成后换 `--samples` 重跑；重试与脱敏日志由 W03-4 接。
- 补充更多边界验证并整理旧版练习文件。
- 请另一名成员独立运行并复核本轮版本。

## 分享包状态

2026-09-15 交付包：`moling-ai-service-v0.3-20260915.zip`，包含统一错误格式、可替换生成器和拆分后的文档。
包内不含 Git 历史、虚拟环境或本地密钥。旧分享包不能代表当前版本。
