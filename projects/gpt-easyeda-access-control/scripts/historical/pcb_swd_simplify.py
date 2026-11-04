import json,pathlib
from eda_call import call
root=pathlib.Path('C:/work');r=json.loads((root/'pcb_swd_power_drc.json').read_text(encoding='utf8'))['result'];ids=r['ids'];pts=[[33.19018,4.0005],[33.2,7.6],[26.6,14.2],[26.6,22.8],[27.2,23.4]]
call('const ids='+json.dumps(ids)+';return await eda.pcb_PrimitiveLine.delete(ids);')
call('const pts='+json.dumps(pts)+";const ids=[];for(let i=1;i<pts.length;i++){const p=await eda.pcb_PrimitiveLine.create('3V3',2,pts[i-1][0]/.0254,pts[i-1][1]/.0254,pts[i][0]/.0254,pts[i][1]/.0254,.25/.0254);ids.push(p.getState_PrimitiveId());}return {ids,drc:await eda.pcb_Drc.check(true,false,true)};");(root/'pcb_swd_short_drc.json').write_text((root/'eda_last.json').read_text(encoding='utf8'),encoding='utf8')
