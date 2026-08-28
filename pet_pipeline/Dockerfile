FROM python:3.11-slim

WORKDIR /workspace
COPY shared/python /workspace/shared/python
COPY pet_pipeline /workspace/pet_pipeline
RUN pip install --no-cache-dir /workspace/shared/python /workspace/pet_pipeline

EXPOSE 8002
CMD ["uvicorn", "shengsheng_pet_pipeline.main:app", "--host", "0.0.0.0", "--port", "8002"]
