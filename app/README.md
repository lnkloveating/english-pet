# App（Mobile + BFF）

App 负责人拥有两个子项目：

- `mobile/`：Expo / React Native 客户端
- `backend/`：客户端唯一访问的 FastAPI Backend-for-Frontend（BFF）

BFF 负责会话入口、服务聚合、超时和错误映射，不实现 Agent 策略或宠物生成。移动端绝不保存模型/云服务密钥。

## 本地运行

先启动 Agent（8001）和 Pet Pipeline（8002），再启动 BFF：

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ..\..\shared\python
pip install -e ".[dev]"
$env:AGENT_SERVICE_URL="http://localhost:8001"
$env:PET_PIPELINE_URL="http://localhost:8002"
uvicorn shengsheng_app_api.main:app --reload --port 8000
```

移动端需要 Node.js 22.13+（Expo SDK 57）：

```powershell
cd ..\mobile
npm install
Copy-Item ..\..\.env.example .env
npm run start
```

真机调试时，把 `EXPO_PUBLIC_API_URL` 改成电脑在局域网内可访问的地址，而不是 `localhost`。

## TODO（负责人 B）

- [ ] 接入真实录音、权限说明、VAD/ASR 上传与弱网恢复
- [ ] 实现引导式、场景式、自由式三类对话 UI
- [ ] 使用安全存储保存匿名会话令牌；增加监护人入口
- [ ] 奖励动画和简单宠物成长状态
- [ ] 宠物创建、候选选择、等待/失败/审核状态页面
- [ ] 家长报告：有效开口、主动开口、平均句长、连续轮数
- [ ] BFF 增加认证、数据库、限流、幂等、结构化日志和追踪
- [ ] 用模拟服务做端到端测试，覆盖超时和安全转移
