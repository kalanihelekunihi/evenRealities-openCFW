# SPDX-License-Identifier: MIT
"""Compare decoded normalization expression trees without reassociation."""
import json,subprocess
from build_gx8002_backup_imcra_state import ROOT
from verify_gx8002_memcpy_source import decode

def expression(code,start,end):
    r={};f={'fr2':0x38000000,'fr3':0x46800000};stack={};loads=0
    for pc in sorted(p for p in code if start<=p<end):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')]
        if op in ('ld.hs','ldbi.hs','ldr.h'):
            r[p[0]]=('signed_sample',loads);loads+=1
        elif op=='sexth':pass # both sample inputs already modeled signed
        elif op=='fmtvrl':f[p[0]]=r[p[1]]
        elif op=='fmfvrl':r[p[0]]=f[p[1]]
        elif op in ('fsitos','fstosi.rz','frecips'):f[p[0]]=(op,f[p[1]])
        elif op=='fmuls':f[p[0]]=(op,f[p[1]],f[p[2]])
        elif op=='fmacs':f[p[0]]=(op,f[p[0]],f[p[1]],f[p[2]])
        elif op=='fsts':stack[args.split(',',1)[1]]=f[p[0]]
        elif op=='flds':f[p[0]]=stack[args.split(',',1)[1]]
        else:raise AssertionError((hex(pc),op,args))
    assert loads==2
    return f['fr0']

def verify():
    out=ROOT/'build/gx8002-backup-imcra-state';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    raw=subprocess.check_output([pre,'-D','--start-address=0x46f6e','--stop-address=0x46fa2',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True)
    stock=expression(decode(raw),0x46f6e,0x46fa2)
    source=expression(decode((out/'state.disassembly.txt').read_text()),0x1000e718,0x1000e756)
    assert stock==source,(stock,source)
    report={'matching_expression':stock,'source_admitted':False,'limits':['One normalization iteration: signed sample inputs, explicit float operations and conversion. Stack save/reload modeled exactly. Loop bounds, physical FPU/reciprocal precision, exceptions and complete initializer behavior remain unqualified.']}
    (ROOT/'docs/research/gx8002-imcra-normalization-symbolic.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify())
