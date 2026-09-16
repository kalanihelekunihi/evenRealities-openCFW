# SPDX-License-Identifier: MIT
"""Record placement sizes for semantics-preserving compiler options."""
import subprocess,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'build/gx8002-backup-cosine';pre=str(root/'build/csky-macos/install/bin/csky-unknown-elf-')
flags=['-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections']
variants=[['-Os'],['-O2'],['-O3'],['-O1'],['-Os','-fno-schedule-insns'],['-Os','-fno-schedule-insns2'],['-Os','-fno-tree-ter'],['-Os','-fno-if-conversion'],['-Os','-fno-tree-dominator-opts'],['-Os','-fno-guess-branch-probability'],['-Os','-fno-cse-follow-jumps']]
results=[]
for i,v in enumerate(variants):
 obj=out/f'probe-{i}.o';elf=out/f'probe-{i}.elf'
 subprocess.run([pre+'gcc',*v,*flags,'-I',str(out),'-c',str(out/'csky_cos_f32.c'),'-o',str(obj)],check=True)
 subprocess.run([pre+'ld','-T',str(out/'cosine.ld'),str(obj),str(out/'table.o'),'-o',str(elf)],check=True)
 from build_transparent_image import Elf32
 e=Elf32(elf.read_bytes(),'probe');body=e.contents(next(s for s in e.sections if s['name']=='.cosine'));results.append({'flags':v,'bytes':len(body)})
print(results)
(root/'docs/research/gx8002-backup-cosine-compiler-probes.json').write_text(json.dumps(results,indent=2)+'\n')
