# SPDX-License-Identifier: MIT
"""Audit source allocations behind the backup denoise record callback."""
import json
from build_gx8002_backup_denoise_record_callback import ROOT,BINDINGS,Elf32,sha

def analyze():
    path=ROOT/'build/gx8002-backup-startup-cluster/cluster.elf'
    elf=Elf32(path.read_bytes(),'cluster');rows=[]
    for name,address in BINDINGS.items():
        symbols=[s['name'] for s in elf.symbols() if s['name'] and s['value']==address and s['section'] not in (0,0xfff1)]
        rows.append({'name':name,'address':address,'kind':'storage' if name=='backup_denoise_state' else 'function','allocated_symbols':symbols})
    result={'cluster_sha256':sha(path.read_bytes()),'dependencies':rows,'source_function_count':sum(r['kind']=='function' and bool(r['allocated_symbols']) for r in rows),
            'limits':['Allocated symbols establish linkage only, not nested execution, complete type recovery or hardware operation.',
                      'The record callback is source-linked in the startup cluster; this audit does not admit it into the complete firmware image.']}
    (ROOT/'docs/research/gx8002-backup-denoise-callback-dependencies.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(json.dumps(analyze(),indent=2))
