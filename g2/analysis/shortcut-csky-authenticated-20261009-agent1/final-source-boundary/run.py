from pathlib import Path
import subprocess,os,json,re,hashlib
r=Path(__file__).resolve().parent;p=r.parent;repo=p.parents[2]
c=repo/'g2/build/pseudocode-first/20260930T190500Z';tools=c/'tools/csky-binutils-001/install/bin'
image=c/'reviews/codec-canonical-images-003/images/binh_a_stage2_xip.bin';data=image.read_bytes();base=0x10203004
assert hashlib.sha256(data).hexdigest()=='49c9aed0126493220a3e48827c267d5e94f64d51d9ede0ccc3e84b8946744584'
env=dict(os.environ,JAVA_HOME='/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home');rows=[]
for addr,name in [(0x10206d90,'LvpKwsInit'),(0x10206dac,'LvpKwsDone'),(0x102073f8,'LvpAudioInDone'),(0x10207660,'LvpAudioInStandbyToStartup'),(0x10207680,'LvpPmuInit'),(0x10208944,'LvpInitMaxKws'),(0x1020975c,'app_event_helper'),(0x10209770,'app_transition_helper')]:
 stem=f'{addr:08x}'
 for kind,argv in [('objdump',[tools/'csky-elfabiv2-objdump','-D','-z','-b','binary','-m','csky','--adjust-vma='+hex(base),'--start-address='+hex(addr),'--stop-address='+hex(addr+0x120),image]),('ghidra',[p/'private-install/support/analyzeHeadless',r,'Boundary_'+stem,'-import',image,'-loader','BinaryLoader','-loader-baseAddr',hex(base),'-processor','CSKY_V2:LE:32:default','-noanalysis','-scriptPath',p/'callees','-postScript','ExportCallee.java',hex(addr)])]:
  out=subprocess.run(list(map(str,argv)),env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);(r/(stem+'-'+kind+'.txt')).write_text(out.stdout);assert out.returncode==0,out.stdout
  if kind=='ghidra':
   ranges=re.findall(r'\[([0-9a-f]{8}), ([0-9a-f]{8})\]',next(x for x in out.stdout.splitlines() if '> BODY ' in x));spans=[]
   for a,b in ranges:
    a,b=int(a,16),int(b,16)+1;spans.append({'runtime':[a,b],'child':[a-base,b-base],'codec':[50576+a-base,50576+b-base],'bytes':b-a,'sha256':hashlib.sha256(data[a-base:b-base]).hexdigest()})
   rows.append({'entry':addr,'candidate':name,'spans':spans,'decompile_completed':'DECOMPILE_COMPLETE true' in out.stdout})
 (r/'bodies.json').write_text(json.dumps(rows,indent=2)+'\n');print(stem,name,flush=True)
sdk=repo/'third-party/upstream/nationalchip-lvp-kws'
out=subprocess.run([str(tools/'csky-elfabiv2-nm'),'-A','--defined-only',str(sdk/'lib/libdriver_release_v1.0.6.a')],stdout=subprocess.PIPE,text=True);(r/'driver-symbols.txt').write_text(out.stdout)
