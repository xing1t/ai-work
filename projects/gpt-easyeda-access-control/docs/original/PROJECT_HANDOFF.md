# PROJECT_HANDOFF — GPT + 嘉立创 EDA 半自动设计

## 当前状态摘要

归档日期：2026-11-04，Asia/Shanghai。建议项目代号：gpt-easyeda-access-control。

- **已验证事实**：经本机 HTTP/WebSocket 桥接，在嘉立创 EDA 专业版完成“题目一·密码门禁控制系统”原理图绘制、元件回读、PCB3 重布局、双层布线与固定地铜生成。
- **最终 PCB 快照**：56 个器件、41 个非空网络、191 个器件焊盘条目、638 段铜线、51 个过孔、两块 GND 固定填充。严格 PCB DRC 返回 true，详细错误列表为空，保存返回 true；56 个位号均显示，焊盘网络归属与导入时一致。
- **必须保留的限制**：原理图阶段曾返回 DRC=false，未取得已通过原理图 ERC/DRC 的最终证据。固件、打样、实物、EMC 和电机堵转测试未验证完成。地铜不是动态覆铜，后续改线或移动器件须重新计算。
- **本次复核范围**：读取并离线复核最终证据，没有重新布线或修改 EDA。桥服务当前连通；只读探针发现活动页是原理图 p1，不是 PCB3。PCB 结果来自保存快照，不冒充归档时对当前 PCB 重新运行的 DRC。
- **资料库现状**：C:\work 不是 Git 仓库，且混有另一个桌面宠物项目。本次只提供供另一对话归档的交接，不把整个工作目录初始化或提交；未创建远程仓库、未推送、未默认公开。

本文中，**已验证事实**指操作证据或可核对文件；**已讨论方案**指提出过但没有完成证据的方案；**待确认**指现有信息不足。“文件存在”不代表脚本可移植、可安全重放或整条流水线已经复现。

## 1. 项目概况

目标是以课程密码门禁为案例，探索 AI 辅助工程师完成原理图与 PCB，积累可复用工具、决策和检查记录。AI 工程接单、报价交付可复用经验；闲鱼自动化、自动发货和 AI 漫剧只是用户提出的后续方向，不属于本案例已实现能力。

|环节|状态与边界|
|---|---|
|连接 EDA、执行 JavaScript、回读结果|已验证；本机 bridge 转发，不是模拟鼠标点击|
|器件检索、核对名称/封装、逐件放置与设置位号|已验证；检索结果仍须核对|
|原理图分块、短引线、同名网络标签/端口|已验证；保存了 173 项预期连接对照|
|PCB3 元件导入|用户创建并准备；开始时已有 56 个导入器件，不能宣称 AI 从零验证了导入全过程|
|PCB 重布局、板框、孔、丝印、两层布线及地铜|已验证；用户指出重叠后重新布局，以最终文件为准|
|PCB DRC、位号显示及网络归属回读|已验证；适用于记录内的规则与最终快照|
|需求取舍、器件/外设选择、视觉审查|仍需人工；用户已实际参与并纠正布局|
|原理图 ERC/DRC 全部闭环|未验证完成，旧报告记录 false|
|完整原生工程包导出、异机恢复|待确认；文本快照不等于包含所有库资源的完整工程包|
|固件、生产资料、打样及实测|未验证完成|
|通用一键全自动设计或接单系统|未实现；现有脚本依赖项目快照、人工判断和多次修正|

## 2. 技术环境与接入方式

### 2.1 已核对环境

|项目|记录|
|---|---|
|系统与 Shell|Windows，详细系统版本待确认；PowerShell 7.6.5|
|工作目录|C:\work，不是干净的专用项目根目录|
|EDA|嘉立创 EDA 专业版桌面端；工程源 editVersion=3.2.116，未以 About 页面再次确认|
|AI 客户端|当前执行助手为 Codex 桌面会话；具体界面模型标签待确认|
|Python|3.14.4；C:\msys64\mingw64\bin\python.exe；主要使用标准库|
|Node.js|v26.13.0；C:\Program Files\nodejs\node.exe|
|Git|2.56.0.windows.2；C:\work 不是 Git 仓库|
|easyeda-api skill|C:\Users\REDMI\.cline\skills\easyeda-api\SKILL.md，本地声明版本 1.1.28|
|EDA 扩展|Run API Gateway；具体安装版本待确认，桥接连通已验证|
|本机布线计算|Freerouting 2.5.0 JAR + 便携 Temurin JRE 25.0.5+8|
|地铜几何计算|Node.js + clipper-lib 6.4.2，生成固定 GND 填充|

