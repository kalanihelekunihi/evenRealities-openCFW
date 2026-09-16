# SPDX-License-Identifier: MIT
"""Measure initializer placement with ordinary semantics-preserving flags."""
import json,subprocess
from build_gx8002_backup_imcra_state import build,ROOT
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def probe():
    build();out=ROOT/'build/gx8002-backup-imcra-state';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_imcra_state_initialize.c'
    variants=[[],['-fno-tree-loop-optimize'],['-fno-ivopts'],['-fno-tree-ter'],['-fno-schedule-insns'],['-fno-schedule-insns2'],['-fno-crossjumping'],['-fno-tree-dominator-opts'],['-fno-guess-branch-probability'],['-fno-reorder-blocks'],['-fno-if-conversion'],['-fno-caller-saves']]
    rows=[]
    for i,extra in enumerate(variants):
        obj=out/f'probe-{i}.o';path=out/f'probe-{i}.elf'
        subprocess.run([pre+'gcc','-Os',*FLAGS[1:],*extra,'-c',str(source),'-o',str(obj)],check=True)
        subprocess.run([pre+'ld','-T',str(out/'state.ld'),str(obj),str(out/'messages.o'),'-o',str(path)],check=True)
        elf=Elf32(path.read_bytes(),'probe');section=next(s for s in elf.sections if s['name']=='.imcra_state');rows.append({'flags':extra,'bytes':section['size'],'fits':section['size']<=1024})
    (ROOT/'docs/research/gx8002-imcra-state-compiler-probes.json').write_text(json.dumps(rows,indent=2)+'\n');return rows
if __name__=='__main__':print(probe())
