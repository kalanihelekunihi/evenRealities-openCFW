# SPDX-License-Identifier: MIT
"""Bounded entry, pool and SRAM-address census for the recovered binary64 unpack."""
import json,re,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode

def analyze():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    assembly=subprocess.check_output([pre,'-D','--start-address=0x3b940','--stop-address=0x4f9cc',str(wrapper)],text=True)
    code=decode(assembly);start,end=0x4afd4,0x4b0b8;branches=[];pools=[];words=[]
    for pc,(op,args,width) in code.items():
        if start<=pc<end:continue
        if op in ('br','bsr','bt','bf','bez','bnez','bnezad','bhz','blz','bhsz','blsz'):
            try:target=int(args.split(',')[-1].strip(),0)
            except ValueError:continue
            if start<=target<end:branches.append({'pc':pc,'target':target,'entry':target==start})
    for line in assembly.splitlines():
        m=re.match(r'\s*([0-9a-f]+):.*\blrw\s+.*//\s*([0-9a-f]+)\s',line)
        if m:
            pc,target=(int(x,16) for x in m.groups())
            if not start<=pc<end and start<=target<end:pools.append({'pc':pc,'pool':target})
    for base in (0x10003000,0x20003000):
        lo,hi=start-0x3b940+base,end-0x3b940+base
        for off in range(len(stock)-3):
            value=int.from_bytes(stock[off:off+4],'little')
            if lo<=value<hi:words.append({'offset':off,'value':value,'entry':value==lo})
    assert branches
    # Record interior findings for review; do not discard failed closure evidence.
    # The linear disassembler interprets the first two lookup bytes as BT.
    assert stock[0x4b3ec:0x4b3f1]==bytes(5*(i+1) for i in range(5))
    assert int.from_bytes(stock[0x3e1c8:0x3e1cc],'little')==0x10012aac
    assert code[0x3e18c][:2]==('lrw','r1, 0x10012aac')
    assert code[0x3e18e][:2]==('ldr.b','r2, (r1, r2 << 0)')
    assert code[0x3e186][:2]==('subi','r2, r3, 4')
    assert code[0x3e188][:2]==('cmphsi','r2, 5')
    assert code[0x3e18a][:2]==('bt','0x3e1c4')
    interior=[r for r in branches if not r['entry']]
    assert interior==[{'pc':0x4b3ec,'target':0x4aff6,'entry':False}]
    interior[0]['classification']='byte lookup data decoded as branch'
    assert all(r['entry'] or 'classification' in r for r in branches)
    result={'table_evidence':{'offset':0x4b3ec,'size':5,'formula':'5 * (index + 1), index 0..4','literal_offset':0x3e1c8,'load_pc':0x3e18e,'index_guard_pc':0x3e188},'stock_sha256':IMAGE_SHA,'stock_range':[start,end],'external_branches':branches,'external_literal_pools':pools,'stored_address_words':words,'source_admitted':False,
            'limits':['Mixed loaded-backup linear branch/pool census and whole-codec byte-offset scan through both SRAM address mappings. Computed entry paths and other mappings remain outside scope.']}
    (ROOT/'docs/research/gx8002-double-unpack-references.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(json.dumps(analyze(),indent=2))