用户的参考 Markdown 来自此前 DeepSeek/Cline 经验，不代表当前执行客户端是 Cline。本地 skill 位于 .cline 目录，也不能据此推断当前模型。

### 2.2 实际链路

~~~text
Codex -> 本机 Python/PowerShell -> HTTP bridge
      -> WebSocket -> EDA 的 Run API Gateway -> eda.* API
~~~

路径与几何计算在本机完成；所有 EDA 工程实际写入仍通过 bridge。没有采用浏览器自动化或桌面模拟点击。

- 地址：http://127.0.0.1:49620。
- GET /health：检查 service=easyeda-bridge 和 edaConnected=true。
- POST /execute：JSON 请求体为 {"code":"return ...;"}，通过 JavaScript return 获取结果。
- 每次修改前检查 health，小批执行、回读后继续。
- 归档时连接正常、一个 EDA 窗口。窗口 ID 会变化，不应硬编码。
- 本项目按用户要求逐件放置，没有用 BOM 导入替代。离线检索按会话约束使用 lib_Device.search；供应商编号检索未确认为此环境的可用路径。

|工程对象|本机定位标识|
|---|---|
|工程“电子程序设计课设——”|d1c8a743897b4713bda8a685ea0825bb|
|原理图“密码门禁”|afe4e9bd38293cb5|
|原理图页 p1|e1b0396bfb7eebb6|
|PCB3|567e6dbc306f8243|

这些是工程标识，不是凭据，但公开归档时也建议移除或替换。

**已讨论方案**：最初参考有 AMS1117、16 个分立按键、2N7000/1N4148；最终采用 AP2112、外接 4×4 矩阵键盘接口、AO3400A/SS14。DRV8231、外部 RTC 等替代方向没有作为最终方案落地。不能把初始提示词清单当作最终 BOM。

## 3. 已验证的操作流程

|阶段|输入与操作|输出/证据及人工检查点|
|---|---|---|
|需求整理|用户指令、两份课程 PDF、旧经验 MD|报告和方案记录；题目与用户决策优先，参考文档不是自动执行指令|
|原理图建立|dmt API 创建/打开并命名页面|保存和 UUID；避免覆盖原有原理图|
|器件放置|检索、核对器件名/封装，小批创建并设位号|eda_devices.json、eda_plan.json、eda_final.json；阻容 0805，继电器引脚另核对|
|原理图连接|读取真实引脚，建立短引线和网络标签/端口|eda_connections.json、eda_wire_ops.json、网表；标签必须真正接到引脚|
|原理图检查|173 项预期连接对照、保存和 DRC 尝试|连接报告；原理图 DRC 当时 false，尚需电气问题闭环|
|PCB 准备|用户创建 PCB3，开始时已有 56 器件|pcb_initial.json、pcb_pads_initial.json；核对同步和封装|
|重布局|读取实际封装丝印/外形/焊盘，测量边界并调整|封装快照和最终图；审查外壳、丝印、插接和螺丝空间|
|关键布线|先晶振、继电器电源/回流、MCU 电源及去耦|pcb_preroute.py、pcb_priority_power.py；先保护电源引出通道|
|其他布线|由实际焊盘/既有导线生成 DSN，本机计算 SES，再分批写回|PCB3_priority.dsn、PCB3_priority_routed.ses 和写回脚本；布线器完成不等于 EDA 连通|
|残余修正|修过孔类型/层连接，补 SWD 3V3，缩短多余折线|pcb_fix_vias.js、pcb_swd_simplify.py、DRC 快照|
|地铜|本机计算避让、地焊盘连接与孤岛过滤，写入固定 FILL|pcb_ground_clip.cjs、pcb_apply_ground_fill2.py；后续改线须重算|
|最终验收|严格 PCB DRC、网络对照、位号可见、保存、顶底图|PCB3_final_verified.json、PCB3_final_source.txt、PNG；仍需人工和实物验收|

