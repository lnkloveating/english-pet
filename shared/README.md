# Shared Contracts

这里是三个模块唯一允许共享的边界定义，不放任何业务实现。

- `contracts/openapi.yaml`：HTTP API 的机器可读合同
- `schemas/*.schema.json`：关键消息的 JSON Schema
- `examples/`：消费者/生产者都应通过的黄金 payload
- `python/`、`typescript/`：最小跨语言类型；后续由 OpenAPI 生成器替换

修改流程见 `docs/API_CONTRACT.md`。任何新增字段必须有示例和兼容性说明。
