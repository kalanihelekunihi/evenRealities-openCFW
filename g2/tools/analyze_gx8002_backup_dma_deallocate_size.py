# SPDX-License-Identifier: MIT
"""Reproducible macOS compiler-size probes for the pending DMA deallocator."""
import json,subprocess
from build_gx8002_backup_dma_deallocate import ROOT,build,Elf32,sha
from verify_gx8002_analog_source import FLAGS


def analyze():
    baseline=build();out=ROOT/'build/gx8002-backup-dma-deallocate'
    prefix=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_dma_deallocate.c'
    rows=[]
    for flag in ('-fno-tree-vrp','-fno-tree-ccp','-fno-tree-dominator-opts','-fno-tree-ter','-fno-schedule-insns','-fno-schedule-insns2','-fno-cse-follow-jumps','-fno-ipa-ra','-fno-expensive-optimizations'):
        command=[prefix+'gcc','-Os',*FLAGS[1:],flag,'-c',str(source),'-o',str(out/'size-probe.o')]
        subprocess.run(command,check=True)
        elf=Elf32((out/'size-probe.o').read_bytes(),'probe')
        size=sum(s['size'] for s in elf.sections if s['flags']&4)
        rows.append({'flag':flag,'executable_bytes':size,'fits_68_bytes':size<=68})
    report={'source_sha256':sha(source.read_bytes()),'baseline':baseline,'probes':rows,'conclusion':('Current source fits the stock envelope; explicit zero-extending byte loads remove redundant compiler extensions.' if baseline['fits'] else 'Current source exceeds the stock envelope; probe sizes do not establish equivalence.'),'limits':['Object sizes are diagnostic evidence, not executable equivalence or final-link qualification. No probe object is used by the firmware composition.']}
    (ROOT/'docs/research/gx8002-backup-dma-deallocate-size.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__':print(json.dumps(analyze(),indent=2))