目前停在设计资料形成和记录内 PCB 检查闭环之后。尚未完成“原理图电气问题全部闭环 → 固件 → 生产资料 → 样机实测”的整机流程。

## 4. 文件与代码清单

以下文件本次均确认存在。旁边 PROJECT_FILE_MANIFEST.json 提供完整本地顶层文件清单、分类与 SHA-256；存在不等于建议全部提交。

### 4.1 优先归档的成果与证据

|准确路径|用途及建议|
|---|---|
|C:\work\PCB3_final_source.txt|最终 PCB 文本源，含固定地铜；项目私有归档，不是已验证可独立迁移的完整工程包|
|C:\work\PCB3_final_verified.json|最终元件、规则、DRC、保存与源数据；核心验收证据，脱敏后归档|
|C:\work\PCB3-final.png、C:\work\PCB3-bottom.png|最后顶/底视觉检查图；不能替代生产文件|
|C:\work\PCB3布局核对.md|最新布局、布线、约束及限制，优先阅读|
|C:\work\密码门禁_绘制报告.md|原理图模块、GPIO、接口及阶段状态；保留原理图 DRC=false 记录|
|C:\work\密码门禁_网表.json|已保存的原理图网表，归档时说明格式|
|C:\work\eda_final.json、C:\work\eda_connections.json|原理图回读与 173 项预期连接对照|
|C:\work\eda_source_after.json|原理图阶段源回读包装文件；恢复方式未独立验证|
|C:\work\pcb_pads_initial.json|PCB 初始焊盘网络映射，供前后比较|
|C:\work\密码门禁_方案与成本估算.md|2026-11-04 历史预算模型，不是实时采购报价；“PCB 尚未完成”等描述已被后续阶段更新|
|C:\work\HANDOFF_READONLY_CHECK.json|本次只读接入结果；不等于重新检查 PCB3|

PCB3_layout_source.txt 当前与最终源重复。pcb_layout_final.json 和多数 pcb_*drc*.json 是旧阶段结果，不能因名字中有 final 就替代 PCB3_final_verified.json。

最终源文件 SHA-256：

~~~text
b23308d9a55fcdb7df6450c9207c2d558bf2a59a774f27d78311afd69d8ffe83
~~~

### 4.2 脚本及成熟度

下表中的文件均在 C:\work\，为准确当前路径。多数仍是会话工作脚本，并非通用发布 CLI。

|文件|用途及使用边界|
|---|---|
|eda_call.py|health、POST execute、保存回包；硬编码 bridge/输出目录；业务内层 applied=false 仍需调用方检查|
|eda_docs.py、eda_search.py、eda_export.py|查本地 API、器件检索、画布截图；路径待参数化，截图可被覆盖|
|eda_build.py、eda_layout.py、eda_wiring.py、eda_uid.py、eda_clean.py|原理图构建、布局、连线及处理；有写入/清理操作，不可整批盲目重放|
|pcb_read_geometry.js、pcb_read_footprints.py、pcb_read_final.js|读焊盘/封装和最终结果；后者会 DRC 并保存，封装脚本会切换文档|
|pcb_bbox.py、pcb_measure_rework.py、pcb_pack_silk.py|边界与丝印计算；依赖会话 JSON 和本机路径|
|pcb_apply_rework.py、pcb_apply_silk_native.py|应用重布局与丝印；需要目标文档和备份保护|
|pcb_preroute.py、pcb_priority_power.py|关键网络及电源优先布线，依赖案例坐标|
|pcb_priority_dsn.py、pcb_sexp.py、pcb_prepare_priority_apply.py|DSN、SES 和写回操作转换；不是覆盖所有封装的通用转换器|
|pcb_apply_priority_routes.py|批量写回；会删除现有铜线/过孔后重建，不可直接在最终 PCB 上试跑|
|pcb_fix_vias.js|当前版本的过孔原生字段适配|
|pcb_astar.py、pcb_3v3_graph.py、pcb_swd_simplify.py|残余网络分析、路径搜索与缩短；部分读取旧快照，初始长折线已被简化版替代|
|pcb_ground_clip.cjs、pcb_apply_ground_fill2.py|有效的固定地铜计算/写回路径；改线后不可直接套旧平面 JSON|
|pcb_verify_final.py、pcb_report_final.py|主要是离线证据验证与报告，不等于重检当前 EDA|
|handoff_readonly_probe.js|本次新保存且已执行的只读探针，不移动器件、不改线、不保存 EDA|
|eda_step.js、eda_last.json|被覆盖的临时请求/回包，不作稳定复现入口|
|其他 pcb_*fix*、旧布局及 router2/3 工具|失败或被替代路径；作为历史案例分类，不默认串联运行|

