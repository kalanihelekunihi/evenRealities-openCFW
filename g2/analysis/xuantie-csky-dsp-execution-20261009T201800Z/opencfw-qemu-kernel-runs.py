from pathlib import Path
import json,subprocess,hashlib
p=Path('/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/xuantie-csky-dsp-execution-20261009T201800Z');rows=[]
for label,file in [('kernel-smoke','smoke.elf'),('abs-oracle','abs-oracle.elf')]:
 sub=p/label;sub.mkdir();cmd=['/opt/homebrew/bin/docker','exec','--workdir','/out/'+label,'opencfw-qemu-csky-resume-20261009t201800','timeout','20s','/tmp/qbuild2/qemu-system-cskyv2','-M','smartl','-cpu','ck804ef','-nographic','-monitor','none','-kernel','/out/'+file,'-d','in_asm,int,guest_errors','-D','/out/'+label+'/qemu.log'];q=subprocess.run(cmd,capture_output=True,text=True,timeout=30);m=sub/'mem.log';row={'label':label,'command':cmd,'elf_sha256':hashlib.sha256((p/file).read_bytes()).hexdigest(),'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'memlog':m.read_text() if m.exists() else None};rows.append(row);print(label,q.returncode,row['memlog'],flush=True)
 if label=='kernel-smoke' and q.returncode!=0:break
(p/'kernel-executions.json').write_text(json.dumps(rows,indent=2)+'\n')
