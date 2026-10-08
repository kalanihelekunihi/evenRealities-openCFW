from pathlib import Path
import subprocess,json,shutil
N=Path('g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/iar-format-engine');C=Path('g2/components/bootloader/initializer_callbacks/iar_format_native');O=N/'current-evidence';O.mkdir(exist_ok=True)
for name in ['comparison.json','comparison.log']:shutil.copy2(Path('/tmp/opencfw-iar-format-canonical-qemu')/name,O/('qemu-'+name))
mutations=[('signed-zero','float_render.c','fraction&UINT64_C(0x7fffffffffffffff)','fraction'),('secure-n-consume','engine.c','constraint("printf_s: %n disallowed");return -1;','(*cursor)++;constraint("printf_s: %n disallowed");return -1;'),('callback-null','engine.c','if(!*context)return -1;','if(!*context)*context=(void *)1;'),('decimal-round','float_render.c',"count,'5','0','9'","count,'6','0','9'")]
rows=[]
for name,file,old,new in mutations:
 d=Path('/tmp/opencfw-iar-format-mutants')/name;d.mkdir(parents=True,exist_ok=True)
 for p in C.iterdir():
  if p.is_file():shutil.copy2(p,d/p.name)
 p=d/file;s=p.read_text();assert old in s;s=s.replace(old,new);p.write_text(s)
 out=d/'out';r=subprocess.run(['python3',str(N/'verify_qemu.py'),'--source-dir',str(d),'--output',str(out)],capture_output=True,text=True,timeout=90);assert r.returncode!=0,(name,r.stdout)
 receipt=json.loads((out/'comparison.json').read_text());assert receipt['status']=='FAIL';rows.append({'mutation':name,'comparison':receipt,'returncode':r.returncode});(O/(name+'-rejected.log')).write_text((out/'comparison.log').read_text());print('REJECTED',name,flush=True)
(O/'negative-controls.json').write_text(json.dumps(rows,indent=2)+'\n')
