# 抖音 registry 刷新协议

> **单点真相**：`batches/douyin-registry-shard-{A~E}.yaml`  
> **合并正本**：`references/ingest-registry.yaml`（仅由 `scripts/merge_douyin_registry.py` 生成）

## 改一条的正确做法

1. 在对应 shard yaml 里 **整段替换** 该 `id` 的旧条目（禁止另建第二份）
2. 运行 `python scripts/merge_douyin_registry.py` → 全量覆盖 registry
3. 在 `batches/douyin-refresh-shard-{X}.md` 记一行变更

## 已废弃（勿再引用）

- ~~prescan-douyin-pilot.csv~~ → 用 `prescan/prescan-douyin.csv`
- ~~手工双写 ingest-registry + shard~~ → 手工验收内容写入 shard 后 merge
