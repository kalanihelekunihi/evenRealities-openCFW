# SPDX-License-Identifier: MIT
"""Measure complete source pack closure under bounded compiler options."""
import json,shlex,subprocess
from build_gx8002_backup_double_pack import build
from build_gx8002_backup_cfft import ROOT,Elf32,sha

def probe():
    baseline=build();base=ROOT/'build/gx8002-backup-double-pack'
    out=ROOT/'build/gx8002-pack-size-probe';out.mkdir(exist_ok=True)
    lib=ROOT/'build/csky-macos/gcc-build/csky-unknown-elf/libgcc'
    log=(base/'shift-rebuild.log').read_text();commands=[baseline['compile_command']]
    for name in ('_lshrdi3.o','_ashldi3.o'):
        lines=[line for line in log.splitlines() if ' -o '+name+' ' in line];assert len(lines)==1
        commands.append(shlex.split(lines[0]))
    options=[[],['-fno-caller-saves'],['-fno-tree-loop-optimize'],['-finline-small-functions'],['-fno-if-conversion'],['-fno-if-conversion2'],['-flto']]
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');rows=[]
    for index,extra in enumerate(options):
        objects=[]
        for j,original in enumerate(commands):
            cmd=['-Os' if v in ('-O2','-Os') else v for v in original];obj=out/f'{index}-{j}.o'
            for flag,target in [('-o',obj),('-MT',obj),('-MF',out/f'{index}-{j}.dep')]:cmd[cmd.index(flag)+1]=str(target)
            cmd+=extra;subprocess.run(cmd,cwd=lib,check=True);objects.append(obj)
        path=out/f'{index}.elf'
        linker=[pre+'gcc','-nostdlib','-Os','-flto','-Wl,-u,__pack_d,-u,__lshrdi3,-u,__ashldi3'] if '-flto' in extra else [pre+'ld']
        subprocess.run([*linker,'-T',str(base/'pack.ld'),*[str(p) for p in objects],'-o',str(path)],check=True)
        e=Elf32(path.read_bytes(),'probe');assert not any(s['name'] and s['section']==0 for s in e.symbols())
        rows.append({'extra_flags':extra,'bytes':sum(s['size'] for s in e.sections if s['flags']&2),'elf_sha256':sha(path.read_bytes()),'path':str(path.relative_to(ROOT))})
    result={'baseline_bytes':baseline['compiled_bytes'],'stock_bytes':400,'all_objects_size_optimized':True,'variants':rows,'source_admitted':False,'limits':['Size probes only. All shift helpers freshly compiled from upstream C; numerical and target execution qualification still required.']}
    (ROOT/'docs/research/gx8002-pack-size-probe.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(json.dumps(probe(),indent=2))
