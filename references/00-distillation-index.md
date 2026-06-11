# 小太阳老师 · 讲题方法蒸馏索引

> 状态：方法库蒸馏完成；**manifest 已按北师大 12 册统一重建**（2026-06）。

## 素材清单（唯一入口）

| 文件 | 数量 | 用途 |
|------|------|------|
| `manifests/manifest-keep-{1shang…6xia}.txt` | **315** keep | 按北师大 12 册分册 |
| `manifests/manifest-reject.txt` | **19** | 非教学（vlog/思想工作等） |
| `manifests/manifest-preview.txt` | **34** | 预习课仅参考 |

| 来源 | 根目录 | 条数 | manifest |
|------|--------|------|----------|
| 小红书 | `f:\xhs_transcripts` | 368（315 keep） | `manifest-keep-{key}.txt` |
| 抖音 | `f:\逐字稿\抖音音频逐字稿转完` | 1446（试点中） | `manifest-keep-douyin-{key}.txt` |

去重：`f:\逐字稿\去重记录.json`（159 条与 xhs 重复已删）

重建 xhs 索引命令：

```bash
python e:/老师skill/xiaotaiyang-teaching-method/scripts/rebuild_manifests.py
```

年级册索引：`grade-semester-index.yaml`  
蒸馏入库协议（1446 条必读）：`ingest-protocol.md`  
讲法证据库：`ingest-registry.yaml`（v0.1-pilot，抖音增量写入）  
抖音预扫试点：`prescan/prescan-douyin-pilot.csv`、`prescan/douyin-pilot-batch0.md`

## 各册条数（2026-06 重建）

| 册 | 条数 |
|----|------|
| 1上–2上 | 0 |
| 2下 | 1 |
| 3上 | 0 |
| 3下 | 8 |
| 4上 | 130 |
| 4下 | 80 |
| 5上 | 83 |
| 5下 | 1 |
| 6上 | 12 |
| 6下 | 0 |

无前缀文件经 **内容审查**（读字幕+主题词+人教错位规则）自动归类；详见 `prescan/manifest-full.csv`。

## 蒸馏范围

- **博主**：小太阳老师
- **年级**：1上–6下（语料集中在 3下–5上）
- **教材锚定**：北师大版；人教字幕只借讲法
- **学情**：`教学知识库/课时知识点边界分析/{3下,4上,4下}/`（其余册待建）

## Skill 调用流程

```
输入：题目 + 年级册（1上–6下）+ 学完第几单元
  → Step 0  学情边界（boundary YAML / 05-grade-boundaries）
  → Step 0.5 查 ingest-registry（高相似 → 套用 adapted_script → Step 4）
  → Step 1–3  A 流程（未高相似命中时：结构分析→判题型→选方法）
  → Step 4  7 步讲题脚本（每步四块：老师说/板书操作/结构操作/此处易卡）
  → Step 5  生长复盘（陌生题 / 新方法卡候选）
```

表征整合：`research/13-representation-layer.yaml`  
波利亚结构操作：`e:/下学期数学教学_Wiki/notes/方法卡/polya-structural-ops.yaml`（Step 4【结构操作】行，不从逐字稿蒸）

## 方法库文件

| 文件 | 内容 |
|------|------|
| `research/01-methods.md` | ~60 方法 |
| `research/03-problem-types.md` | T01–T31 + G5 + G6 |
| `research/05-grade-boundaries.md` | 学情边界 |
| `research/02-teaching-flow.md` | 7 步节奏 + **四块**讲题脚本模板 |
| `research/13-representation-layer.yaml` | 表征整合层 v2.1 |
| `duizhao/duizhao-rules-4xia.yaml` | 四下人教→北师大对照规则 |
