from pcb_sexp import *
import json
current=json.loads((root/'pcb_priority_copper.json').read_text(encoding='utf8'))['result'];base=parse((root/'PCB3_rework.dsn').read_text());network=child(base,'network')
for c in children(network,'class'):
 if c[1] in ['P3V3','P5V']:child(child(c,'rule'),'width')[1]='250' if c[1]=='P3V3' else '500'
wiring=['wiring']
for l in current['source'].splitlines():
 h,d=l.split('||');h=json.loads(h);d=json.loads(d.rstrip('|'));net=d.get('netName')
 if h['type']=='LINE' and d['layerId'] in [1,2]:
  p=['path','Top' if d['layerId']==1 else 'Bottom',str(d['width']*25.4)]+[str(d[k]*25.4) for k in ['startX','startY','endX','endY']];wiring.append(['wire',p,['net',net],['type','protect']])
 if h['type']=='VIA':wiring.append(['via','Via600',str(d['centerX']*25.4),str(d['centerY']*25.4),['net',net],['type','protect']])
base[base.index(child(base,'wiring'))]=wiring;(root/'PCB3_priority.dsn').write_text(dump(base).replace('(string_quote QUOTE)','(string_quote ")')+'\n',encoding='utf8');print('Protected priority copper',len(wiring)-1)
