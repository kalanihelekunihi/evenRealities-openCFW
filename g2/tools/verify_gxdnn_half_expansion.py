#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Exhaustive native upstream half-to-binary32 conversion comparison."""
import json,re,struct,subprocess
from analyze_gxdnn_half_tables import analyze,ROOT

def verify():
    pin=analyze()
    if not all(t['matches_reference'] for t in pin['tables']):raise ValueError('table mismatch')
    header=ROOT/'build/upstream-rocm-half/include/half.hpp';text=header.read_text()
    def table(name):
        match=re.search(r'\b'+name+r'\[\d+\]\s*=\s*\{([^}]+)\}',text,re.S)
        return [int(x.strip(),0) for x in match[1].split(',') if x.strip()]
    mantissa,exponent,offset=map(table,('mantissa_table','exponent_table','offset_table'))
    out=ROOT/'build/gxdnn-analysis';source=out/'half-expansion-probe.cpp';exe=out/'half-expansion-probe'
    source.write_text('''#include "half.hpp"
#include <cstdint>
#include <cstdio>
#include <cstring>
int main(){for(uint32_t i=0;i<65536;++i){float f=half_float::detail::half2float<float>(static_cast<uint16_t>(i));uint32_t bits;std::memcpy(&bits,&f,4);if(std::fwrite(&bits,4,1,stdout)!=1)return 1;}return 0;}
''')
    subprocess.run(['xcrun','clang++','-std=c++11','-O2','-I'+str(header.parent),str(source),'-o',str(exe)],check=True)
    raw=subprocess.check_output([str(exe)])
    if len(raw)!=65536*4:raise ValueError('native output size')
    for h in range(65536):
        wanted=(mantissa[offset[h>>10]+(h&1023)]+exponent[h>>10])&0xffffffff
        if struct.unpack_from('<I',raw,h*4)[0]!=wanted:raise ValueError(f'half expansion mismatch {h:04x}')
    return {'upstream':pin,'cases':65536,'source_admitted':False,'limits':['All input bit patterns match the authenticated reference table formula, including NaN payload bits. Native macOS source execution only, no x86 archive execution or NPU hardware proof.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-half-expansion-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
