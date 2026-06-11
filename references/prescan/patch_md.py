# -*- coding: utf-8 -*-
import csv

path = r"f:\代码\.claude\skills\xiaotaiyang-teaching-method\references\prescan\filename-stats.md"
csv_path = r"f:\代码\.claude\skills\xiaotaiyang-teaching-method\references\prescan\prescan-raw.csv"
rows = list(csv.DictReader(open(csv_path, encoding="utf-8-sig")))

insert = """## manifest 清单命中（文件可出现在多个清单）

| 清单 | 命中文件数 |
|------|------------|
| keep-34grade | 243 |
| keep-5grade | 110 |
| keep-6grade | 12 |
| reject | 102 |
| preview | 22 |
| 未分类 | 1 |

> 说明：`old_manifest` 列保留全部命中，用 `|` 连接；上表为各清单独立计数（有重叠）。

"""

text = open(path, encoding="utf-8").read()
if "manifest 清单命中" not in text:
    text = text.replace("## 交叉表", insert + "## 交叉表")


def score(r):
    s = 0
    if "无年级前缀" in r["renjiao_hint"]:
        s += 3
    if r["renjiao_hint"].count("|") >= 2:
        s += 2
    if r["content_type"] == "其他":
        s += 3
    if r["old_manifest"] == "未分类":
        s += 4
    if "|" in r["old_manifest"]:
        s += 5
    if len(r["topic_keywords"]) <= 6:
        s += 2
    return s


hard = sorted(rows, key=lambda r: (-score(r), r["filename"]))[:10]
block = "## 最难分类样例 Top 10\n\n"
for r in hard:
    block += (
        f"- **{r['filename']}** — 年级:{r['renjiao_hint']} "
        f"类型:{r['content_type']} manifest:{r['old_manifest']} "
        f"关键词:{r['topic_keywords']}\n\n"
    )

idx = text.find("## 最难分类样例 Top 10")
if idx >= 0:
    text = text[:idx] + block

open(path, "w", encoding="utf-8").write(text)
print("patched")
