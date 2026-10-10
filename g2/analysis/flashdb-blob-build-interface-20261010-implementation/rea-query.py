import asyncio,os,json
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
D=Path(__file__).parent.resolve()
async def main():
 env=dict(os.environ,REA_ANALYSIS_PROVIDER='ghidra',GHIDRA_INSTALL_DIR='/opt/homebrew/opt/ghidra/libexec',JAVA_HOME='/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home')
 async with stdio_client(StdioServerParameters(command='/opt/homebrew/bin/node',args=['/Users/kalani/Repos/rea/scripts/rea.mjs','mcp'],env=env)) as (r,w):
  async with ClientSession(r,w) as s:
   await s.initialize()
   try:
    for name,args in [('open_binary',{'path':str(D/'rea-thumb-view.elf'),'provider_id':'ghidra'}),('binary_overview',{}),('batch_decompile',{'addresses':['0054116e']})]:
     result=await s.call_tool(name,args);(D/('rea-'+name+'.json')).write_text(json.dumps({'arguments':args,'result':result.model_dump()},indent=2)+'\n');print(name,'error',result.isError,flush=True)
     if name=='open_binary' and result.isError:break
   finally:
    result=await s.call_tool('close_binary',{});(D/'rea-close.json').write_text(json.dumps(result.model_dump(),indent=2)+'\n');print('close',result.isError,flush=True)
asyncio.run(main())
