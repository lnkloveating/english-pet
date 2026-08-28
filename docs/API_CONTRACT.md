# API Contract

机器可读合同位于 `shared/contracts/openapi.yaml`；JSON Schema 位于 `shared/schemas/`。本文说明跨模块约定。

## 通用规则

- 基础路径：`/v1`
- JSON 字段使用 `snake_case`；时间使用 UTC RFC 3339
- 客户端为写请求发送 `X-Request-ID`；创建任务时发送 `Idempotency-Key`
- 错误统一为 `ErrorResponse`，不得把 Provider 错误或密钥返回客户端
- 所有服务提供 `GET /healthz`
- 超时预算：Agent 10 秒，宠物任务创建 3 秒；长任务必须异步

## 对话回合

`POST /v1/agent/turn`

核心输入：会话 ID、匿名 child ID、ASR 文本、音频元数据、当前学习者画像和对话上下文。核心输出：宠物回复、教学动作、奖励决定、更新后画像与安全结果。

奖励不变量：

```text
valid_speaking_attempt == true  ⇒  base_voice_fruit >= 1
```

bonus 是稀疏惊喜，不应在每回合出现；发音/语法问题不得令基础奖励归零。

## 宠物任务

- `POST /v1/pets/jobs`：提交描述，立即返回 `job_id` 和 `queued`
- `GET /v1/pets/jobs/{job_id}`：返回 `queued|structuring|generating_concept|review_required|generating_3d|completed|failed`

MVP 允许在 `completed` 时只有 `concept_image_url`，`model_url` 可为空。3D 任务默认关闭。

## App BFF

- `POST /v1/sessions/{session_id}/turns`：转发并聚合 Agent 回合
- `POST /v1/pets` 与 `GET /v1/pets/jobs/{job_id}`：代理宠物任务

移动端只调用 BFF；服务地址和供应商密钥只存在服务端。

## 合同修改流程

1. 先提交 `shared/contracts/openapi.yaml`、Schema 与示例。
2. 标记兼容性：additive / deprecating / breaking。
3. 三模块分别更新 consumer/producer 测试。
4. 合并实现后再删除弃用字段；`/v1` 中不得无迁移直接 breaking change。