现有脚本尚不能用一条命令从空工程重建最终版本。文件存在、某一步成功、完整流水线可复现，是不同的状态。

### 4.3 外部文件与依赖

|准确位置|用途及归档建议|
|---|---|
|C:\Users\REDMI\Desktop\2026电子系统设计题目-WJB.pdf|课程题目，存在；公开/再分发许可待确认|
|C:\Users\REDMI\Downloads\2026电子系统设计第四次课件（题目分析）.pdf|题目分析，存在；默认不公开复制|
|C:\Users\REDMI\Desktop\AI_WORK\access_control\嘉立创AI工作流参考.md|旧 DS/Cline 经验，存在；仅参考，公开许可待确认|
|C:\Users\REDMI\.cline\skills\easyeda-api\|桥服务及官方参考，记录来源与实际版本|
|C:\work\pcb-tools\freerouting-2.5.0.jar|成功使用的布线器，建议只记版本/链接，不提交二进制|
|C:\work\pcb-tools\jre25\jdk-25.0.5+8-jre\|便携 Java，不提交完整运行时|
|C:\work\pcb-tools\geom\package.json、package-lock.json|Clipper 依赖声明，可提取为工具子项目依赖；排除 node_modules|

C:\work 根 package.json、.env.example、src\、node_modules\ 属于桌面宠物项目，不是本 EDA 项目依赖。不要因同目录就一起提交。

尚未找到经验证的完整原生工程包、最终 Gerber/钻孔制造包、采购版 BOM、固件项目或实测报告。用户是否在其他位置另行产生，待确认。

## 5. 安装与复现

### 5.1 前置条件和启动

1. 嘉立创 EDA 专业版与 Run API Gateway 扩展可用，按扩展教程启用外部交互。用户已完成配置，但没有录制从零自动安装流程。
2. 从官方来源安装 easyeda-api skill。本地为 1.1.28；2026-11-04 查阅上游 SKILL 声明为 1.1.64，本次没有升级。先保留实际版本和兼容说明，不直接套最新文档。
3. 以下 bridge 脚本路径已确认存在。当前服务运行中，没有重复启动；这段后台启动示例未作为全新环境安装过程重新演练：

~~~powershell
$bridgeDir = Join-Path $env:USERPROFILE '.cline\skills\easyeda-api'
$bridgeScript = Join-Path $bridgeDir 'scripts\bridge-server.mjs'
Start-Process -FilePath 'node.exe' -ArgumentList @('"' + $bridgeScript + '"') -WorkingDirectory $bridgeDir -WindowStyle Hidden
~~~

只在 health 不可达时启动；端口占用时按实际 bridge 发现结果处理，不重复启动。用户原始教程也提供了进入该 skill 目录后执行 node scripts/bridge-server.mjs 的交互方式。

### 5.2 已执行的最小只读示例

~~~powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:49620/health'
python C:\work\eda_call.py C:\work\handoff_readonly_probe.js
~~~

探针已单独保存，完整内容如下：

~~~javascript
const document = await eda.dmt_SelectControl.getCurrentDocumentInfo();
return {
  document,
  pcbPartCount: document?.documentType === 3
    ? (await eda.pcb_PrimitiveComponent.getAll()).length
    : null
};
~~~

