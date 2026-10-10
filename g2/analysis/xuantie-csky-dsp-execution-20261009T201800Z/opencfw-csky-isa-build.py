from pathlib import Path
import subprocess,json,hashlib
p=Path('g2/analysis/xuantie-csky-dsp-execution-20261009T201800Z');rows=json.loads((p/'harness-build-results.json').read_text());cmd=next(x['command'] for x in rows if '/out/harness.c' in x['command']);base=cmd[:cmd.index('/tool/bin/csky-abiv2-elf-gcc')];flags=cmd[cmd.index('/tool/bin/csky-abiv2-elf-gcc')+1:cmd.index('-c')];out=[]
for name in ['isa-main.c','isa-probes.S']:
 a=base+['/tool/bin/csky-abiv2-elf-gcc']+flags+['-c','/out/'+name,'-o','/out/'+name+'.o'];q=subprocess.run(a,capture_output=True,text=True);out.append({'command':a,'returncode':q.returncode,'stderr':q.stderr});assert q.returncode==0,q.stderr
cmd=base+['/tool/bin/csky-abiv2-elf-gcc','-mcpu=ck804ef','-mhard-float','-nostdlib','-nostartfiles','-Wl,-T,/out/harness.ld','-o','/out/isa.elf','/out/startup.o','/out/isa-main.c.o','/out/isa-probes.S.o'];q=subprocess.run(cmd,capture_output=True,text=True);out.append({'command':cmd,'returncode':q.returncode,'stderr':q.stderr});assert q.returncode==0,q.stderr;(p/'isa-build-results.json').write_text(json.dumps(out,indent=2)+'\n');print('ISA LINK',hashlib.sha256((p/'isa.elf').read_bytes()).hexdigest())
