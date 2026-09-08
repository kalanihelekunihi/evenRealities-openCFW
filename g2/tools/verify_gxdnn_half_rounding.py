#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare native macOS upstream conversion with decoded reference formula."""
import json,re,struct,subprocess
from analyze_gxdnn_half_tables import analyze,ROOT

def verify():
    pin=analyze()
    if not all(t['matches_reference'] for t in pin['tables']):raise ValueError('conversion table mismatch')
    header=ROOT/'build/upstream-rocm-half/include/half.hpp';text=header.read_text()
    def table(name):
        match=re.search(r'\b'+name+r'\[\d+\]\s*=\s*\{([^}]+)\}',text,re.S)
        return [int(x.strip(),0) for x in match[1].split(',') if x.strip()]
    base,shift=table('base_table'),table('shift_table')
    def reference(bits):
        index=bits>>23;mantissa=bits&0x7fffff;s=shift[index]
        h=(base[index]+(mantissa>>s))&0xffff
        inc=((mantissa>>(s-1))|int((index&255)==102))&int((h&0x7c00)!=0x7c00)
        inc&=int(bool(bits&((1<<(s-1))-1)))|h
        return (h+inc)&0xffff
    out=ROOT/'build/gxdnn-analysis';source=out/'half-rounding-probe.cpp';exe=out/'half-rounding-probe'
    source.write_text('''#define HALF_ROUND_TIES_TO_EVEN 1
#include "half.hpp"
#include <cstdio>
#include <cstring>
#include <cstdint>
int main(){ uint32_t bits; while(std::fread(&bits,4,1,stdin)==1){float value;std::memcpy(&value,&bits,4);uint16_t h=half_float::detail::float2half<std::round_to_nearest>(value);if(std::fwrite(&h,2,1,stdout)!=1)return 2;} return std::ferror(stdin)?1:0;}
''')
    subprocess.run(['xcrun','clang++','-std=c++11','-O2','-I'+str(header.parent),str(source),'-o',str(exe)],check=True)
    samples=set()
    for index in range(512):
        for m in (0,1,0x3fffff,0x400000,0x7ffffe,0x7fffff):samples.add((index<<23)|m)
        s=shift[index]
        for q in (0,1,2,127,511,1022,1023):
            center=(q<<s)+(1<<(s-1))
            for delta in (-1,0,1):
                if 0<=center+delta<=0x7fffff:samples.add((index<<23)|(center+delta))
    # Reproducible broad exponent/mantissa patterns beyond boundary probes.
    state=0x12345678
    for _ in range(100000):
        state=(state*1664525+1013904223)&0xffffffff;samples.add(state)
    samples=sorted(samples);raw=b''.join(struct.pack('<I',x) for x in samples)
    result=subprocess.run([str(exe)],input=raw,stdout=subprocess.PIPE,check=True).stdout
    if len(result)!=2*len(samples):raise ValueError('probe output size')
    for index,bits in enumerate(samples):
        actual=struct.unpack_from('<H',result,index*2)[0]
        if actual!=reference(bits):raise ValueError(f'rounding mismatch {bits:08x}')
    return {'upstream':pin,'cases':len(samples),'ties_to_even':True,'source_admitted':False,'limits':['Reference instruction-formula comparison, not executed x86 archive. Native source converter only; arithmetic and target NPU numeric behavior remain unqualified. NaN behavior preserved as observed, not independently corrected.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-half-rounding-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
