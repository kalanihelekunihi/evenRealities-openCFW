#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Record host special-value outputs, explicitly not hardware qualification."""
import hashlib,json,struct,subprocess
from verify_gxdnn_half_arithmetic import verify,ROOT

def observe():
    evidence=verify()  # Authenticates upstream and rebuilds the native source.
    if evidence['mismatch_count']:raise ValueError('finite arithmetic baseline')
    values=[0,0x8000,0x3c00,0xbc00,0x7c00,0xfc00,0x7c01,0x7e00,0xfe55]
    cases=[(op,a,b) for op in range(4) for a in values for b in values]
    data=subprocess.check_output([str(ROOT/'build/gxdnn-analysis/half-arithmetic-reference')],input=b''.join(struct.pack('<HHH',*c) for c in cases))
    if len(data)!=2*len(cases):raise ValueError('special output length')
    rows=[{'operation':op,'a':a,'b':b,'result':struct.unpack_from('<H',data,i*2)[0]} for i,(op,a,b) in enumerate(cases)]
    # Independent signed nonzero / signed zero rule, separate from NaN observations.
    checks=0
    for row in rows:
        if row['operation']==3 and row['a'] in (0x3c00,0xbc00) and row['b'] in (0,0x8000):
            if row['result']!=(((row['a']^row['b'])&0x8000)|0x7c00):raise ValueError('signed division by zero')
            checks+=1
    return {'source_sha256':evidence['source_sha256'],'upstream_commit':evidence['upstream_commit'],'cases':len(rows),'signed_division_zero_checks':checks,'observations':rows,'source_admitted':False,'limits':['Native macOS observations. Only four signed nonzero/zero results independently checked here; NaN payload/sign propagation and NPU behavior remain unqualified.']}
if __name__=='__main__':
    r=observe();(ROOT/'docs/research/gx8002-half-special-observations.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],r['signed_division_zero_checks'])
