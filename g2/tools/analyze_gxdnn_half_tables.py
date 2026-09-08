#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare pinned upstream source tables with reference objects; no firmware output."""
import json,re,struct,hashlib,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
COMMIT='207ee58595a64b5c4a70df221f1e6e704b807811'
def analyze():
    repo=ROOT/'build/upstream-rocm-half';header=repo/'include/half.hpp'
    source=subprocess.check_output(['git','-C',str(repo),'show',COMMIT+':include/half.hpp'])
    if source!=header.read_bytes():raise ValueError('header checkout mismatch')
    inventory=json.loads((ROOT/'docs/research/gx8002-gxdnn-cmodel-inventory.json').read_text())
    pin=next(m['sha256'] for m in inventory['members'] if m['name']=='float16.o')
    data=(ROOT/'build/gxdnn-analysis/float16.o').read_bytes()
    if hashlib.sha256(data).hexdigest()!=pin:raise ValueError('reference object hash')
    shoff=struct.unpack_from('<Q',data,40)[0];entsize,num,names=struct.unpack_from('<HHH',data,58)
    sections=[struct.unpack_from('<IIQQQQIIQQ',data,shoff+i*entsize) for i in range(num)]
    s=sections[names];strings=data[s[4]:s[4]+s[5]];rows=[]
    for name,width in (('base_table',2),('shift_table',1),('mantissa_table',4),('exponent_table',4),('offset_table',2)):
        match=re.search(r'\b'+name+r'\[\d+\]\s*=\s*\{([^}]+)\}',source.decode(),re.S)
        if not match:raise ValueError('source array missing '+name)
        values=[int(v.strip(),0) for v in match[1].split(',') if v.strip()]
        payload=b''.join(v.to_bytes(width,'little') for v in values)
        candidates=[]
        for sec in sections:
            section_name=strings[sec[0]:].split(b'\0',1)[0].decode()
            if section_name.endswith(name) and section_name.startswith('.rodata.'):
                candidates.append(data[sec[4]:sec[4]+sec[5]])
        if len(candidates)!=1:raise ValueError('reference array ambiguous '+name)
        rows.append({'name':name,'bytes':len(payload),'source_sha256':hashlib.sha256(payload).hexdigest(),'matches_reference':payload==candidates[0]})
    return {'repository':'https://github.com/ROCm/half','commit':COMMIT,'header_sha256':hashlib.sha256(source).hexdigest(),'reference_object_sha256':pin,'tables':rows,'source_admitted':False,'limits':['Matching tables establish a source-family fingerprint, not exact historical release or complete rounding equivalence. Inspection only; tables are not copied into firmware.']}
if __name__=='__main__':
    r=analyze();(ROOT/'docs/research/gx8002-half-table-matches.json').write_text(json.dumps(r,indent=2)+'\n');print(r['tables'])
