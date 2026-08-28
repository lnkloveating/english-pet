# Contributing

## 首次设置

1. Clone 后复制 `.env.example` 为 `.env`。
2. 阅读 `docs/TEAM.md` 和自己模块的 README。
3. 在自己的功能分支工作，不直接提交到 `main`。

## 分支与提交

- Agent：`feat/agent-<topic>`
- App：`feat/app-<topic>`
- Pet：`feat/pet-<topic>`
- 合同：`contract/<topic>`
- 修复：`fix/<topic>`

提交信息建议使用 `feat(agent): ...`、`fix(app): ...`、`docs(shared): ...`。一个提交只解决一个问题。

## Pull Request 门槛

- 说明用户价值、范围、验证结果和是否修改合同。
- 新功能必须有测试或解释无法自动测试的原因。
- 不得包含密钥、儿童个人信息、真实音频或生成资产缓存。
- 合同变更必须同步 OpenAPI、Schema、示例和消费者/生产者。
- 至少一位非作者审核；合同变更由三位负责人确认。

## Definition of Done

- 代码可在全新环境按 README 启动。
- 自动检查通过，失败/超时/空输入路径有处理。
- 儿童可见文案符合 `docs/PRODUCT_GUARDRAILS.md`。
- 新增日志和埋点不包含个人信息或完整自由文本。