本次实得 success=true、当前为 p1（documentType=1），因此 pcbPartCount=null。若人工切到 PCB3 后运行同一探针，可读取器件数；本次没有为归档自动切换用户活动页。

该 bridge 请求不需要 AI API Key。其他模型平台账号或计费设置未归档或验证，不从无关 .env 提取。

### 5.3 实际使用的布线命令和边界

以下形式实际运行成功，但输入文件必须先生成，不能直接在最终工程上重放写回：

~~~powershell
$pcbJavaExe = 'C:\work\pcb-tools\jre25\jdk-25.0.5+8-jre\bin\java.exe'
& $pcbJavaExe -jar C:\work\pcb-tools\freerouting-2.5.0.jar -de C:\work\PCB3_priority.dsn -do C:\work\PCB3_priority_routed.ses --gui.enabled=false --user_data_path=C:\work\pcb-tools\router-data-priority --usage_and_diagnostic_data.disable_analytics=true --router.fanout.enabled=false --router.automatic_neckdown=true --router.autorouter.max_passes=20 --router.optimizer.enabled=false
~~~

该 DSN/SES 不是最终 PCB：之后还有过孔修正、SWD 电源收尾与固定地铜生成。不能将这条命令称为最终工程恢复命令。

地铜曾执行 node C:\work\pcb_ground_clip.cjs 并由 pcb_apply_ground_fill2.py 写回；两者依赖特定快照。换路径、换工程或改线后需重新整理输入。全流程异机/空工程重建未验证。

## 6. 工程案例与验证

### 6.1 最终设计与已有决策

- 主控 U1：STM32F103C8T6；LDO U2：AP2112K-3.3TRG1；EEPROM U3：AT24C02D-SSHM-T。
- K1/K2：两个 SRD-05VDC-SL-C，用户已决定保留继电器。实际库引脚核对为线圈 1/4、COM=5、NC=3、NO=2；NC 接 GND、NO 接 5V，两 COM 接电机两端。切换两个电机端子的电位实现正反转，不是两个独立门锁。
- Q1–Q4 为 AO3400A，D1–D3 为 SS14；有源蜂鸣器、红色状态灯和白光演示 LED。
- 电阻 15 个、电容 16 个，全部为 0805。键盘是外接 4×4 无源矩阵接口，占 8 个 GPIO，没有在板上放 16 个独立按键。
- 密码/少量循环日志放非易失 EEPROM，保持数据不依赖持续 3V3；CR2032 只给 VBAT/RTC 后备，不给整机供电，也不与 3V3 硬并联。
- Y1 为 8MHz，C10/C11 初始负载 33pF；Y2 为 32.768kHz，C12/C13 初始负载 22pF。晶体起振、寄生和精度尚需校核与实测。
- PCB 85×60 mm、两层布线、元件在顶层；四角 3.2 mm 非金属化孔，中心距相邻板边各 3.5 mm。用户授权尺寸自行把握，电机未选型。
- 电机主干 1.50 mm，MOTOR_A 局部引出 1.125 mm；继电器电源/回流主干 1.50 mm。普通信号主要 0.25 mm，芯片/晶振短引出有 0.15–0.20 mm。没有按未知电机保证载流额定值。
- 顶、底地铜是两块固定 FILL，不是自动更新的 POUR/POURED。包含几何避让、地焊盘连接和孤岛筛选，设计变更后须重新生成。

### 6.2 GPIO 与接口

|GPIO|网络/用途|
|---|---|
|PA0–PA3 / PA4–PA7|KEY_R1–4 / KEY_C1–4|
|PB0 / PB1|PIR_OUT / BUZZ_EN|
|PB2|BOOT1 下拉|
|PB12 / PB13|RELAY_A / RELAY_B|
|PB14 / PB15|LIGHT_EN / STATUS_LED|
|PB6 / PB7|I2C_SCL / I2C_SDA|
|PA13 / PA14|SWDIO / SWCLK|
|PD0 / PD1|HSE_IN / HSE_OUT|
|PC14 / PC15|LSE_IN / LSE_OUT|

