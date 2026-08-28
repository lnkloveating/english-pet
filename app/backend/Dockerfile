FROM python:3.11-slim

WORKDIR /workspace
COPY shared/python /workspace/shared/python
COPY app/backend /workspace/app/backend
RUN pip install --no-cache-dir /workspace/shared/python /workspace/app/backend

EXPOSE 8000
CMD ["uvicorn", "shengsheng_app_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
