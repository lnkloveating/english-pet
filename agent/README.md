# Agent Service

儿童英语聊天 Agent 的独立 FastAPI 服务。它接收已经转写的儿童表达与学习者画像，输出短回复、教学动作、奖励和新画像。

## 已有骨架

- `SafetyPolicy`：个人信息、危险/不适龄话题的 redirect / trusted-adult 决策
- `RewardPolicy`：有效开口必有基础声果；bonus 稀疏且不惩罚发音
- `CorrectionPolicy`：recast 隐性纠错接口与少量确定性样例
- `LearnerModel`：基于有效开口更新信心与目标句长
- `ResponseProvider`：stub 实现；后续接 LLM 时不改变业务合同
- `POST /v1/agent/turn`、`WS /v1/agent/voice` 与 `GET /healthz`
- 可替换的 `StreamingAsrProvider`，支持 stub 和豆包流式语音识别 2.0

## 本地运行

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ..\shared\python
pip install -e ".[dev]"
uvicorn shengsheng_agent.main:app --reload --port 8001 --env-file ..\.env
pytest
```

## 豆包流式 ASR 2.0

新版控制台使用单个 API Key：

```env
ASR_PROVIDER=doubao_streaming
DOUBAO_ASR_API_KEY=
DOUBAO_ASR_RESOURCE_ID=volc.seedasr.sauc.duration
DOUBAO_ASR_WS_URL=wss://openspeech.bytedance.com/api/v3/sauc/bigmodel_async
```

旧版控制台可改用 `DOUBAO_ASR_APP_KEY` 与 `DOUBAO_ASR_ACCESS_TOKEN`。密钥只放在
根目录 `.env`，不得写入移动端、日志或 Git。

客户端语音流协议见 [`docs/VOICE_PROTOCOL.md`](docs/VOICE_PROTOCOL.md)。

真实凭证联调可使用一段 16-bit 单声道 PCM WAV：

```powershell
python scripts\smoke_test_doubao_asr.py path\to\speech.wav
```

只验证 API Key 与服务权限，不发送音频：

```powershell
python scripts\smoke_test_doubao_asr.py --handshake-only
```

## TODO（负责人 A）

- [ ] 将黄金对话样例扩展到不同年级、低置信 ASR、沉默与中英混说
- [ ] 接入首个 LLM Provider，并用结构化输出约束回复长度和动作
- [x] 接入豆包流式 ASR adapter；音频本体不进入 Agent 日志
- [ ] 接入 TTS adapter
- [ ] 设计会话状态机：repeat → choose → answer → describe → free
- [ ] 引入离线评测：安全率、难度适配、recast 质量、平均延迟与成本
- [ ] 将内存画像替换为持久层；增加监护人数据删除接口

## 明确禁止

- 不直接依赖 `app/` 或 `pet_pipeline/` 内部代码
- 不让 LLM 单独决定基础奖励
- 不把模型推理过程、Provider 错误或儿童个人信息写入响应/日志
