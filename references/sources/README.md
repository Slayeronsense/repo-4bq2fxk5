# 语料来源

- 根目录：`f:\xhs_transcripts`（小红书课堂字幕 ASR，368 条）
- 博主：小太阳老师

## Manifest（唯一年级索引）

全部在 `../manifests/`：

- `manifest-keep-{1shang,1xia,…,6xia}.txt` — 12 册教学语料
- `manifest-reject.txt` — 剔除
- `manifest-preview.txt` — 预习仅参考

**不要**使用已删除的旧文件（`manifest-keep-34grade.txt` 等）。

重建：`python ../scripts/rebuild_manifests.py`

审计明细：`../prescan/manifest-full.csv`
