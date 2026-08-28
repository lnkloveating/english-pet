# 三人分工与协作

## 负责人 A：Agent

工作目录：`agent/`

- 实现儿童语言水平画像、对话状态和难度调整
- 实现隐性纠错（recast）、奖励规则与安全策略
- 对接 ASR/LLM/TTS Provider，但保持 Provider 可替换
- 维护 Agent 单元测试、评测样例和延迟/成本指标

第一周交付：20 个黄金对话用例、stub → 首个 LLM Provider、奖励规则测试覆盖。

## 负责人 B：App

工作目录：`app/`

- Expo 客户端：录音、回合 UI、宠物反馈、奖励动画
- BFF：认证占位、会话、服务聚合、超时/错误映射
- 端到端埋点和家长报告基础页面
- 客户端不接触模型密钥，不依赖 Agent/Pet 内部代码

第一周交付：三屏可点击流程、BFF 接 stub 服务、一次完整对话回合。

## 负责人 C：Pet Pipeline

工作目录：`pet_pipeline/`

- 中文/英文描述安全处理与结构化
- 概念图 Provider、状态机、审核钩子、对象存储适配器
- Blender 模板化生成接口与最小脚本验证
- 定义移动端资产预算（面数、纹理、文件大小、glTF）

第一周交付：描述 → 结构化 JSON → stub 概念图任务；一个允许的基础骨架配置。

## 共同拥有：Shared Contracts

- `shared/` 改动使用 `contract/*` 分支。
- Pull Request 必须说明兼容性、迁移方式和示例 payload。
- 破坏性修改发布新主版本路径，不直接覆盖 `/v1`。
- 每日 15 分钟接口同步；每周一次真实设备端到端演示。

## 推荐分支

```text
main
├── feat/agent-first-provider
├── feat/app-speaking-loop
├── feat/pet-concept-job
└── contract/v1-turn-metadata
```

每个人只提交自己目录和经共同确认的 `shared/` 文件。不要把个人密钥、测试儿童数据、生成缓存提交到 Git。
