# 声生岛（Shengsheng Island）

一个会被孩子“用英语养大”的 AI 宠物。孩子通过英语开口与宠物互动，获得声果、推动宠物成长，并在低压力的陪伴式对话中逐步建立表达信心。

本仓库是可直接三人并行开发的 MVP monorepo。三个业务模块不互相导入内部代码，只通过 `shared/` 中的版本化合同和 HTTP API 通信。

## MVP 范围

- 一个宠物、三个引导式英语场景
- 儿童语音输入链路的接口占位：VAD → ASR → 语言/重复检测
- 自适应儿童英语聊天 Agent：学习者画像、难度控制、隐性纠错、奖励与安全策略
- “有效开口必有基础奖励，表现好偶有额外惊喜”的奖励机制
- 用户描述 → 安全结构化 → 2D 概念图生成；模板化 Blender 3D 作为异步占位
- 简单成长状态与家长报告数据接口

## 目录与负责人

| 目录 | 默认负责人 | 主要产出 |
| --- | --- | --- |
| `agent/` | Agent 工程师 | 对话决策、学习者画像、隐性纠错、奖励判断、安全策略 |
| `app/` | App 工程师 | Expo 移动端、FastAPI BFF、语音/UI、服务接入 |
| `pet_pipeline/` | 宠物生成工程师 | 描述结构化、概念图 Provider、Blender 自动化接口 |
| `shared/` | 三人共同评审 | OpenAPI、JSON Schema、跨模块类型与错误约定 |

详细职责见 [docs/TEAM.md](docs/TEAM.md)，接口约定见 [docs/API_CONTRACT.md](docs/API_CONTRACT.md)。

## 技术栈

- 移动端：Expo + React Native + TypeScript
- 应用后端（BFF）：Python 3.11 + FastAPI + httpx
- Agent / 宠物流水线：Python 3.11 + FastAPI + Pydantic
- 本地编排：Docker Compose；测试：pytest / Vitest
- 合同：OpenAPI 3.1 + JSON Schema，接口版本统一为 `/v1`

选择这套技术栈是为了尽快跑通体验闭环；MVP 阶段不训练自有大模型，先用策略层、可观测数据与可替换 Provider 验证产品。

## 5 分钟启动

1. 复制环境变量：`Copy-Item .env.example .env`
2. 安装 Docker Desktop 后运行：`docker compose up --build`
3. Agent 文档：`http://localhost:8001/docs`
4. 宠物流水线文档：`http://localhost:8002/docs`
5. App BFF 文档：`http://localhost:8000/docs`
6. 移动端：进入 `app/mobile`，执行 `npm install` 与 `npm run start`

没有 Docker 也可按各模块 README 独立启动。

## 第一条端到端链路

```text
Mobile
  → POST /v1/sessions/{id}/turns (BFF)
    → POST /v1/agent/turn (Agent)
  ← 宠物回复 + 隐性纠错标记 + 声果奖励 + 新学习者画像
```

宠物创建链路：

```text
Mobile
  → POST /v1/pets (BFF)
    → POST /v1/pets/jobs (Pet Pipeline)
  ← job_id；随后轮询状态和概念图
```

## 开发原则

1. 保护开口意愿优先：有效英语开口不得因发音或语法不完美失去基础奖励。
2. Agent 是伙伴，不是判分老师；优先使用 recast（自然复述）隐性纠错。
3. 儿童安全默认开启；不保存原始音频，除非获得可撤销的监护人同意。
4. 合同先行：跨模块字段先修改 `shared/`，经三人评审后再实现。
5. 不在客户端保存任何模型或云服务密钥。

## 开发工作流

- 从 `main` 创建：`feat/agent-*`、`feat/app-*`、`feat/pet-*`、`contract/*`
- 小 PR、至少一位非作者审核；修改合同需三位负责人确认
- 提交前运行 `./scripts/check.ps1`（Windows）或 `./scripts/check.sh`
- 禁止提交 `.env`、儿童原始音频、真实个人信息与生成资产缓存

路线图见 [docs/ROADMAP.md](docs/ROADMAP.md)，产品与安全边界见 [docs/PRODUCT_GUARDRAILS.md](docs/PRODUCT_GUARDRAILS.md)。
