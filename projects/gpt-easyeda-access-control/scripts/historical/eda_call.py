import json, urllib.request, urllib.error, pathlib, sys, time
BASE='http://127.0.0.1:49620'
def call(code):
    h=json.load(urllib.request.urlopen(BASE+'/health'))
    if not h.get('edaConnected'): raise RuntimeError('EDA disconnected')
    req=urllib.request.Request(BASE+'/execute',data=json.dumps({'code':code}).encode(),headers={'Content-Type':'application/json'})
    try: r=json.load(urllib.request.urlopen(req,timeout=45))
    except urllib.error.HTTPError as e:
        print(e.read().decode()); raise
    pathlib.Path('C:/work/eda_last.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(r,ensure_ascii=False,indent=2))
    if not r.get('success'): raise RuntimeError('execute failed')
    return r.get('result')
if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    call(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8-sig'))
