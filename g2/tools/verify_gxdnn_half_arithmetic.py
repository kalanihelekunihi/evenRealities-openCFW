#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Native reference checks using independent Python IEEE pack/unpack rounding."""
import hashlib,json,math,struct,subprocess
from analyze_gxdnn_half_tables import analyze,ROOT

def verify():
    pin=analyze()
    if not all(t['matches_reference'] for t in pin['tables']):raise ValueError('upstream conversion tables')
    source=ROOT/'tools/reference_gxdnn_half_arithmetic.cpp';exe=ROOT/'build/gxdnn-analysis/half-arithmetic-reference'
    subprocess.run(['xcrun','clang++','-std=c++11','-O2','-ffp-contract=off','-fno-fast-math','-I'+str(ROOT/'build/upstream-rocm-half/include'),str(source),'-o',str(exe)],check=True)
    values=[0,0x8000,1,0x8001,0x3ff,0x400,0x3bff,0x3c00,0x3c01,0x4000,0x7bff,0xfbff]
    pairs=[(a,b) for a in values for b in values];state=0x12345678
    for _ in range(30000):
        state=(state*1664525+1013904223)&0xffffffff;a=state&0xffff
        state=(state*1664525+1013904223)&0xffffffff;b=(state>>16)&0xffff
        if a&0x7c00!=0x7c00 and b&0x7c00!=0x7c00:pairs.append((a,b))
    cases=[];expected=[]
    for a,b in pairs:
        x=struct.unpack('<e',struct.pack('<H',a))[0];y=struct.unpack('<e',struct.pack('<H',b))[0]
        for op in range(4):
            if op==3 and y==0:continue
            z=x+y if op==0 else x-y if op==1 else x*y if op==2 else x/y
            z=struct.unpack('<f',struct.pack('<f',z))[0]
            try:h=struct.unpack('<H',struct.pack('<e',z))[0]
            except OverflowError:h=0xfc00 if z<0 else 0x7c00
            cases.append((op,a,b));expected.append(h)
    output=subprocess.check_output([str(exe)],input=b''.join(struct.pack('<HHH',*c) for c in cases))
    if len(output)!=2*len(cases):raise ValueError('arithmetic output length')
    mismatches=[]
    for i,(op,a,b) in enumerate(cases):
        actual=struct.unpack_from('<H',output,i*2)[0]
        if actual!=expected[i]:mismatches.append({'op':op,'a':a,'b':b,'expected':expected[i],'actual':actual})
    return {'upstream_commit':pin['commit'],'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'cases':len(cases),'mismatch_count':len(mismatches),'mismatches':mismatches[:32],'source_admitted':False,'limits':['Finite operand samples only; division by zero and NaNs excluded. Python binary64 arithmetic rounded through binary32 then binary16 is an independent check, not an exhaustive NPU oracle.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-half-arithmetic-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],r['mismatch_count'])
