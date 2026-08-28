# Agent Service

儿童英语聊天 Agent 的独立 FastAPI 服务。它接收已经转写的儿童表达与学习者画像，输出短回复、教学动作、奖励和新画像。

## 已有骨架

- `SafetyPolicy`：个人信息、危险/不适龄话题的 redirect / trusted-adult 决策
- `RewardPolicy`：有效开口必有基础声果；bonus 稀疏且不惩罚发音
- `CorrectionPolicy`：recast 隐性纠错接口与少量确定性样例
- `LearnerModel`：基于有效开口更新信心与目标句长
- `ResponseProvider`：stub 实现；后续接 LLM 时不改变业务合同
- `POST /v1/agent/turn` 与 `GET /healthz`

## 本地运行

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ..\shared\python
pip install -e ".[dev]"
uvicorn shengsheng_agent.main:app --reload --port 8001
pytest
```

## TODO（负责人 A）

- [ ] 将黄金对话样例扩展到不同年级、低置信 ASR、沉默与中英混说
- [ ] 接入首个 LLM Provider，并用结构化输出约束回复长度和动作
- [ ] 接入 ASR/TTS adapter；音频本体不进入 Agent 日志
- [ ] 设计会话状态机：repeat → choose → answer → describe → free
- [ ] 引入离线评测：安全率、难度适配、recast 质量、平均延迟与成本
- [ ] 将内存画像替换为持久层；增加监护人数据删除接口

## 明确禁止

- 不直接依赖 `app/` 或 `pet_pipeline/` 内部代码
- 不让 LLM 单独决定基础奖励
- 不把模型推理过程、Provider 错误或儿童个人信息写入响应/日志
