# -*- coding: utf-8 -*-
import os
import re
import csv
from collections import Counter, defaultdict

TRANSCRIPT_DIR = r"f:\xhs_transcripts"
REF = r"f:\代码\.claude\skills\xiaotaiyang-teaching-method\references"
OUT_DIR = os.path.join(REF, "prescan")

MANIFESTS = {
    # 12 册统一入口（见 grade-semester-index.yaml）
    "reject": "manifests/manifest-reject.txt",
    "preview": "manifests/manifest-preview.txt",
}

def load_manifest(path):
    names = set()
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # strip optional path prefix
            base = os.path.basename(line)
            names.add(base)
            names.add(line)
    return names

def extract_topic_keywords(name):
    stem = name[:-4] if name.endswith(".txt") else name
    # remove trailing id suffix _hex
    stem = re.sub(r"_[0-9a-f]{16,}$", "", stem, flags=re.I)
    # take part before first _ if title is before id
    if "_" in stem:
        title = stem.split("_", 1)[0]
    else:
        title = stem
    # clean hashtags fragments for keywords
    title = re.sub(r"#\S+", "", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title[:120]

def renjiao_hints(filename):
    hints = []
    f = filename

    def add(h):
        if h not in hints:
            hints.append(h)

    # explicit prefixes with hyphen
    prefix_map = [
        ("三下-", "三下"), ("四上-", "四上"), ("四下-", "四下"),
        ("五上-", "五上"), ("五下-", "五下"), ("六上-", "六上"), ("六下-", "六下"),
    ]
    for pref, tag in prefix_map:
        if f.startswith(pref):
            add(tag)

    # 四上/四下 without hyphen at start
    if f.startswith("四上") and "四上" not in hints:
        add("四上")
    if f.startswith("四下") and "四下" not in hints:
        add("四下")
    if f.startswith("五上") and "五上" not in hints:
        add("五上")
    if f.startswith("五下") and "五下" not in hints:
        add("五下")
    if f.startswith("六上") and "六上" not in hints:
        add("六上")
    if f.startswith("六下") and "六下" not in hints:
        add("六下")
    if f.startswith("三下") and "三下" not in hints:
        add("三下")

    if "四升五预习" in f:
        add("四升五预习")
    if "寒假预习" in f or re.search(r"三年级寒假预习|四年级寒假预习|五年级寒假预习|六年级寒假预习", f):
        add("寒假预习")
    elif "寒假" in f and "预习" in f:
        add("寒假预习")

    # inline grade mentions (secondary, only if no structural prefix)
    grade_patterns = [
        (r"三年级|三下", "三下"),
        (r"四年级上|四上", "四上"),
        (r"四年级下|四下", "四下"),
        (r"五年级上|五上", "五上"),
        (r"五年级下|五下", "五下"),
        (r"六年级上|六上", "六上"),
        (r"六年级下|六下", "六下"),
    ]
    structural = hints and hints[0] not in ("四升五预习", "寒假预习")
    if not structural:
        for pat, tag in grade_patterns:
            if re.search(pat, f) and tag not in hints:
                add(tag)

    core_grade_tags = {"三下", "四上", "四下", "五上", "五下", "六上", "六下"}
    if not (set(hints) & core_grade_tags):
        add("无年级前缀")

    return "|".join(hints)

def content_type(filename):
    f = filename
    types = []

    def pick(t):
        if t not in types:
            types.append(t)

    if re.search(r"vlog|Vlog|日常|图书馆|颁奖|顺顺|开学第一天|二楼|生活", f):
        pick("vlog生活")
    if "期末复习" in f or "期末试卷" in f or "期末考前" in f or "期末注" in f:
        pick("期末复习")
    if "预习" in f and "寒假预习" not in f and "四升五预习" not in f:
        # 寒假/四升五 handled as renjiao; still 预习 content
        if "预习" in f:
            pick("预习")
    if "寒假预习" in f or "四升五预习" in f or re.search(r"预习\d", f):
        pick("预习")
    if re.search(r"思维拓展|思维训练|易错题|种子题|思想工|拓展题|黄金档", f):
        pick("思维拓展")
    if re.search(r"第[一二三四五六七八九十\d]+单元|单元-|课时|认识|探索|解决问题|竖式|口算|面积|方程|分数|小数|三角形|四边形|观察物体|统计|平均数", f):
        pick("教学")

    # default teaching for typical math titles without other signals
    if not types:
        if re.search(r"小学数学|数学题|易错题|竖式|计算|应用题|#", f):
            pick("教学")
        elif f.startswith("shunshun") or "30天挑战" in f:
            pick("vlog生活")
        else:
            pick("其他")
    elif "教学" not in types and not set(types) & {"vlog生活"}:
        # mixed: if looks like lesson and has 思维
        if re.search(r"单元|认识|探索|竖式|应用题|小学数学", f):
            pick("教学")

    return "|".join(types)

def manifest_label(filename, manifest_sets):
    hits = []
    for label, names in manifest_sets.items():
        if filename in names:
            hits.append(label)
    if not hits:
        return "未分类"
    return "|".join(hits)

def ambiguity_score(row):
    """Higher = harder to classify."""
    score = 0
    rh = row["renjiao_hint"]
    if "无年级前缀" in rh:
        score += 3
    if rh.count("|") >= 2:
        score += 2
    ct = row["content_type"]
    if ct.count("|") >= 2:
        score += 1
    if ct == "其他":
        score += 3
    if row["old_manifest"] == "未分类":
        score += 2
    if row["old_manifest"].count("|") > 1:
        score += 5
    # short/generic titles
    kw = row["topic_keywords"]
    if len(kw) <= 8:
        score += 1
    return score

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    manifest_sets = {}
    for label, fn in MANIFESTS.items():
        manifest_sets[label] = load_manifest(os.path.join(REF, fn))

    all_manifest_names = set()
    for s in manifest_sets.values():
        all_manifest_names |= s

    files = sorted([f for f in os.listdir(TRANSCRIPT_DIR) if f.lower().endswith(".txt")])

    rows = []
    for fn in files:
        rows.append({
            "filename": fn,
            "renjiao_hint": renjiao_hints(fn),
            "content_type": content_type(fn),
            "old_manifest": manifest_label(fn, manifest_sets),
            "topic_keywords": extract_topic_keywords(fn),
        })

    # stats
    total = len(rows)
    hint_counter = Counter()
    no_prefix = 0
    for r in rows:
        parts = r["renjiao_hint"].split("|")
        if "无年级前缀" in parts:
            no_prefix += 1
        for p in parts:
            hint_counter[p] += 1

    content_counter = Counter()
    for r in rows:
        for p in r["content_type"].split("|"):
            content_counter[p] += 1

    manifest_counter = Counter(r["old_manifest"] for r in rows)
    simple_manifest = Counter()
    for r in rows:
        sm = r["old_manifest"].split("|")[0] if "|" not in r["old_manifest"] else r["old_manifest"]
        simple_manifest[r["old_manifest"]] += 1

    # cross tab: renjiao primary grade vs manifest
    grade_tags = ["三下", "四上", "四下", "五上", "五下", "六上", "六下", "寒假预习", "四升五预习", "无年级前缀"]
    cross = defaultdict(lambda: Counter())
    for r in rows:
        hints = r["renjiao_hint"].split("|")
        primary = hints[0]
        cross[primary][r["old_manifest"]] += 1

    reject_count = sum(1 for r in rows if "reject" in r["old_manifest"].split("|"))

    # hardest 10
    scored = sorted(rows, key=lambda r: (-ambiguity_score(r), r["filename"]))
    hardest = scored[:10]

    csv_path = os.path.join(OUT_DIR, "prescan-raw.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["filename", "renjiao_hint", "content_type", "old_manifest", "topic_keywords"])
        w.writeheader()
        w.writerows(rows)

    md_path = os.path.join(OUT_DIR, "filename-stats.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# xhs_transcripts 文件名预扫描统计\n\n")
        f.write(f"- **扫描目录**: `{TRANSCRIPT_DIR}`\n")
        f.write(f"- **.txt 总数**: {total}\n")
        f.write(f"- **无年级前缀**: {no_prefix}\n")
        f.write(f"- **manifest-reject 命中**: {reject_count}\n")
        f.write(f"- **manifest 未分类**: {manifest_counter.get('未分类', 0)}\n\n")

        f.write("## 人教/年级线索（可多标签，按标签计数）\n\n")
        f.write("| 标签 | 数量 |\n|------|------|\n")
        for tag in grade_tags:
            f.write(f"| {tag} | {hint_counter.get(tag, 0)} |\n")
        f.write("\n")

        f.write("## 内容类型（可多标签）\n\n")
        f.write("| 类型 | 数量 |\n|------|------|\n")
        for t, c in content_counter.most_common():
            f.write(f"| {t} | {c} |\n")
        f.write("\n")

        f.write("## manifest 归属\n\n")
        f.write("| old_manifest | 数量 |\n|--------------|------|\n")
        for m, c in manifest_counter.most_common():
            f.write(f"| {m} | {c} |\n")
        f.write("\n")

        f.write("## 交叉表：首条年级线索 × manifest\n\n")
        manifests_order = sorted({m for r in rows for m in r["old_manifest"].split("|")})
        f.write("| 首条年级线索 | " + " | ".join(manifests_order) + " |\n")
        f.write("|" + "---|" * (len(manifests_order) + 1) + "\n")
        for g in grade_tags:
            if g not in [r["renjiao_hint"].split("|")[0] for r in rows]:
                continue
            f.write(f"| {g} |")
            for m in manifests_order:
                cnt = sum(1 for r in rows if r["renjiao_hint"].split("|")[0] == g and m in r["old_manifest"].split("|"))
                f.write(f" {cnt} |")
            f.write("\n")
        # also rows for any primary not in grade_tags
        primaries = sorted(set(r["renjiao_hint"].split("|")[0] for r in rows))
        for g in primaries:
            if g in grade_tags:
                continue
            f.write(f"| {g} |")
            for m in manifests_order:
                cnt = sum(1 for r in rows if r["renjiao_hint"].split("|")[0] == g and m in r["old_manifest"].split("|"))
                f.write(f" {cnt} |")
            f.write("\n")

        f.write("\n## 全部文件名清单\n\n")
        for r in rows:
            f.write(f"- `{r['filename']}` — {r['renjiao_hint']} / {r['content_type']} / {r['old_manifest']}\n")

        f.write("\n## 最难分类样例 Top 10\n\n")
        for r in hardest:
            f.write(f"- **{r['filename']}** — 年级:{r['renjiao_hint']} 类型:{r['content_type']} manifest:{r['old_manifest']} 关键词:{r['topic_keywords']}\n")

    # summary json for agent
    summary_path = os.path.join(OUT_DIR, "_summary.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(f"total={total}\n")
        f.write(f"no_prefix={no_prefix}\n")
        f.write(f"reject={reject_count}\n")
        f.write("hints=" + str(dict(hint_counter)) + "\n")
        f.write("manifest=" + str(dict(manifest_counter)) + "\n")
        f.write("hardest10=\n")
        for r in hardest:
            f.write(r["filename"] + "\n")

    print("OK", total, no_prefix, reject_count)

if __name__ == "__main__":
    main()
