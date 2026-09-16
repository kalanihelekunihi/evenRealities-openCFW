# SPDX-License-Identifier: MIT
"""Audit source ownership of initializer bindings in the combined ELF."""
import json
from build_gx8002_backup_flash_interface import ROOT,BINDINGS
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import sha

def analyze():
    path=ROOT/'build/gx8002-backup-startup-cluster/cluster.elf';elf=Elf32(path.read_bytes(),'startup');symbols=elf.symbols();rows=[]
    for name,address in BINDINGS.items():
        match=next((s for s in symbols if s['name']==name),None)
        assert match is not None and match['value']==address,(name,match)
        owned=match['section'] not in (0,0xfff1)
        rows.append({'symbol':name,'address':address,'source_allocated':owned,'section_index':match['section']})
    report={'elf_sha256':sha(path.read_bytes()),'bindings':rows,'source_allocated_count':sum(r['source_allocated'] for r in rows),'total':len(rows),'limits':['Linkage inventory only: allocated source is not proof of complete nested behavior, device data closure or physical startup. Indirect dependencies outside this binding list remain.']}
    (ROOT/'docs/research/gx8002-backup-flash-initializer-dependencies.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(analyze(),indent=2))
