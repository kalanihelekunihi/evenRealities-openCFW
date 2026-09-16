# SPDX-License-Identifier: MIT
"""Audit probe symbol linkage and remaining SPI object allocation gaps."""
import json
from build_gx8002_backup_dw_spi_probe import ROOT,BINDINGS,Elf32,sha

def analyze():
    path=ROOT/'build/gx8002-backup-startup-cluster/cluster.elf'
    elf=Elf32(path.read_bytes(),'startup');symbols=elf.symbols();rows=[]
    for name,address in BINDINGS.items():
        allocated=[s['name'] for s in symbols if s['value']==address and s['section'] not in (0,0xfff1) and s['name']]
        rows.append({'symbol':name,'kind':'storage' if name=='open_cfw_gx8002_backup_spi_master' else 'function','address':address,'allocated_source_symbols':allocated})
    objects=[]
    for name,address,size in [('fallback_device_state',0x20017670,16),('spi_master',0x20017680,36),('driver_context',0x200176a4,44)]:
        owners=[s['name'] for s in elf.sections if s['flags']&2 and s['size'] and s['address']<=address and address+size<=s['address']+s['size']]
        objects.append({'object':name,'address':address,'bytes':size,'allocated_sections':owners})
    result={'cluster_sha256':sha(path.read_bytes()),'dependencies':rows,'source_dependency_count':sum(bool(r['allocated_source_symbols']) for r in rows),'source_function_dependency_count':sum(r['kind']=='function' and bool(r['allocated_source_symbols']) for r in rows),'objects':objects,'limits':['Symbol/section ownership audit is not composed execution or hardware proof.','Driver context +36 meaning is unresolved; its 44-byte extent is corroborated by the authenticated upstream dwspi symbol (see context-layout report), not complete backup type recovery.']}
    (ROOT/'docs/research/gx8002-backup-spi-source-dependencies.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(json.dumps(analyze(),indent=2))
