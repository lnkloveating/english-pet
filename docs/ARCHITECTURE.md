# 架构说明

## 系统边界

```text
Expo Mobile
   │ HTTPS / JSON（后续语音流用 WebSocket）
   ▼
App BFF ────────────────┐
   │                    │
   ▼                    ▼
Agent Service      Pet Pipeline
   │                    │
LLM/ASR/TTS          Image Provider → review → Blender adapter

所有边界由 shared/contracts/openapi.yaml 定义
```

`app/backend` 是客户端唯一入口，负责认证、会话、幂等、超时和聚合；不包含 Agent 策略或宠物生成实现。`agent` 只做儿童对话决策；`pet_pipeline` 只做异步资产任务。生产环境中的数据库、队列、对象存储均通过适配器替换，MVP 骨架使用内存实现。

## Agent 回合

1. 预处理 ASR 文本与音频元数据（MVP 为接口占位）。
2. Safety Policy 判断是否需要拒绝、转移话题或提示寻求成人帮助。
3. Learner Profile 估计孩子当前可承受的词汇、句长和提问复杂度。
4. Correction Policy 决定是否做自然复述；不显示错误分数。
5. Reward Policy 以规则保证所有有效开口有基础声果，bonus 稀疏出现。
6. Response Generator 生成一句短回应和最多一个问题。
7. 返回决策迹线中的非敏感字段，供产品分析；禁止暴露模型思维过程。

## 宠物生成

MVP 主路径是可控 2D：描述 → 安全改写 → 结构化参数 → 概念图 → 自动规则审核 → 人工抽检。3D 路径只接受允许的基础骨架与参数，Blender adapter 负责拼装和导出 glTF，不从零自由建模。

## 数据策略

- `child_id` 使用服务端生成的非语义 ID。
- 默认不保存原始音频；保存转写前需监护人同意和明确保留期限。
- 日志中不得出现姓名、学校、联系方式、精确位置或完整自由文本。
- 安全事件单独分级记录，并限制访问权限。
