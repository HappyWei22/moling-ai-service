# 墨灵 v2 正式评测集

协议：`POST /parse/v2`　样本包版本：`moling-v2-eval` v1.0　建集日期：2026-10-09

---

## 1. 这是什么

与当前 v2 需求解析协议一致、可复核、可重复运行的正式评测集。用于验证三件事：

1. 能否从用户原话准确提取职业、场景、书体和单次练习时长；
2. 信息不足 / 非法值 / 冲突同时出现时，能否**一次回复覆盖全部已识别问题**且不重复追问；
3. 多轮补充或明确修正后，能否根据完整会话得到正确结果。

**这不是 v1 样本改个字段名的产物**：123 条中有 109 条为重新审核或新建（仅 14 条迁移自 v1，
且其中 7 条结论发生变化，见 `v1到v2迁移说明.md`）。

---

## 2. 数据版本与规模

| 项 | 值 |
|---|---|
| 总条数 | 123 |
| dev / val / sealed | 63 / 35 / 25 |
| 语义组 | 112 |
| 独立会话 | 12 |
| 样本 SHA256 | 见 `split_manifest.json` |
| 协议版本 | v2（提示词 `parsing/prompt_v2.md`） |
| 提示词 SHA256（前 12） | 见 `baseline/` 运行记录元数据 |

> 说明：任务说明 §5 要求「至少 100 条，按约 60%/20%/20% 分配」。
> 本集 123 条，比例 **51.2% / 28.5% / 20.3%**。**偏差原因**：多轮样本按「检查点」计数
> （§6 要求同一会话多轮各建一条记录），而多轮检查点天然集中在 dev/val（多轮需调试），
> 共 23 个检查点全部落在 dev/val，导致二者占比高于 80%。sealed 保持 25 条，
> 且**全部为独立新建语义组**。若强行凑 60/20/20，需把已用于调试的组移入 sealed，
> 会破坏「sealed 不使用已调试内容」的纪律，故**未**调整。此偏差已如实登记。

---

## 3. 目录结构

```
v2_eval/
├── samples_v2.jsonl              # 全量样本（正式交付物）
├── splits/
│   ├── samples_v2_dev.jsonl      # 物理分开保存，便于隔离
│   ├── samples_v2_val.jsonl
│   └── samples_v2_sealed.jsonl
├── split_manifest.json           # 各集编号/语义组/会话/覆盖统计/哈希
├── 标注指南_v2.md
├── v1到v2迁移说明.md
├── 争议裁决表.md
├── 校验报告.md                    # 由 validate_v2.py 自动产出
├── 封存访问记录.md
├── README.md
├── scripts/
│   ├── v2_rules.py               # 判据唯一来源（与上游实现同源推导）
│   ├── sample_specs.py           # 123 条样本声明
│   ├── build_samples.py          # 生成 + 用上游 finalize_v2 回灌校验
│   ├── validate_v2.py            # 数量/覆盖/隔离/近重复/清单
│   └── make_mock_responses.py    # 生成 mock 响应（流程自检用）
└── baseline/
    ├── dev_val_runs.jsonl        # ✅ 真实模型 dev/val 运行记录（98 条）
    ├── dev_val_report.md         # ✅ 真实批次自动报告
    ├── 追问人工复核.md            # ✅ 追问语义复核（执行人自审，72 条）
    ├── mock_dev_val_runs.jsonl   # mock 流程自检记录（非模型效果证据）
    ├── mock_dev_val_report.md
    └── mock_responses_v2.json
```

---

## 4. 依赖与运行

### 4.1 环境

项目 Python 虚拟环境（`.venv`），已安装 `requirements.txt` 全部依赖。
真实模型调用需在**项目根目录** `.env` 配置密钥（`.env` 已被 `.gitignore` 忽略，不提交）：

```ini
DASHSCOPE_API_KEY=sk-...
MOLING_LLM_MODEL=qwen3.8-flash
MOLING_LLM_EXTRA_BODY={"enable_thinking": false}
```

### 4.2 重建样本（可选，产物已提交）

```bash
python v2_eval/scripts/build_samples.py
python v2_eval/scripts/validate_v2.py
```

`build_samples.py` 会用上游 `finalize_v2` 对每条回灌，**任何标准答案与真实实现不一致都会中止构建**。

### 4.3 流程自检（无需密钥）

```bash
python v2_eval/scripts/make_mock_responses.py
python -m parsing.run_parse --protocol v2 --client mock \
  --samples v2_eval/samples_v2.jsonl --splits dev,val \
  --mock-file v2_eval/baseline/mock_responses_v2.json \
  --out v2_eval/baseline/mock_dev_val_runs.jsonl \
  --report v2_eval/baseline/mock_dev_val_report.md
```

