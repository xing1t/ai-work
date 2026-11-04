import re,json,pathlib,collections
root=pathlib.Path('C:/work')
def parse(text):
 text=text.replace('(string_quote ")','(string_quote QUOTE)');tokens=re.findall(r'"(?:\\.|[^"\\])*"|[^\s()]+|[()]',text);stack=[];out=[]
 for t in tokens:
  if t=='(':v=[];(stack[-1] if stack else out).append(v);stack.append(v)
  elif t==')':stack.pop()
  else:stack[-1].append(t[1:-1] if t.startswith('"') else t)
 return out[0]
def children(node,key):return [v for v in node if isinstance(v,list) and v and v[0]==key]
def child(node,key):return next(iter(children(node,key)),None)
def dump(node):return '('+' '.join(dump(x) if isinstance(x,list) else ('"'+x+'"' if any(y.isspace() for y in x) or x=='' else x) for x in node)+')'
if __name__=='__main__':
 t=parse((root/'PCB3_routed.ses').read_text());out=child(t,'routes');print('ROOTS',[v[0] for v in t if isinstance(v,list)]);print('ROUTES',[v[:3] for v in out if isinstance(v,list)][:3]);nw=child(out,'network_out');print('NetNames',[n[1] for n in children(nw,'net')]);print('Wires/Vias',sum(len(children(n,'wire')) for n in children(nw,'net')),sum(len(children(n,'via')) for n in children(nw,'net')))