|接口|针序|
|---|---|
|J1|1=5V，2=GND|
|J2|1–4=KEY_R1–4，5–8=KEY_C1–4|
|J3|1=5V，2=PIR_OUT，3=GND；核对实际模块输出电平|
|J4|1=3V3，2=SWDIO，3=SWCLK，4=GND|
|J5|1=GND，2=3V3，3=SCL，4=SDA；核对实际 OLED 针序|
|J6|1=MOTOR_A，2=MOTOR_B|

### 6.3 验证状态分别记录

|检查|结果与依据|
|---|---|
|原理图连接归属|原报告记录 173 项预期连接 0 不匹配；本次确认预期表 173 项、最终回读 56 器件、保存 true|
|原理图 ERC/DRC|当时 DRC=false，详细结果不能可靠返回；未确认最终通过|
|PCB 焊盘网络|191 项含电池座同号重复焊盘，与初始基准逐项一致；本次离线重比通过|
|最终 PCB DRC|PCB3_final_verified.json：drcPassed=true，drc=[]|
|保存与位号|同一快照 saved=true，56 个位号均 visible=true|
|源快照一致性|PCB3_final_source.txt 与最终 JSON 内 source 一致，哈希见上|
|预算|有历史估算，不等于完整采购 BOM 或现时报价|
|完整原生工程导出、异机恢复|未验证，不能把文本快照冒充完整工程包|
|最终 Gerber/钻孔包|未找到已验证交付包|
|打样、焊接、固件、整机实测|没有完成证据|

课程行为目标：4 位密码、正转 5 秒/等待 10 秒/反转 5 秒、30 秒内两次错误报警、改密及日志查询。这是需求记录，不是已实现并验收的固件功能。

## 7. 问题与经验

|问题/表现|原因或范围|有效处理与后续限制|
|---|---|---|
|初版外壳/丝印重叠，焊盘 DRC 没报全|铜间距不能代表可装配性|读实际封装边界并重排，另做视觉检查|
|把 layout 当作仅摆放而提前停止|阶段范围判断不完整|用户明确要求重布局并连线，按最终布线快照验收|
|器件搜索首项不对应目标|多个近似型号|放置前核对型号、封装和必要引脚|
|同名标签可能悬空|标签必须真实接到引脚|读实际 pin/netlist，对照预期连接|
|参考文档有 API，但客户端不可用|本地版本兼容差异|autoRouting 未提供；DSN/JSON 导出曾返回 undefined，不作为最终依赖|
|规则覆盖 API 没有效果|旧客户端兼容问题|按已读原生格式修改并回读实际配置，不把 undefined 当成功|
|Windows Freerouting 原生 CLI 失败|2.5.0 的 ObstacleArea 序列化异常|改用同版本 JAR + JRE；原生 CLI 不是已验证成功路径|
|先布信号堵住电源脚|过孔/线路占用细间距引出通道|先固定电源、去耦、晶振，再重布信号|
|过孔创建成功但不导通|此环境默认原生字段不适用|核对后用 viaType=0、ruleName=null，并保留 0.30/0.60 mm 孔/外径，再查 DRC|
|外层 success=true，内层 applied=false|执行成功不等于接受写入|检查业务返回和保存结果，再读取工程确认|
|追加原生记录后丢末尾 PAD_NET|结尾分隔与换行处理不完整|逐行解析/序列化，保留每条尾竖线与最终换行，恢复并核对 191 项映射|
|固定 FILL 字段写入失败|当前客户端接受 fillStyle='SOLID'|不盲套其他版本枚举；按本机实际验证|
|覆铜重建 API 报 undefined/length|接口版本不兼容|本机几何避让后写固定 FILL，不能宣称动态覆铜成功|
|删除字符串使位号也消失|查询/删除影响属性显示相关对象|恢复 Designator 并核实 56 个可见，不再无筛选删除所有文字|
|创建数与按 ID 回读数不同|短线、重复/合并与返回行为要适配|以真实几何、网络及 DRC 验证，不把请求数当实际对象数|
|临时请求、回包和截图被覆盖|交互工作使用固定输出名|正式归档用最终命名和哈希，不用 eda_last.json 判断历史状态|

