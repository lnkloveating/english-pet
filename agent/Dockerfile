FROM python:3.11-slim

WORKDIR /workspace
COPY shared/python /workspace/shared/python
COPY agent /workspace/agent
RUN pip install --no-cache-dir /workspace/shared/python /workspace/agent

EXPOSE 8001
CMD ["uvicorn", "shengsheng_agent.main:app", "--host", "0.0.0.0", "--port", "8001"]
