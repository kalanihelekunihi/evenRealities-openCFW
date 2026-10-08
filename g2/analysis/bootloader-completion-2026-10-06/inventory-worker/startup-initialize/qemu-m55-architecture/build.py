"""Build only synthetic Cortex-M55 harness scenarios; no firmware outputs changed."""
from pathlib import Path
import json,subprocess,hashlib
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'AGENTS.md').exists())
b=json.loads((HERE/'build-inputs.json').read_text());t=Path('/tmp/opencfw-qemu-m55');t.mkdir(exist_ok=True);objs=[]
for name in b['files'][1:]:
 o=t/(Path(name).stem+'.o');subprocess.run(['clang',*b['flags'],'-c',str(ROOT/name),'-o',str(o)],check=True);objs.append(str(o))
rows=[]
for incoming,fp,own in [(0,f,o) for f in [0,1] for o in [0,1,2]]+[(1,1,o) for o in [0,1,2]]:
 tag=('incoming-fp' if incoming else 'fp' if fp else 'basic')+'-owner'+str(own);o=t/(tag+'-harness.o');elf=t/(tag+'.elf')
 subprocess.run(['clang',*b['flags'],'-DTEST_FP='+str(fp),'-DTEST_OWNERSHIP='+str(own),'-DTEST_FP_INCOMING='+str(incoming),'-c',str(ROOT/b['files'][0]),'-o',str(o)],check=True)
 subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','--gc-sections','-T',str(HERE/'module.ld'),'-o',str(elf),str(o),*objs],check=True)
 rows.append(dict(tag=tag,fp=fp,incoming_fp=incoming,ownership=own,elf=str(elf),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),objects=[str(o),*objs]))
(HERE/'scenario-inputs.json').write_text(json.dumps(rows,indent=2)+'\n')
