# Pet Pipeline

AI 宠物资产异步流水线。MVP 主路径：孩子描述 → 安全结构化 → 可控 2D 概念图；模板化 Blender 3D 接口保留但默认关闭。

## 已有骨架

- `PetDescriptionParser`：将中英文自由描述映射到受控 species / color / personality / theme / accessories
- `PetSafetyRewriter`：去除不适龄和明显版权角色指向
- `ConceptImageProvider`：stub 及真实图片 Provider 的协议
- `BlenderAdapter`：只接受模板参数的协议与禁用实现
- `InMemoryJobRepository`：MVP 异步状态机占位
- `POST /v1/pets/jobs`、`GET /v1/pets/jobs/{job_id}`

## 本地运行

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ..\shared\python
pip install -e ".[dev]"
uvicorn shengsheng_pet_pipeline.main:app --reload --port 8002
pytest
```

## TODO（负责人 C）

- [ ] 将规则结构化器替换为带 Schema 验证的 LLM Provider
- [ ] 接入 Image Provider，输出立绘、三视图和表情参考的可选任务
- [ ] 增加内容审核、版权相似性、人工审核队列与失败重试
- [ ] 将内存任务仓库替换为数据库 + 队列 + 对象存储
- [ ] 创建 CatBase / DinoBase / FoxBase 中至少一个高质量基础资产
- [ ] Blender worker 仅映射允许的参数，导出经预算校验的 glTF
- [ ] 定义生成成本、等待时间、取消与资产删除流程

## MVP 资产预算建议

- 2D：透明背景 WebP，单张不超过 1 MB
- 3D：glTF/GLB，单模型建议不超过 15k triangles、2 张 1024 纹理、5 MB
- 所有 3D 资产必须来自已审核基础骨架，第一版不做自由拓扑/自动 rig
