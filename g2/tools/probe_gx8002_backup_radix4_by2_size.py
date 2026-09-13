# SPDX-License-Identifier: MIT
"""Non-mutating compiler size probes for the scalar butterfly candidates."""
import json,subprocess
from build_gx8002_backup_radix4_by2 import ROOT,sha,Elf32,FLAGS

def probe():
    out=ROOT/'build/gx8002-backup-radix4-by2/probes';out.mkdir(parents=True,exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_radix4_by2.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');rows=[]
    options=[(),('-fno-tree-loop-optimize',),('-fno-ivopts',),('-fno-tree-loop-optimize','-fno-ivopts'),('-fno-schedule-insns',),('-fno-schedule-insns2',),('-fno-tree-ter',),('-fno-tree-reassoc',),('-fno-caller-saves',),('-fomit-frame-pointer',)]
    for optimization in ('-Os','-O2'):
      for extra in options:
        sizes=[]
        for inverse in (0,1):
            flags=[optimization,*FLAGS[1:],*extra,'-DINVERSE='+str(inverse)]
            path=out/'probe.o';subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(path)],check=True)
            elf=Elf32(path.read_bytes(),'size probe');sizes.append(sum(s['size'] for s in elf.sections if s['flags']&2 and s['flags']&4))
        rows.append({'optimization':optimization,'extra_flags':list(extra),'bytes':sizes})
    report={'source_sha256':sha(source.read_bytes()),'probes':rows,'source_admitted':False,'limits':['Object section sizes only; no candidate flags selected or artifacts overwritten.']}
    (ROOT/'docs/research/gx8002-backup-radix4-by2-size-probes.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
    for r in sorted(probe()['probes'],key=lambda r:sum(r['bytes'])):print(r)
