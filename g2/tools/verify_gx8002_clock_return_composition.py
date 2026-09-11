# SPDX-License-Identifier: MIT
"""Decoded frequency epilogue composed with decoded divider leaf."""
import json
import subprocess
from itertools import product
from verify_gx8002_clock_frequency_return import ROOT,build_probe,build_getter,programs,decode,execute,PARAM,BASE,MASK
from verify_gx8002_clock_divider import build as build_divider,execute as divider,expected


def verify():
    candidate=build_probe();leaf=build_divider();build_getter();programs()
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    stock=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x16afc','--stop-address=0x1739a',str(stock)],text=True))
    outer=decode((ROOT/'build/gx8002-clock-frequency-size-probe/analysis.disassembly.txt').read_text())
    inner=decode((ROOT/'build/gx8002-board/clock-divider-candidate.disassembly.txt').read_text())
    count=0
    for use_source_outer,use_source_inner,present,shift,mask,word,frequency in product((False,True),(False,True),(False,True),(0,15,31),(0,0x3ff,0xffff),(0,1,MASK),(0,32000,98304000,MASK)):
        args=(present,BASE,0x80,shift,mask,word)
        want_reads,want_div=expected(*args)
        observed=[]
        def hook(param,base):
            if (param,base)!=(PARAM,BASE):raise ValueError('Composition arguments')
            reads,value=divider(inner if use_source_inner else old,0x10024ae8 if use_source_inner else 0x16afc,*args)
            observed.extend(reads)
            return value
        calls,result=execute(outer if use_source_outer else old,0x100252a6 if use_source_outer else 0x1738a,
                             0 if use_source_outer else 0x1000dfec,frequency,None,hook)
        if observed!=want_reads or calls!=[(PARAM,BASE)] or result!=(frequency//want_div if want_div else frequency):
            raise ValueError('Decoded return/divider composition mismatch')
        count+=1
    return {'candidate':candidate,'divider_candidate':leaf,'decoded_cases':count,'source_admitted':False,
            'limits':['Return slice and leaf use separate modeled register frames; valid entry/saved frame and descriptor assumed. Not whole-function ABI or hardware proof.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-clock-return-composition.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Decoded return/divider compositions:',report['decoded_cases'])
