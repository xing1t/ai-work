# 历史脚本审阅

以下 12 份脚本已逐份阅读后原样复制，本次未导入或执行。仅作研究，不可盲目重放；依赖未全部归档，仓库不是可运行的历史工作目录。新的设计修改需要另有明确任务、目标核对和备份。

|脚本|用途|依赖与硬编码|副作用 / 边界|
|---|---|---|---|
|[eda_call.py](eda_call.py)|bridge 调用助手|Python 标准库 urllib；127.0.0.1:49620；C:/work/eda_last.json|执行任意传入 EDA 代码，覆盖本地回包；只检查外层 success|
|[handoff_readonly_probe.js](handoff_readonly_probe.js)|历史活动文档探针|Run API Gateway eda.*|仅读取当前文档；本次不执行|
|[pcb_read_final.js](pcb_read_final.js)|最终 PCB 采集|eda.*；硬编码 PCB UUID 567e6dbc306f8243|运行 PCB DRC 并保存工程，有工程副作用|
|[pcb_fix_vias.js](pcb_fix_vias.js)|过孔字段适配|eda.*；mil 换算、0.3/0.6mm 案例值|setDocumentSource 覆盖工程源|
|[pcb_ground_clip.cjs](pcb_ground_clip.cjs)|固定地铜几何计算|Node + pcb-tools/geom/node_modules/clipper-lib；C:/work；pcb_pour_source.json、pcb_routed_current.json|离线写 pcb_ground_planes.json；硬编码板框、间距；不直接改 EDA|
|[pcb_apply_ground_fill2.py](pcb_apply_ground_fill2.py)|固定地铜写回|eda_call；C:/work 的 planes/pour_source；PCB UUID|删除部分原生记录、替换源、切换文档并检查 DRC；本地覆盖回包|
|[pcb_apply_priority_routes.py](pcb_apply_priority_routes.py)|布线写回|eda_call；C:/work/pcb_route_ops.json；56 器件假设|先删除铜线与过孔再重建，运行 DRC，覆盖本地输出|
|[pcb_priority_dsn.py](pcb_priority_dsn.py)|优先铜线转 DSN|pcb_sexp；C:/work；PCB3_rework.dsn 与 pcb_priority_copper.json|离线覆盖 PCB3_priority.dsn，未归档所有输入，不可独立复现|
|[pcb_sexp.py](pcb_sexp.py)|DSN/SES 解析辅助|Python 标准库；C:/work/PCB3_routed.ses|主入口离线读取/打印；不是通用完整语法实现|
|[pcb_swd_simplify.py](pcb_swd_simplify.py)|SWD 电源短路径替换|eda_call；C:/work/pcb_swd_power_drc.json；硬编码折线|删除历史 ID 并创建铜线、运行 DRC、覆盖本地回包|
|[pcb_verify_final.py](pcb_verify_final.py)|旧离线验收|Python；C:/work 的最终 JSON 与初始基准|离线断言后覆盖 PCB3_final_source.txt；不能当纯只读命令|
|[pcb_report_final.py](pcb_report_final.py)|旧布局报告生成|Python；C:/work/PCB3_final_verified.json|离线覆盖报告与 PCB3_layout_source.txt；不重检活动工程|
