from pathlib import Path
import json,shlex,urllib.request,urllib.parse
D=Path(__file__).parent.resolve();env={}
for line in Path('/Users/kalani/Repos/ghidra-mcp/.local/launch.env').read_text().splitlines():
 line=line.strip().removeprefix('export ')
 if '=' in line and not line.startswith('#'):
  k,v=line.split('=',1);env[k]=shlex.split(v)[0] if shlex.split(v) else ''
token=next(v for k,v in env.items() if 'TOKEN' in k)
def request(path,args,post=False):
 url='http://127.0.0.1:8089'+path
 if not post:url+='?'+urllib.parse.urlencode(args)
 req=urllib.request.Request(url,data=json.dumps(args).encode() if post else None,headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=45) as r:return dict(status=r.status,response=json.loads(r.read()))
 except Exception as e:return dict(error=type(e).__name__,detail=str(e))
if __import__('sys').argv[-1]=='open':
 result=request('/open_project',dict(path=str(D/'scratch/FlashDBBlobScratch.gpr'),headless='false',program='/ghidra-view.elf'),True);(D/'ghidra-open-receipt.json').write_text(json.dumps(result,indent=2)+'\n');print('Open response recorded')
elif __import__('sys').argv[-1]=='program':
 result=request('/open_program',dict(path='/ghidra-view.elf',auto_analyze=False),True);(D/'ghidra-program-receipt.json').write_text(json.dumps(result,indent=2)+'\n');print('Program open recorded')
else:
 for name,path,args in [('decompile','/force_decompile',dict(function='0x54116e',program='ghidra-view.elf')),('callees','/get_function_call_graph',dict(function='0x54116e',depth=1,direction='callees',program='ghidra-view.elf'))]:
  result=request(path,args);(D/('ghidra-'+name+'.json')).write_text(json.dumps(dict(arguments=args,**result),indent=2)+'\n');print(name,result.get('status',result.get('error')))
