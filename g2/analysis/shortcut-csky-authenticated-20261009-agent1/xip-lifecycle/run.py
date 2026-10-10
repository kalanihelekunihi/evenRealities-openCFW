from pathlib import Path
import os,json,hashlib,subprocess,re,sys
root=Path(__file__).resolve().parent;parent=root.parent;repo=parent.parents[2]
campaign=repo/'g2/build/pseudocode-first/20260930T190500Z';env=dict(os.environ,JAVA_HOME='/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
identity=json.loads((campaign/'identity.json').read_text());images={x['id']:x for x in map(json.loads,(campaign/'inventory/images.jsonl').open())}
for rec in [identity['bundle'],identity['components']['codec']]:assert sha(repo/rec['path'])==rec['sha256']
rec=images['binh_a_stage2_xip'];source=repo/rec['content_path'];assert sha(source)==rec['content_sha256'];data=source.read_bytes();lo,hi=rec['mapping_model']['source']['component_span'];assert data==(repo/identity['components']['codec']['path']).read_bytes()[lo:hi]
base=rec['mapping_model']['routes'][0]['expected_execution']['span'][0];assert base==0x10203004
(root/'mapping.json').write_text(json.dumps(rec['mapping_model'],indent=2)+'\n')
tools=campaign/'tools/csky-binutils-001/install/bin';launcher=parent/'private-install/support/analyzeHeadless';receipts=[];bodies=[]
jobs=[(0x102078a4,'LvpSystemInit'),(0x102085a4,'LvpInitMode'),(0x10208cd4,'LvpInitializeAppEvent'),(0x102085f8,'LvpModeTick'),(0x10208d48,'LvpAppEventTick'),(0x10207a7c,'LvpSystemDone')]
if '--callbacks' in sys.argv:
 jobs=[(0x10208634,'IdleInit'),(0x10208624,'IdleDone'),(0x1020861c,'IdleTick'),(0x10208620,'IdleBuffer'),(0x10208670,'TwsInit'),(0x1020864c,'TwsDone'),(0x10026358,'TwsTick'),(0x10208644,'TwsBuffer'),(0x10208ca0,'AppSuspend'),(0x10208c7c,'AppResume'),(0x10208c98,'WatchdogCallback'),(0x10206f9c,'QueueInit'),(0x10206fb0,'QueueGet')]
if '--app' in sys.argv:
 jobs=[(0x10208e4c,'SampleAppInit'),(0x10208f04,'SampleAppEventResponse'),(0x102091bc,'SampleAppTaskLoop'),(0x10208dec,'SampleAppSuspend'),(0x10208dcc,'SampleAppResume')]
for start,name in jobs:
 rec=images['binh_a_stage2_sram' if start<0x10200000 else 'binh_a_stage2_xip'];source=repo/rec['content_path'];assert sha(source)==rec['content_sha256'];data=source.read_bytes();lo,hi=rec['mapping_model']['source']['component_span'];assert data==(repo/identity['components']['codec']['path']).read_bytes()[lo:hi];base=rec['mapping_model']['routes'][0]['expected_execution']['span'][0]
 stem=hex(start)[2:]
 commands=[('objdump',[str(tools/'csky-elfabiv2-objdump'),'-D','-z','-b','binary','-m','csky','--adjust-vma='+hex(base),'--start-address='+hex(start),'--stop-address='+hex(min(base+len(data),start+0x1400)),str(source)]),('ghidra',[str(launcher),str(root),'Xip_'+stem,'-import',str(source),'-loader','BinaryLoader','-loader-baseAddr',hex(base),'-processor','CSKY_V2:LE:32:default','-noanalysis','-scriptPath',str(parent/'callees'),'-postScript','ExportCallee.java',hex(start)])]
 for kind,argv in commands:
  r=subprocess.run(argv,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);out=root/(stem+'-'+kind+'.txt');out.write_text(r.stdout);receipts.append({'argv':argv,'exit_code':r.returncode,'output':str(out.relative_to(repo)),'sha256':sha(out)});assert r.returncode==0
  if kind=='ghidra':
   ranges=re.findall(r'\[([0-9a-f]{8}), ([0-9a-f]{8})\]',next(x for x in r.stdout.splitlines() if '> BODY ' in x));spans=[]
   for a,b in ranges:
    a,b=int(a,16),int(b,16)+1;fa,fb=a-base,b-base;assert 0<=fa<fb<=len(data);spans.append({'runtime':[a,b],'child':[fa,fb],'codec':[lo+fa,lo+fb],'bytes':fb-fa,'sha256':hashlib.sha256(data[fa:fb]).hexdigest()})
   bodies.append({'image':rec['id'],'entry':start,'source_candidate':name,'image_sha256':rec['content_sha256'],'base':base,'spans':spans,'total_bytes':sum(x['bytes'] for x in spans),'decompile_completed':'DECOMPILE_COMPLETE true' in r.stdout,'qualification':'conditional reviewed direct-XIP or SRAM mapping; unresolved callee effects/dispatch remain partial'})
 suffix='-callbacks' if '--callbacks' in sys.argv else '-app' if '--app' in sys.argv else ''
 print(stem,name,flush=True);(root/('receipts'+suffix+'.json')).write_text(json.dumps(receipts,indent=2)+'\n');(root/('bodies'+suffix+'.json')).write_text(json.dumps(bodies,indent=2)+'\n')
