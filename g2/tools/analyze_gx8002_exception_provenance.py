# SPDX-License-Identifier: MIT
"""Authenticate SDK exception sources and deployed frame/literal evidence."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,SDK_COMMIT,authenticated_blob,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode

def analyze():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';sources={}
    for rel in ('arch/soc/grus/trap_c.c','arch/soc/grus/vectors.S'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();data=authenticated_blob(sdk/rel,blob);sources[rel]={'blob':blob,'sha256':sha(data)}
        assert b'Licensed under the Apache License, Version 2.0' in data
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-D','--start-address=0x15604','--stop-address=0x15658',str(path)],text=True))
    expected={0x15604:('mfcr','r3, cr<0, 0>'),0x15608:('lsri','r3, r3, 16'),0x1560a:('sextb','r3, r3'),0x1560c:('br','0x1560c'),0x15610:('psrset','ee'),0x15628:('subi','r14, r14, 72'),0x1562a:('stm','r0-r12, (r14)'),0x15650:('bsr','0x15604'),0x15654:('br','0x15610')}
    for pc,pair in expected.items():assert code[pc][:2]==pair,(hex(pc),code[pc],pair)
    assert int.from_bytes(stock[0x15658:0x1565c],'little')==int.from_bytes(stock[0x1565c:0x15660],'little')==0x20027310
    return {'sdk_commit':SDK_COMMIT,'sources':sources,'stock_sha256':IMAGE_SHA,'package_offset':0x15604,'bytes':92,'region_sha256':sha(stock[0x15604:0x15660]),'frame_bytes':72,'saved_registers':['r0-r12','r13','r14','r15','epsr','epc'],'stock_stack_top_and_sp_slot':0x20027310,'upstream_reserved_stack_bytes':768,'candidate_stack_start':0x20027010,'source_admitted':False,'limits':['Source lineage and selected decoded frame/loop anchors, not complete compiled or symbolic equivalence. Stack interval inferred from SDK allocation and deployed top literal; ownership/startup must be verified.','Stock C handler is already an infinite loop after reading exception vector; retaining that behavior is not a substitute for reconstructing other functionality.']}
if __name__=='__main__':
    r=analyze();(ROOT/'docs/research/gx8002-exception-provenance.json').write_text(json.dumps(r,indent=2)+'\n');print('Exception source/frame provenance checked')
