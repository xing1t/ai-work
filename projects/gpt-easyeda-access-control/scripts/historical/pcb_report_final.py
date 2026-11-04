import json,pathlib,collections
root=pathlib.Path('C:/work');f=json.loads((root/'PCB3_final_verified.json').read_text(encoding='utf8'))['result'];rs=[]
for l in f['source'].splitlines():
 h,d=l.split('||');rs.append((json.loads(h),json.loads(d.rstrip('|'))))
counts=collections.Counter(h['type'] for h,d in rs);widths=collections.defaultdict(list)
for h,d in rs:
 if h['type']=='LINE' and d['layerId'] in [1,2]:widths[d['netName']].append(d['width']*.0254)
lines=['# PCB3 密码门禁：重布局与布线核对','', '已在原 PCB3 中重新布局、完成两层布线并保存。当前严格 DRC 返回 true，详细错误列表为空；全部网络连通。','', '- 板框：85 × 60 mm。','- 安装孔：四角 3.2 mm 非金属化孔，孔中心距相邻板边均为 3.5 mm；地铜在四角留出避让。','- 元件：56 个；41 个非空网络；191 个器件焊盘条目。','- 布线：638 段铜线、51 个 0.60/0.30 mm 过孔、顶底层各一块 GND 铜皮。','- 56 个位号均显示；电阻、电容封装全部为 0805。','- 所有器件焊盘的位号、引脚号及网络归属与导入时逐项一致。','- 根据实际封装丝印、焊盘及外形边界重排；器件间距规则设为 0.30 mm，当前无器件间距报错。','', '|区域|主要器件|','|---|---|','|主控、晶振、复位/启动|U1、Y1、Y2、C5–C14、R1–R3、SW1|','|3.3V 电源|U2、C1–C4|','|EEPROM、I2C 上拉|U3、C15、R4、R5|','|继电器及电机输出|K1、K2、Q1、Q2、D1、D2、R6–R9、C16、J6|','|蜂鸣器|BZ1、Q3、D3、R10、R11|','|照明和指示|D4、Q4、R12–R14、D5、R15|','|RTC 后备电池|BT1|','', '接口位置：J2 键盘在左侧；J3 PIR、J5 OLED 在上侧；J1 5V 输入在继电器之间靠上板边；J6 电机在右侧；J4 SWD 在下侧。','', '|网络|实际最小线宽 mm|实际最大线宽 mm|','|---|---:|---:|']
for net in ['5V','3V3','GND','MOTOR_A','MOTOR_B']:lines.append(f'|{net}|{min(widths[net]):.3f}|{max(widths[net]):.3f}|')
lines+=['', '电机主干为 1.50 mm，局部引出有 1.125 mm 收窄；继电器电源/回流主干为 1.50 mm。普通信号以 0.25 mm 为主，晶振与芯片电源脚附近使用 0.15–0.20 mm 短引出。','', '核对范围：当前规则下的铜箔间距、板边距离、线宽、过孔、网络一致性、连接及器件间距；DRC 通过并不等同于已验证整机功能、EMC 或电机堵转载流。','', '当前客户端的地铜重建接口不兼容，因此地铜采用经过几何避让计算的固定 GND 填充，带地焊盘散热连接及孤岛过滤。以后移动器件或修改走线，应重新计算这两块地铜；不要将其当作会自动更新的动态覆铜。','', '电机尚未选型：需按额定/堵转电流确认电源、继电器触点、连接器和电源/回流路径的能力，当前没有额定电流保证。','', '|位号|X mm|Y mm|旋转 °|','|---|---:|---:|---:|']
for p in sorted(f['parts'],key=lambda p:p['ref']):lines.append(f"|{p['ref']}|{p['x']*.0254:.2f}|{p['y']*.0254:.2f}|{p['rot']}|")
lines+=['','最终源文件：PCB3_final_source.txt；原始回读证据：PCB3_final_verified.json。',''];(root/'PCB3布局核对.md').write_text('\n'.join(lines),encoding='utf8');(root/'PCB3_layout_source.txt').write_text(f['source'],encoding='utf8');print('Updated final PCB layout and routing report; source backup refreshed.')
