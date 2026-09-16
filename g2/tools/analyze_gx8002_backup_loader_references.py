# SPDX-License-Identifier: MIT
"""Bounded stage-one loader references in both instruction/data aliases."""
import json,re,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode


def verify():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    start,end=0x396a0,0x39744;base=0x38954
    tool=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    asm=subprocess.check_output([tool,'-D',f'--start-address={base:#x}','--stop-address=0x3b938',str(wrapper)],text=True)
    branches=[];pools=[];words=[]
    for pc,(op,args,width) in decode(asm).items():
        if start<=pc<end:continue
        if op in ('br','bsr','bt','bf','bez','bnez','bnezad','bhz','blz','bhsz','blsz'):
            try:target=int(args.split(',')[-1].strip(),0)
            except ValueError:continue
            if start<=target<end:branches.append({'pc':pc,'target':target,'entry':target==start})
    for line in asm.splitlines():
        m=re.match(r'\s*([0-9a-f]+):.*\blrw\s+.*//\s*([0-9a-f]+)\s',line)
        if m:
            pc,target=(int(x,16) for x in m.groups())
            if not start<=pc<end and start<=target<end:pools.append({'pc':pc,'pool':target})
    for runtime in (0x10000000,0x20000000):
        low,high=start-base+runtime,end-base+runtime
        for off in range(len(stock)-3):
            value=int.from_bytes(stock[off:off+4],'little')
            if low<=value<high:words.append({'offset':off,'value':value,'entry':value==low})
    from analyze_gx8002_model_command_chain import analyze as command_chain, START
    commands=command_chain();classified=[]
    for off,operand,relative in ((0x192b0,'destination',16),(0x1aae8,'source',4)):
        command=next(row for row in commands['commands'] if START+row['offset']<=off<START+row['offset']+row['bytes'])
        assert off==START+command['offset']+relative
        assert command['operator']=='copy' and command['copy'][operand]=={'base_slot':1,'offset':3456}
        assert int.from_bytes(stock[off:off+4],'little')==0x10000d80
        classified.append({'offset':off,'classification':'encoded model tensor operand, not an absolute executable pointer','command_offset':START+command['offset'],'operand':operand,'base_slot':1,'tensor_offset':3456})
    boot_asm=subprocess.check_output([tool,'-D','--start-address=0xde8','--stop-address=0xe10',str(wrapper)],text=True)
    boot=decode(boot_asm)
    assert boot[0xdf6][:2]==('lrw','r2, 0x10001e60')
    assert boot[0xdf8][:2]==('ldr.w','r3, (r2, r3 << 2)')
    assert boot[0xdfc][:2]==('jmp','r3')
    assert boot[0xe04][:2]==('movi','r5, 2')
    table=[]
    for off in (0x1eb0,0x1eb4):
        value=int.from_bytes(stock[off:off+4],'little');assert value==0x10000db4
        assert value-0x10000000+0x50==0xe04
        table.append({'offset':off,'classification':'earlier boot-stage-one dispatch table entry','table_runtime':0x10001e60,'table_index':(off-0x1eb0)//4,'target_runtime':value,'target_boot_package_offset':0xe04,'indexed_load_pc':0xdf8,'indirect_jump_pc':0xdfc})
    return {'boot_dispatch_classifications':table,'cross_image_lifetime_resolved':False,'model_operand_classifications':classified,'unclassified_stored_offsets':[w['offset'] for w in words if w['offset'] not in (0x192b0,0x1aae8,0x1eb0,0x1eb4)],'stock_sha256':IMAGE_SHA,'range':[start,end],'stage1_vector_offset':base,'external_branches':branches,'external_literal_pools':pools,'stored_words':words,'source_admitted':False,'limits':['Linear stage-one branch/pool census and whole-package unaligned scan of instruction/data aliases. Computed targets and other mappings remain outside scope; candidates require classification.']}


if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-loader-references.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
