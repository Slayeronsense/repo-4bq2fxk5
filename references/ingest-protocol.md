# 小太阳逐字稿 · 入库协议（北师大 12 册）

> **版本**：v3.1（2026-06-10）  
> **用途**：抖音增量 + 未来新字幕蒸馏时，AI 必须读本文件。  
> **正本路径**：`e:\老师skill\xiaotaiyang-teaching-method\`  
> **废弃路径**：`f:\代码\.claude\skills\xiaotaiyang-teaching-method\`（见 `DEPRECATED.md`，勿用）

---

## 1. 三层结构（禁止混用）

| 层级 | 是什么 | 权威文件 | 蒸馏时写什么 |
|------|--------|----------|--------------|
| **索引层** | 视频归哪册 | `grade-semester-index.yaml` + `manifests/manifest-keep-{key}.txt` | 只更新 manifest |
| **方法层** | 讲法操作系统 | `research/01-methods.md`、`03-problem-types.md`、`02-teaching-flow.md` | 新方法/题型增量追加 |
| **证据层** | 逐条适配讲法 | `ingest-registry.yaml` | 含 `adapted_script` + 表征字段 |

**禁止**：模板化空壳 `adapted_script`；按人教单元当主分类；引用废弃路径。

---

## 2. 北师大 12 册命名（唯一标准）

`grade_semester` 一律用显示名（如 `4下`）。manifest key 见 `grade-semester-index.yaml`。

---

## 3. 语料来源

| 库 | 路径 | 条数 |
|----|------|------|
| 小红书 | `f:\xhs_transcripts` | 368 |
| 抖音 | 用户指定目录 | ~1446 |

重建索引：`python e:\老师skill\xiaotaiyang-teaching-method\scripts\rebuild_manifests.py`

---

## 4. 单条蒸馏流水线

```
读逐字稿
  → 定 grade_semester + 安全等级（绿/黄/红）
  → 黄/红：适配（删/降/换超纲内容）
  → 读 13-representation-layer.yaml：判场景 + 判 cra_lesh_mode（见 §5.1）
  → 贴表征标签
  → 写 adapted_script（表征路径 + 7 步脚本，禁止模板占位）
  → 写入 ingest-registry
  → 新方法增量写入 01/03
```

**输出必须是完整讲题脚本**（见 `02-teaching-flow.md`）。

---

## 5. registry 单条 schema

```yaml
- id: XTY-042
  file: f:/逐字稿/.../xxx.md
  source: douyin | xhs
  grade_semester: 4下
  题型: [T05]
  方法: [积的变化规律]

  表征整合:
    场景: 应用题              # 应用题 | 概念课 | 几何画图 | 纯运算
    cra_lesh_mode: 快路径     # 蒸馏语料默认快路径；视频展现新讲法时用慢路径
    cra_path: R → A
    lesh_path: 语言 → 图画 → 符号
    xt_diagram: 线段图
    channel_ref: 无

  讲法证据:
    原句摘录: "..."
    adapted_script: |
      ## 学情边界
      - 可用：… / 禁用：…

      ## 表征路径
      - 场景：应用题
      - 模式：快路径
      - CRA：R → A
      - Lesh：语言 → 图画 → 符号
      - 具体画法（小太阳）：线段图
      - 概念通道（06 库）：无

      ## 题型与方法
      - 题型：T05 …
      - 主方法：积的变化规律

      ## 讲题脚本
      ### 1. 理信息
      【老师说】…（本题情境，非模板）
      【板书/操作】…
      【结构操作】SEP_COND
      【此处易卡】…

      ### 2. 找联系
      【老师说】…
      【板书/操作】…
      【结构操作】RELATED_PROB
      【此处易卡】…

      （3–7 步同上四块格式）

  boundary: ok
```

**Skill 讲题时（Step 0.5）**：

1. 查 registry 相似 `adapted_script`
2. **高相似命中** → 套用 + 学情微调 + **统一为四块格式**（见下），**跳过 A 流程 Step 1–3**
3. **未命中** → 走 A 流程（结构分析→判题型→选方法→7 步脚本）
4. Step 2 仍无匹配 → 生长协议（慢路径）

**旧 registry 条目**：存量多为「### N. + 段落」；Step 4 **运行时转换**为四块（含【结构操作】），不批量回填。新蒸条目直接写四块。

---

## 5.1 蒸馏时如何判定表征字段

读 `research/13-representation-layer.yaml`：

**先判模式**：蒸馏已有视频 → 默认 **快路径**；视频展现 registry/规则库未覆盖的新讲法 → **慢路径**（按 `slow_path_reasoning` 从逐字稿反推）。

| 字段 | 快路径 | 慢路径 |
|------|--------|--------|
| `场景` | `routing` 判应用题/概念课/几何/纯运算 | 同左 |
| `cra_lesh_mode` | 快路径 | 慢路径 |
| `cra_path` | 用 `cra_default`（应用题 R→A） | 从视频讲法反推深度，写明依据 |
| `lesh_path` | 用 `lesh_default`；应用题不从「情境」起步 | 从视频表征互译反推链条 |
| `xt_diagram` | `xt_diagram_rules.trigger` 匹配量+关系 | 由 Lesh「图画」+ 视频实操反推 |
| `channel_ref` | 概念课且 06 有 R06；否则「无」 | 概念课产出 R06 候选或「无」 |

不确定填 `?` + `待审核: [字段名]`。键必须存在。

新方法写入 `01-methods.md` 时补：`cra_stage`、`lesh_from/to`（若适用）、`channel_ref`（概念类）。

**不从视频蒸**：班级错因、Bar Model（已删）、S1–S8（已搁置）。

**Polya**：只从 Wiki `polya-structural-ops.yaml` 读；**不从抖音逐字稿蒸**。Step 4 写入【结构操作】行（op_id 仅该行，不进【老师说】）。

**预习向语料**：与正课同一 schema、同一讲题主流程；manifest 可标 preview 仅作索引，不设单独分支。

---

## 6. 与现有数据

- 已蒸 xhs 368 + 试点条目**暂不回填**（用户挂起）
- 新蒸条目走 v3.1 schema

---

## 7. 蒸馏后检查清单

- [ ] `grade_semester` 用 12 册显示名
- [ ] 黄/红 必有适配后 `adapted_script`
- [ ] 每条含 `表征整合` 六字段（场景 + 模式 + 四表征，允许 `?`）
- [ ] `adapted_script` 含表征路径块，脚本非模板空壳
- [ ] 01/03 增量未覆盖旧条目

---

## 8. 参照索引

| 查什么 | 路径 |
|--------|------|
| 表征整合层 v2.1 | `research/13-representation-layer.yaml` |
| 学情边界 | `f:\代码\教学知识库\课时知识点边界分析\{册}\` |
| 06 概念表征库 | `e:/下学期数学教学_Wiki/wiki/assets/06_概念表征库.md` |
| 波利亚结构操作库 | `e:/下学期数学教学_Wiki/notes/方法卡/polya-structural-ops.yaml` |
| 波利亚反模式 | `e:/下学期数学教学_Wiki/notes/方法卡/polya-anti-patterns.md` |
| 方法/题型 | `research/01-methods.md`、`03-problem-types.md` |

---

## 9. 批量前试点

批量蒸之前先试蒸 5–10 条，验证 schema 通畅、脚本非空壳，再启动批量。
