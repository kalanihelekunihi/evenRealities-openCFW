#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Authenticate the complete SDK hardware shim and compile its C recovery."""
import json, struct, subprocess
from analyze_gx8002_upstream_objects import ROOT, SDK_COMMIT, authenticated_blob, IMAGE, IMAGE_SHA, sha
from verify_gx8002_analog_source import FLAGS
from verify_gx8002_memcpy_source import decode
from build_transparent_image import Elf32
DELTA=0x101f6a74
FUNCTIONS=[('snpu_device_init',0xeb34,4),('snpu_device_exit',0xeb38,4),('snpu_request_irq',0xeb3c,16)]

def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    rel='drivers_lib/snpu/grus/snpu_hw.o';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
    data=authenticated_blob(sdk/rel,blob);e=Elf32(data,rel);section=next(s for s in e.sections if s['name']=='.sram_text');oracle=e.contents(section);symbols=e.symbols();relocs=e.relocations(section['index']);stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or len(oracle)!=76:raise ValueError('SNPU hardware identity')
    if len(relocs)!=1:raise ValueError('SNPU hardware relocation count')
    relocation=relocs[0]
    if relocation['offset']!=16 or relocation['type']!=19 or relocation['addend']!=0 or symbols[relocation['symbol']]['name']!='gx_request_irq':raise ValueError('SNPU hardware relocation identity')
    if any(stock[0xeb34+i]!=oracle[i] for i in range(76) if i not in range(16,20)):raise ValueError('SNPU hardware complete section mismatch')
    w=out/'snpu-device-stock.elf';subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True);b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0xeb34','--stop-address=0xeb80',str(w)],text=True))
    op,args,width=old[0xeb44]
    if op!='bsr' or ((int(args,0)+DELTA)&0xffffffff)!=0x1002553c:raise ValueError('SNPU IRQ relocation target')
    header_path='include/driver/gx_irq.h';header_blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+header_path],text=True).strip();header=authenticated_blob(sdk/header_path,header_blob)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_snpu_device.c';flags=['-Os',*FLAGS[1:]];obj=out/'snpu-device-candidate.o';subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(obj)],check=True)
    script=out/'snpu-device-candidate.ld';script.write_text('SECTIONS {\n'+''.join(f'.text.{n} {o+DELTA:#x} : {{ *(.text.open_cfw_gx8002_{n}) }}\n' for n,o,size in FUNCTIONS)+'}\nopen_cfw_gx8002_request_irq = 0x1002553c;\n')
    p=out/'snpu-device-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(obj),'-o',str(p)],check=True);compiled=Elf32(p.read_bytes(),str(p));rows=[]
    if any(s['name'] and s['section']==0 for s in compiled.symbols()):raise ValueError('SNPU hardware unresolved symbol')
    for name,offset,size in FUNCTIONS:
        original=next(s for s in symbols if s['name']==name)
        if original['value']!=offset-0xeb34 or original['section']!=section['index'] or original['size']>size:raise ValueError('SNPU hardware symbol boundary')
        used=original['size']
        if stock[offset+used:offset+size]!=bytes(size-used):raise ValueError('SNPU hardware padding')
        sec=next(s for s in compiled.sections if s['name']=='.text.'+name);payload=compiled.contents(sec)
        if compiled.relocations(sec['index']):raise ValueError('SNPU hardware unresolved relocation')
        rows.append({'symbol':'open_cfw_gx8002_'+name,'section_name':sec['name'],'package_offset':offset,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':size,'stock_sha256':sha(stock[offset:offset+size]),'fits':len(payload)<=size})
    (out/'snpu-device-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'sdk_commit':SDK_COMMIT,'oracle':{'path':rel,'blob':blob,'sha256':sha(data),'complete_section_bytes':76,'package_offset':0xeb34,'resolved_irq_target':0x1002553c},'irq_header':{'path':header_path,'blob':header_blob,'sha256':sha(header)},'source_sha256':sha(source.read_bytes()),'flags':flags,'regions':rows,'source_admitted':False,'limits':['Identification and linking only. Empty init/exit are authenticated original behavior, not replacement stubs. Need target ABI/IRQ forwarding qualification; original private signatures remain inferred.']}
    (ROOT/'docs/research/gx8002-snpu-device-linked-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
