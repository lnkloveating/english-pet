# Blender Adapter

这里只放模板化 3D 自动化，不允许 LLM 生成任意脚本后直接在生产 worker 执行。

建议接口输入：经过 `PetSpecification` 校验的 species、颜色、最多三个允许配饰和已审核 `base_asset_id`。worker 从只读基础资产创建副本，设置白名单材质/部件，运行资产预算检查，再导出 GLB。

安全要求：worker 使用隔离容器、无网络、只读模板目录、CPU/内存/时长限制；生成脚本必须来自仓库审核版本。