本会话 PCB API 坐标按 mil，mm=mil×0.0254；原理图按其 API 的 10mil 单位。原生规则即使显示 unit=mm，内部尺寸字段仍须按格式和回读值核对，不能猜单位。枚举也应按本机文档和实际版本验证。

## 8. 下一步计划

|优先级/类型|具体产出|验收标准|
|---|---|---|
|P0 修复/设计审查|原理图问题清单与修复；电机、电源、驱动校核|取得 ERC/DRC 可解释结果；记录额定/堵转电流与选型依据；变更后 PCB 同步并重验|
|P0 完善交付|含必要库资源的完整工程备份及生产资料候选|独立副本/另一工作区恢复，器件/网络一致；生产包对应最终版本|
|P1 完善流程|参数化的最小工具集|移除硬编码路径/工程 ID，增加目标保护、备份、业务返回检查和只读验证；新测试工程演练通过|
|P1 完善工程|地铜重算和变更流程|改线后清除/重算固定地铜，再通过 DRC、网络与视觉检查|
|P2 新增能力|固件最小工程和测试计划|键盘、OLED、RTC、EEPROM、驱动分模块调试；实测时序、报警、改密与掉电保存|
|P2 新增能力|样机与实测报告|完成制作后记录电流、温升、起振、复位、电机动作与异常|
|P3 业务扩展|接单报价交付模板、闲鱼或漫剧独立项目|分别立项，明确授权、输入、验收和成本；不写入当前已完成能力|

最值得先做的三项：**完整工程备份与恢复验证；原理图问题闭环和电机选型；脚本参数化及可重复的只读检查**。

## 9. GitHub 归档建议

### 9.1 简单目录（本次没有新建仓库）

~~~text
projects/gpt-easyeda-access-control/
  README.md
  docs/                 # 交接、需求、决策、问题与进度
  hardware/schematic/   # 核实过的原理图源/网表/导出
  hardware/pcb/         # 最终源、验收快照与预览
  scripts/              # 筛选和参数化后的项目脚本
  prompts/              # 使用边界与版本
  references/README.md  # 来源、用途、授权，不默认放课程原件
  validation/           # 检查结果与基准映射
~~~

通用脚本成熟后再提到仓库级 tools/。初期不加网站、数据库或复杂 CI。创建与推送前明确账号、仓库名、可见性，不能默认公开。本次没有核查 GitHub 登录状态或操作远程。

### 9.2 可直接用于 README 的介绍

> 本项目记录 AI 经本机桥服务操作嘉立创 EDA 专业版，辅助完成密码门禁原理图与 PCB 的过程。案例采用 STM32F103C8T6、外接矩阵键盘、I2C 显示/EEPROM、RTC 后备和双继电器电机输出。已形成保存的原理图与 PCB3，并保留 PCB 严格 DRC 通过及网络归属对照证据。仍需完成原理图电气问题闭环、具体电机选型、固件与实物验证；现有自动化是项目专用半自动工作流，不是通用一键产品。地铜为固定填充，变更后须重算。

### 9.3 排除与公开前审查

- 不提交真实密钥、Token、Cookie、账号凭据、.env、证书和私钥；配置示例只用占位符。
- 客户、课程或无公开授权的原件默认不入公开库，放不跟踪的 private/ 或外部受控存储。
- 排除 node_modules、__pycache__、临时请求、日志、下载缓存、JRE/JAR/EXE/安装包，依赖记版本与来源。
- 历史失败快照和 DSN/SES 若保留，须说明历史状态，不能作为最终交付。
- 公开前检查个人路径、工程标识、库资源、完整回包与截图；gitignore 不会清除已进入 Git 历史的内容。
- 不复制同目录桌面宠物项目的 src、根 package.json 和 .env.example。

以下仅是资料库配置建议，没有覆盖 C:\work 原有 gitignore：

~~~gitignore
.env
.env.*
!.env.example
*.pem
*.key
credentials/
secrets/
private/
customer-data/
node_modules/
__pycache__/
*.py[cod]
*.log
.cache/
tmp/
downloads/
~~~

