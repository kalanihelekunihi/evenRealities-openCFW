from pathlib import Path
import os,json,hashlib,subprocess,re
root=Path(__file__).resolve().parent; parent=root.parent; repo=parent.parents[2]
campaign=repo/'g2/build/pseudocode-first/20260930T190500Z'; env=dict(os.environ,JAVA_HOME='/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home')
identity=json.loads((campaign/'identity.json').read_text()); images={x['id']:x for x in map(json.loads,(campaign/'inventory/images.jsonl').open())}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for r in [identity['bundle'],identity['components']['codec']]:assert sha(repo/r['path'])==r['sha256']
codec=(repo/identity['components']['codec']['path']).read_bytes(); receipts=[];bodies=[]
jobs=[('binh_a_stage1',0x0fffffe8,s) for s in [0x10000a04,0x10000f14,0x1000092c,0x10000134,0x10000f04,0x10000a2c]]+[('binh_a_stage2_sram',0x10023400,s) for s in [0x10025a88,0x10024984,0x10025cbc,0x10026314]]
obj=campaign/'tools/csky-binutils-001/install/bin/csky-elfabiv2-objdump'; launcher=parent/'private-install/support/analyzeHeadless'
for image,base,start in jobs:
 rec=images[image]; source=repo/rec['content_path'];assert sha(source)==rec['content_sha256'];lo,hi=rec['mapping_model']['source']['component_span'];assert source.read_bytes()==codec[lo:hi]
 stem=hex(start)[2:];project='Callee_'+stem
 commands=[('objdump',[str(obj),'-D','-z','-b','binary','-m','csky','--adjust-vma='+hex(base),'--start-address='+hex(start),'--stop-address='+hex(min(base+source.stat().st_size,start+0x1000)),str(source)]),('ghidra',[str(launcher),str(root),project,'-import',str(source),'-loader','BinaryLoader','-loader-baseAddr',hex(base),'-processor','CSKY_V2:LE:32:default','-noanalysis','-scriptPath',str(root),'-postScript','ExportCallee.java',hex(start)])]
 for kind,argv in commands:
  r=subprocess.run(argv,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);out=root/(stem+'-'+kind+'.txt');out.write_text(r.stdout);receipts.append({'argv':argv,'exit_code':r.returncode,'output':str(out.relative_to(repo)),'sha256':sha(out)});assert r.returncode==0
  if kind=='ghidra':
   ranges=re.findall(r'\[([0-9a-f]{8}), ([0-9a-f]{8})\]',next(x for x in r.stdout.splitlines() if '> BODY ' in x)); spans=[]
   for a,b in ranges:
    a,b=int(a,16),int(b,16)+1;fa,fb=a-base,b-base;assert 0<=fa<fb<=source.stat().st_size;spans.append({'runtime':[a,b],'child':[fa,fb],'codec':[lo+fa,lo+fb],'bytes':fb-fa,'sha256':hashlib.sha256(source.read_bytes()[fa:fb]).hexdigest()})
   bodies.append({'image':image,'entry':start,'image_sha256':rec['content_sha256'],'base':base,'spans':spans,'total_bytes':sum(x['bytes'] for x in spans),'decompile_completed':'DECOMPILE_COMPLETE true' in r.stdout,'qualification':'conditional intended stage1 header-stripped or reviewed stage2 normal copy mapping; callee effects require review'})
 print(stem,flush=True)
 (root/'receipts.json').write_text(json.dumps(receipts,indent=2)+'\n');(root/'bodies.json').write_text(json.dumps(bodies,indent=2)+'\n')
