# SPDX-License-Identifier: MIT
"""Measure out-of-line saturation without changing the FFT source candidate."""
import json,subprocess
from build_gx8002_backup_split import ROOT,FLAGS,Elf32,sha

def probe():
    out=ROOT/'build/gx8002-split-saturation-probe';out.mkdir(exist_ok=True)
    original=ROOT/'components/shared/gx8002/runtime_gx8002_backup_split.c';source=original.read_text()
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');rows=[]
    for name,modified in (('baseline',source),('sat32_noinline',source.replace('static int32_t sat32','static __attribute__((noinline)) int32_t sat32')),('add_sat_noinline',source.replace('static int32_t add_sat','static __attribute__((noinline)) int32_t add_sat'))):
        path=out/(name+'.c');path.write_text(modified);sizes=[]
        for inverse in (0,1):
            obj=out/(name+str(inverse)+'.o')
            subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-fno-caller-saves','-DINVERSE='+str(inverse),'-c',str(path),'-o',str(obj)],check=True)
            elf=Elf32(obj.read_bytes(),name);sizes.append(sum(s['size'] for s in elf.sections if s['flags']&2 and s['flags']&4))
        rows.append({'variant':name,'code_bytes':sizes,'source_sha256':sha(modified.encode())})
    report={'original_source_sha256':sha(original.read_bytes()),'probes':rows,'limits':['Object-code size only; no source candidate modified and no behavior qualification.']}
    (ROOT/'docs/research/gx8002-split-saturation-size-probes.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(probe()['probes'])