### 9.4 第三方来源、用途与授权

|来源|用途|已知授权/归档方式|
|---|---|---|
|[easyeda-api-skill](https://github.com/easyeda/easyeda-api-skill)，[SKILL 声明](https://github.com/easyeda/easyeda-api-skill/blob/main/SKILL.md)|桥服务、API 与格式参考|本地及上游 SKILL 声明 MIT；保留来源/版权，分发内容按对应文件许可核对|
|[Run API Gateway](https://github.com/easyeda/eext-run-api-gateway)|EDA 网关|官方仓库标示 Apache-2.0，不改称自研|
|[Freerouting 2.5.0](https://github.com/freerouting/freerouting/releases/tag/v2.5.0)，[该版 LICENSE](https://github.com/freerouting/freerouting/blob/v2.5.0/LICENSE)|本机布线|GPL-3.0；记版本与来源，不默认提交发行二进制|
|[clipper-lib](https://github.com/junmer/clipper-lib)|多边形运算与偏置|本地 6.4.2 package 声明 BSL，README 标明 Boost Software License 1.0|
|[Eclipse Temurin](https://adoptium.net/temurin/)|运行 JAR|本地 25.0.5+8；分发许可按发行包复核，建议只记来源|
|[STM32 原厂手册](https://www.st.com/resource/en/datasheet/stm32f103v8.pdf)|MCU 参考|原厂资料，只记链接，不推定可任意再分发|
|[AP2112 原厂页](https://www.diodes.com/part/view/AP2112?BackID=9304)、[AO3400A 原厂页](https://www.aosmd.com/products/mosfets/low-voltage-mosfets-12v-30v/ao3400a)|原报告选型参考|本次没有重新核算全部电气参数；来源和授权分开记录|
|本地两份课程 PDF 与旧经验 MD|需求和经验|存在；公开/再分发许可待确认，默认不公开原件|

项目自身代码、设计与文档的对外许可尚未由用户选择，不自动套 MIT，也不从第三方许可推断整个项目授权。

## 附录：接续提示词

这是从已执行会话约束整理的**新归档版**，不是原始提示词逐字转录，也未在另一工程独立验证。原始长提示词在聊天中，未单独导出为原文文件。

~~~text
你是我的嘉立创 EDA 专业版操作助手。通过本机 bridge 操作 EDA。
先 GET /health，确认 edaConnected=true，再只读获取当前工程与文档。
先说明实际发现，不凭名称或旧缓存猜当前页，不直接运行历史批处理。

本案例参考 PROJECT_HANDOFF.md 和 PCB3_final_verified.json。
原理图为“密码门禁”p1，PCB 为 PCB3；先核对目标 UUID 和备份。
每次改动前检查 health，每次只做一小批，执行后回读实际结果再继续。
器件检索核对型号、封装和引脚；阻容用 0805，键盘为外接 4×4 接口。
原理图优先短引线和同名网络标签，但必须核对实际引脚网络归属。
PCB 同时看外形、丝印、板边、螺丝与插接空间，不以铜间距替代装配检查。
先电源、去耦和晶振，再布信号；按实际负载确定线宽和过孔。
API、枚举、单位按本机版本文档及回读确认，不支持的接口不假定成功。
外层 success=true 后仍检查内层 applied/保存结果。
最终汇报实际器件/网络、DRC、未连接、保存、人工检查和未验证项。
当前地铜固定填充，改线/移动器件后须重算；电机未选型，不保证额定载流。
默认先只读评审，拿到本次具体修改任务后再动工程。
~~~

## 需要我补充的信息

1. 电机型号、额定电压/电流、堵转电流、5V 电源能力和机械负载。
2. 实际键盘、PIR、OLED 的商品/数据手册、针序及电平，以及尚未给出的装配限制。
3. 用户是否在本对话外完成完整工程包、生产包、采购 BOM、固件、打样或实测；如有，提供已有位置和结果。
4. EDA About 的完整版本、Gateway 扩展版本与 AI 界面模型标签，现有可靠记录不足。
5. GitHub 账号、仓库名、可见性、项目自身许可，以及课程/参考/客户资料的公开授权范围。