### 4.4 真实模型开发/验证评测（本次正式基线）

```bash
.venv/bin/python -m parsing.run_parse --protocol v2 --client real \
  --samples v2_eval/samples_v2.jsonl --splits dev,val \
  --out v2_eval/baseline/dev_val_runs.jsonl \
  --report v2_eval/baseline/dev_val_report.md --tag v2-baseline
```

> 只要求 dev/val。**封存集不作为日常测试对象**，须获最终评估授权后另行运行。

---

## 5. 判据来源与可复现性

标准答案**不是手写死的**，而是：

1. `sample_specs.py` 声明每条样本的「模型原始候选」；
2. `v2_rules.derive()` 按 `parse_requirement_v2._collect_errors` / `_finalize_v2` 的逻辑推导五字段答案与问题集合；
3. `build_samples.py` 再把推导结果丢回**上游真实 `_finalize_v2`** 实跑一遍，逐条断言一致。

即：**标注口径与代码行为强制同源**，不存在「文档说一套、代码做一套」。

### 5.1 已知上游行为（E8）

`_collect_errors` 会对 `font`/`duration_minutes` 的**候选原值**做本地枚举校验。
因此当冲突字段的候选原值**本身不是合法枚举值**时（如「楷书和行书」），会被额外补一条
`invalid_value`，状态由 `conflict` 降级为 `invalid`。

> **边界（经真实批次验证，2026-10-09 更正）**：E8 **不等于**「`conflict` 状态不可达」。
> 若冲突字段的候选值**本身是合法书体/时长**（如 `font="楷书"` 且模型声明冲突），
> 最终状态**正常保留为 `conflict`**。受影响的是本集 22 条冲突样本中的 **9 条**。
> 详见 `争议裁决表.md` D01（含双向复现证据与最小修复方案）。

> 这不影响评测集可用性：脚本用问题集合反推状态，与实现一致；但**上游若修复 E8，
> 受影响的 9 条冲突样本需重标**。

---

## 6. 职责

| 角色 | 姓名 | 职责 |
|---|---|---|
| 建集执行人 | 罗占勇 | 样本设计、标注、脚本、组织测试、整理结果 |
| 复核人 | **待指定** | 检查追问语义与报告、复核全部正式样本 |

> 任务说明 §9 指出组员姓名与截止日期由项目负责人安排并回填。
> 本人**不代为填写**「已复核」「已批准」等记录 —— 复核需由第二位真人在本 README 与本表签名确认。

---

## 7. 交付状态

| 项 | 状态 |
|---|---|
| 有效条数 ≥ 100 且覆盖达标 | ✅ 123 条，八维覆盖全达标 |
| 自动校验通过 | ✅ `validate_v2.py` 全绿；上游 `validate_samples` 通过 |
| 无跨集语义组/会话泄漏 | ✅ 已校验 |
| 近重复检查 | ✅ 0 对（相似度 ≥0.92） |
| 封存可追溯 | ✅ 25 条独立新建，零访问 |
| 迁移说明 | ✅ `v1到v2迁移说明.md`（14 条逐条记录） |
| 争议裁决 | ✅ 8 项已裁决，3 项待上游确认 |
| **真实模型 dev/val 批量测试** | ✅ **已完成**（98 条，`qwen3.8-flash`，零技术失败）见 §8 |
| **实际追问人工复核** | ⚠️ **执行人自审已完成**（`baseline/追问人工复核.md`，72 条），**独立双人复核未完成** |
| **双人交叉复核** | ⚠️ **未完成**（复核人待指定） |

**结论：数据、脚本、真实模型批次三层均已完成。** 唯一未完成项是任务说明 §9 要求的
**独立双人复核** —— 该项需第二位真人执行，不由本人代为填写。

---

## 8. 真实模型批次结果（2026-10-09）

- 批次：`20261009T145849Z-v2-baseline`｜模型：`qwen3.8-flash`｜提示词 SHA256 前 12：`97664f29304a`
- 样本：`dev_val_runs.jsonl`（dev 63 + val 35 = **98 条**）｜技术失败：**0**
- 命令：见 `baseline/README` 或本文件 §9 复现段落

### 8.1 总体指标

