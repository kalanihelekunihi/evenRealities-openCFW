#!/usr/bin/env python3
"""Controlled native/C comparison of Apollo BLE master pair WSF path."""
from pathlib import Path
import hashlib,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *

root=Path(__file__).resolve().parents[3]
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
src=root/'components/audio/uart_thread_source_candidate/display_ble_master_pair_event.c'
stub='''#include <stdint.h>
volatile uint32_t audio_ble_master_pair_mode_cell_20000444;
uint8_t audio_ble_dm_handler_state[0x18];
void *WsfMsgAlloc(uint16_t n){(void)n;return 0;}
void WsfMsgSend(uint8_t h,void*m){(void)h;(void)m;}
void *audio_queue_copy_bytes(void*d,const void*s,uint32_t n){(void)s;(void)n;return d;}
'''
with tempfile.TemporaryDirectory() as directory:
    temp=Path(directory);st=temp/'stub.c';st.write_text(stub);elf=temp/'fixture.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-O2','-nostdlib','-Wl,-Ttext=0x100000',
                    '-Wl,-e,audio_ble_master_event_503b24',str(src),str(st),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        obj=ELFFile(f)
        segments=[(s['p_vaddr'],s.data()) for s in obj.iter_segments() if s['p_type']=='PT_LOAD']
        symbols={s.name:s['st_value'] for s in obj.get_section_by_name('.symtab').iter_symbols()}
    cases=0
    for mode in (0,1,2):
        for allocation in (False,True):
            for connection in (1,3,0xff):
                pair=[]
                for compiled in (False,True):
                    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
                    u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
                    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
                    u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
                    for addr,data in segments:u.mem_write(addr,data)
                    cell=symbols['audio_ble_master_pair_mode_cell_20000444'] if compiled else 0x20000444
                    dm=symbols['audio_ble_dm_handler_state'] if compiled else 0x20073b78
                    u.mem_write(cell,struct.pack('<I',0x20071000));u.mem_write(0x20071000,bytes([mode]))
                    u.mem_write(dm+0xc,b'\x42')
                    event=0x20072000;record=0x20073000;message=0x20080000
                    u.mem_write(event,bytes(range(32)))
                    u.mem_write(record,b'\xaa'*4+bytes([connection])+b'\xaa'*11)
                    u.mem_write(message,b'\xcc'*16)
                    trace=[]
                    hooks=[('alloc','WsfMsgAlloc',0x4bf99e),
                           ('copy','audio_queue_copy_bytes',0x439be4),
                           ('send','WsfMsgSend',0x4bf9ba)]
                    for kind,symbol,native in hooks:
                        addr=symbols[symbol] if compiled else native
                        def hook(uc,pc,width,user,kind=kind):
                            r0,r1,r2=(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
                            if kind=='alloc':trace.append((kind,r0));uc.reg_write(UC_ARM_REG_R0,message if allocation else 0)
                            elif kind=='copy':
                                data=bytes(uc.mem_read(r1,r2));trace.append((kind,r0-message,data,r2))
                                uc.mem_write(r0,data);uc.reg_write(UC_ARM_REG_R0,r0)
                            else:trace.append((kind,r0,r1==message,bytes(uc.mem_read(r1,16))))
                            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
                        u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
                    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
                    u.reg_write(UC_ARM_REG_R0,event);u.reg_write(UC_ARM_REG_R1,record)
                    try:u.emu_start((symbols['audio_ble_master_event_503b24'] if compiled else 0x503b24)|1,0x600000,count=5000)
                    except Exception as err:raise AssertionError((mode,allocation,connection,compiled,hex(u.reg_read(UC_ARM_REG_PC)),trace)) from err
                    pair.append((trace,bytes(u.mem_read(message,16))))
                assert pair[0]==pair[1],(mode,allocation,connection,pair)
                cases+=1
print('PASS_DISPLAY_BLE_MASTER_PAIR_NATIVE',cases)
