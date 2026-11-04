import json,pathlib,uuid
from eda_call import call
root=pathlib.Path('C:/work');planes=json.loads((root/'pcb_ground_planes.json').read_text());base=json.loads((root/'pcb_pour_source.json').read_text(encoding='utf8'))['result']['source'];padnets=[]
for l in base.splitlines():
 h,d=l.split('||');h=json.loads(h);d=json.loads(d.rstrip('|'))
 if h['type']=='PAD_NET':padnets.append({'h':h,'d':d})
payloads=[]
for p in planes:
 payloads.append({'id':uuid.uuid4().hex[:16],'data':{'partitionId':'','groupId':0,'netName':'GND','layerId':p['layer'],'width':.2,'fillStyle':'SOLID','path':p['path'],'locked':True,'zIndex':-1,'isBridgingCopper':False,'networkList':[],'refs':None}})
code='const padnets='+json.dumps(padnets)+';const fills='+json.dumps(payloads)+";const source=await eda.sys_FileManager.getDocumentSource();let rs=source.split(/\\r?\\n/).filter(Boolean).map(l=>{const i=l.indexOf('||');return {h:JSON.parse(l.slice(0,i)),d:JSON.parse(l.slice(i+2).replace(/\\|$/,''))};});rs=rs.filter(r=>!['PAD_NET','POURED','POUR'].includes(r.h.type));rs.push(...padnets);let ticket=Math.max(...rs.map(r=>r.h.ticket||0))+1;for(const p of fills)rs.push({h:{type:'FILL',id:p.id,ticket:ticket++},d:p.data});return {fills:fills.map(p=>p.id),padnets:padnets.length,applied:await eda.sys_FileManager.setDocumentSource(rs.map(r=>JSON.stringify(r.h)+'||'+JSON.stringify(r.d)+'|').join('\\n')+'\\n')};"
result=call(code);assert result['applied'], 'Source update rejected';call("return await eda.dmt_EditorControl.openDocument('567e6dbc306f8243');");call("return {drc:await eda.pcb_Drc.check(true,false,true),source:await eda.sys_FileManager.getDocumentSource()};");(root/'pcb_filled_check.json').write_text((root/'eda_last.json').read_text(encoding='utf8'),encoding='utf8')