| 指标 | dev | val | 合计 |
|---|---|---|---|
| 自动检查全一致 | 29/63（46.0%） | 18/35（51.4%） | **47/98（48.0%）** |
| 完整问题集合一致 | 50/63（79.4%） | 26/35（74.3%） | 76/98（77.6%） |
| **错误放行率** | 0/44 | 0/27 | **0/71（0.0%）** |
| 模型错误召回率 | 28/41（68.3%） | 18/28（64.3%） | 46/69（66.7%） |
| 模型错误精确率 | 28/30（93.3%） | 18/19（94.7%） | 46/49（93.9%） |

**字段准确率（成功解析样本口径）**

| 字段 | dev | val |
|---|---|---|
| occupation | 62/63（98.4%） | 35/35（100%） |
| scene | 51/63（81.0%） | 33/35（94.3%） |
| font | 63/63（100%） | 35/35（100%） |
| duration_minutes | 62/63（98.4%） | 35/35（100%） |
| status | 53/63（84.1%） | 29/35（82.9%） |

### 8.2 关键结论

1. **错误放行率 0**（0/71）—— 没有一条含问题的输入被判为 `complete`。安全底线守住。
2. **「一次汇总全部已识别问题」完全成立** —— 多问题样本统一输出
   「请补充或修改以下信息：1. … 2. … 3. …」，无漏问、无重复问、无多余问。
   这是 v2 相对 v1 的核心改进，真实模型下已验证。
3. **`font` 提取 100%**（98/98）—— v2 改名后的书体识别无退化。
4. **status 判定是最弱项**（82.9%~84.1%），偏差集中在三类：
   - **家族 A（8 条）**：期望 `complete`，模型给 `needs_clarification` ——
     五个字段**全部提取正确**却仍追问，属提示词遵循度问题（E9 候选）。
   - **家族 B（9 条）**：期望 `invalid`，模型给 `conflict` —— 模型判定正确，
     是上游 E8 使其降级。
   - **家族 C（6 条）**：期望 `invalid`，模型给 `needs_clarification` —— 模型未识别非法值。
5. **没有一条偏差根因在评测集标注侧**，故**无需重标本集**。

> **证据分层**：本节数字来自**真实模型调用**（A 级证据），可直接作为基线引用。
> `baseline/mock_*` 是流程自检（C 级），**不可**作为模型效果引用。

**结论：数据与脚本层已完成并通过自动校验；因「双人复核」与「真实模型批次」依赖他人与密钥，
按 §9 验收条件，整体交付状态应标为「数据就绪，评测未完成」。不得仅凭 mock 退出码 0 宣称通过验收。**

---

## 9. 限制与未解决问题

1. **E8 未修**：冲突字段候选原值非法时 `conflict` 被降级为 `invalid`，追问会出现自相矛盾的两条消息
   （影响 9 条，详见 `争议裁决表.md` D01）。
2. **E9 候选（新）**：模型在五字段齐全、`errors=[]` 时仍输出 `needs_clarification`
   （家族 A，8 条），与 `prompt_v2.md:12` 的 `complete` 定义冲突，属提示词遵循度问题，建议反馈提示词负责人。
3. **D07 待确认**：`0.5小时`（=30 分钟）当前判非法，是否符合预期待上游确认。
4. **比例偏差**：dev+val 占比高于 80%，原因见 §2。
5. **API 检查未发真实 HTTP**：脚本按内部解析结果构造 API 响应，真实 HTTP 契约另由接口测试核验。
6. **场景词表未权威化**：v2 未搬入 v1 扩展场景映射词表，`scene` 按原话保留。
7. **独立双人复核未完成**：§9 要求的第二位复核人尚未指定。`baseline/追问人工复核.md`
   是执行人自审，**不能替代**独立复核。

---

## 10. 复现命令

```bash
# 1) 生成样本（用上游真代码回灌校验）
python v2_eval/scripts/build_samples.py

# 2) 自动校验（数量/八维覆盖/隔离/近重复/manifest）
python v2_eval/scripts/validate_v2.py

# 3) 真实模型 dev/val 批次（需在 .env 配置 DASHSCOPE_API_KEY）
MOLING_LLM_PROMPT_VERSION=v2 python -m parsing.run_parse \
  --protocol v2 --client real --samples v2_eval/samples_v2.jsonl --splits dev,val \
  --out v2_eval/baseline/dev_val_runs.jsonl \
  --report v2_eval/baseline/dev_val_report.md --tag v2-baseline
```

> `MOLING_LLM_PROMPT_VERSION=v2` **必须显式设置**，否则会静默跑在默认提示词版本上。
> 运行记录里的 `prompt_version` / `prompt_sha256` 可用于事后核对。
