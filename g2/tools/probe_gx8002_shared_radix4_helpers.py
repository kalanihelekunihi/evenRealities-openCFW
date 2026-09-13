# SPDX-License-Identifier: MIT
"""Measure shared radix-4 helper inlining choices without changing source."""
import json,subprocess
from build_gx8002_backup_radix4 import ROOT,FLAGS,Elf32,sha

def probe():
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_radix4_shared.c';original=source.read_text()
    out=ROOT/'build/gx8002-shared-radix4-probes';out.mkdir(exist_ok=True);pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');rows=[]
    choices=((),('cross',),('add','sub'),('half_add','half_sub'),('sat16',),('cross','add','sub'),('load','store'),('add','sub','half_add','half_sub','cross'))
    for index,names in enumerate(choices):
        text=original
        for name in names:
            prefix='static int32_t ' if name=='sat16' else 'static void ' if name=='store' else 'static complex_q15 '
            target=prefix+name+'(';assert target in text
            text=text.replace(target,prefix.replace('static ','static __attribute__((noinline)) ')+name+'(')
        path=out/f'probe{index}.c';obj=out/f'probe{index}.o';path.write_text(text)
        subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-fno-caller-saves','-c',str(path),'-o',str(obj)],check=True)
        elf=Elf32(obj.read_bytes(),'probe');size=sum(s['size'] for s in elf.sections if s['flags']&2 and s['flags']&4)
        rows.append({'noinline':list(names),'code_bytes':size,'source_sha256':sha(text.encode())})
    report={'original_source_sha256':sha(source.read_bytes()),'probes':rows,'limits':['Object sizes only. Changes are probe copies, not qualified source replacements.']}
    (ROOT/'docs/research/gx8002-shared-radix4-helper-probes.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(probe()['probes'])
