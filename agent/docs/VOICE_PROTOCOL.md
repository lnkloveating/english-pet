# Agent 语音流协议（v1）

Agent 暴露 `WS /v1/agent/voice`。移动端仍应连接 App BFF，由 BFF 将此协议代理到 Agent；
移动端不得直接持有豆包密钥。

当前协议是 additive 的内部合同：已有 `POST /v1/agent/turn` 保持不变。音频约定为
16 kHz、16-bit、单声道 PCM。单个二进制帧最多 64 KB，单回合最多约 60 秒。

## 建立会话

连接成功后，客户端首先发送：

```json
{
  "type": "session.start",
  "session_id": "session_001",
  "child_id": "anonymous_child_001",
  "learner_profile": {
    "grade": 3,
    "level": 2,
    "confidence": 0.5,
    "target_sentence_words": 5,
    "interests": [],
    "recent_topics": []
  },
  "audio": {
    "format": "pcm",
    "sample_rate": 16000,
    "bits": 16,
    "channels": 1
  },
  "context": []
}
```

Agent 返回 `session.ready`。

## 一个语音回合

1. 客户端发送 `{"type":"input.start"}`。
2. Agent 返回 `input.ready`。
3. 客户端连续发送二进制 PCM 音频帧。
4. 客户端发送 `{"type":"input.commit"}`。
5. Agent 可返回多个 `asr.partial`，然后返回 `asr.final`。
6. Agent 将最终文字交给现有回合逻辑，返回 `agent.reply` 和 `turn.completed`。

`agent.reply.turn` 与 `POST /v1/agent/turn` 的响应结构一致。连接可复用；下一回合重新发送
`input.start`。取消当前回合发送 `input.cancel`，关闭会话发送 `session.close`。

## 服务端事件

```text
session.ready
input.ready
asr.partial       { text }
asr.final         { text }
agent.reply       { transcript, turn }
turn.completed    { turn_id }
input.cancelled
session.closed
error             { error: { code, message, retryable } }
```

Provider 的原始错误和凭证永远不会透传给客户端。
