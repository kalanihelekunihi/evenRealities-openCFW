#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Identify NPU accessor boundaries from masked object code and decoded calls."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
NAMES=['npu_get_over_cmd_addr','npu_get_mac_overflow_cmd_addr','npu_get_op_overflow_cmd_addr','npu_get_mcu_id','npu_get_mcu_struct_addr','npu_set_mcu_done','npu_reset','npu_set_task_head','npu_get_task_head','npu_get_base_addr','npu_get_cur_cmd_addr']
TARGETS={'reg_get_val':0x102055ec,'reg_set_val':0x102055f0,'reg_set_bit':0x102055cc}
def identify():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='drivers_lib/snpu/grus/snpu_regs.o';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();data=authenticated_blob(sdk/rel,blob);e=Elf32(data,rel);sec=next(s for s in e.sections if s['name']=='.sram_text');content=e.contents(sec);symbols=e.symbols();relocs=e.relocations(sec['index']);stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('NPU accessor stock')
    # Existing stock ELF is only a disassembly wrapper; authenticate its payload
    # by regenerating rather than trusting a previous run's file.
    import struct
    out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'npu-accessor-stock.elf';subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True);b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    dis=subprocess.check_output([pre+'objdump','-D','--start-address=0xc000','--stop-address=0x15414',str(w)],text=True);code=decode(dis);rows=[]
    for name in NAMES:
        symbol=next(s for s in symbols if s['name']==name);start,size=symbol['value'],symbol['size'];needle=content[start:start+size];calls=[];ignored=set()
        for rel in relocs:
            if start<=rel['offset']<start+size:
                helper=symbols[rel['symbol']]['name']
                if rel['type']!=19 or helper not in TARGETS or rel['addend']!=0:raise ValueError('NPU accessor unexpected relocation')
                off=rel['offset']-start;calls.append((off,helper));ignored.update(range(off,off+4))
        fixed=[i for i in range(size) if i not in ignored];matches=[]
        for offset in range(0xc000,0x15414-size+1,2):
            if not all(stock[offset+i]==needle[i] for i in fixed):continue
            checked=[]
            for off,helper in calls:
                instruction=code.get(offset+off)
                if instruction is None or instruction[0]!='bsr' or ((int(instruction[1],0)+0x101f6a74)&0xffffffff)!=TARGETS[helper]:break
                checked.append({'offset':off,'helper':helper,'runtime_target':TARGETS[helper]})
            else:matches.append({'package_offset':offset,'runtime_address':offset+0x101f6a74,'bytes':size,'sha256':sha(stock[offset:offset+size]),'calls':checked})
        rows.append({'symbol':name,'object_offset':start,'object_symbol_size':size,'matches':matches})
    report={'sdk_commit':SDK_COMMIT,'object':{'path':'drivers_lib/snpu/grus/snpu_regs.o','blob':blob,'sha256':sha(data)},'stock_sha256':IMAGE_SHA,'functions':rows,'source_admitted':False,'limits':['Identification only. Fixed bytes match and branch relocations resolve to known primitives; need envelope and behavior qualification before source replacement. No object bytes emitted.']}
    (ROOT/'docs/research/gx8002-npu-accessor-identification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(identify(),indent=2))
