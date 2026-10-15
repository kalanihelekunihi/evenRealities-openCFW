#!/usr/bin/env python3
"""Controlled native/C comparison of Apollo BLE master cache insert 0x503568."""
from pathlib import Path
import hashlib,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *

root=Path(__file__).resolve().parents[3]
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
src=root/'components/audio/uart_thread_source_candidate/display_ble_master_cache_insert.c'
stub='''#include <stdint.h>
volatile uint8_t audio_ble_subsystem_state_20071670[0xa0];
uint32_t audio_ble_master_mode_get_536a00(void){return 0;}
uint32_t audio_ble_privacy_compare_address(const uint8_t*a,const uint8_t*b){(void)a;(void)b;return 0;}
void audio_ble_copy_address6_4d293c(void*a,const void*b){(void)a;(void)b;}
'''
with tempfile.TemporaryDirectory() as directory:
    temp=Path(directory);st=temp/'stub.c';st.write_text(stub);elf=temp/'fixture.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-O2','-nostdlib','-Wl,-Ttext=0x100000',
                    '-Wl,-e,audio_ble_master_child_503568',str(src),str(st),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        obj=ELFFile(f)
        segments=[(s['p_vaddr'],s.data()) for s in obj.iter_segments() if s['p_type']=='PT_LOAD']
        symbols={s.name:s['st_value'] for s in obj.get_section_by_name('.symtab').iter_symbols()}
    cases=0
    for alternate in (0,1):
        for slot in (0,4,10):
            for duplicate in (False,True):
                for count in (0,3):
                    pair=[]
                    for compiled in (False,True):
                        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
                        u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
                        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
                        u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
                        for address,data in segments:u.mem_write(address,data)
                        state=symbols['audio_ble_subsystem_state_20071670'] if compiled else 0x20071670
                        message=0x20071000
                        source=bytearray(range(32));source[6]=3;source[0xb]=4
                        u.mem_write(message,bytes(source))
                        u.mem_write(state,b'\xaa'*0xa0)
                        for index in range(10):
                            row=state+index*15
                            u.mem_write(row+6,bytes([2 if index<slot else 0xff]))
                        if duplicate and slot<10:
                            row=state+slot*15
                            u.mem_write(row+6,bytes([4 if alternate else 3]))
                            u.mem_write(row,bytes(source[12:18] if alternate else source[7:13]))
                        u.mem_write(state+0x96,bytes([count]))
                        trace=[]
                        hooks=[('mode','audio_ble_master_mode_get_536a00',0x536a00),
                               ('compare','audio_ble_privacy_compare_address',0x4d294a),
                               ('copy','audio_ble_copy_address6_4d293c',0x4d293c)]
                        for kind,symbol,native in hooks:
                            addr=symbols[symbol] if compiled else native
                            def hook(uc,pc,width,user,kind=kind):
                                r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
                                if kind=='mode':trace.append((kind,));uc.reg_write(UC_ARM_REG_R0,alternate)
                                else:
                                    a=bytes(uc.mem_read(r0,6));b=bytes(uc.mem_read(r1,6))
                                    trace.append((kind,r0-state,r1-message,a,b))
                                    if kind=='compare':uc.reg_write(UC_ARM_REG_R0,1 if a==b else 0)
                                    else:uc.mem_write(r0,b)
                                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
                            u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
                        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
                        u.reg_write(UC_ARM_REG_R0,message);u.reg_write(UC_ARM_REG_R1,0x20072000)
                        try:u.emu_start((symbols['audio_ble_master_child_503568'] if compiled else 0x503568)|1,0x600000,count=12000)
                        except Exception as err:raise AssertionError((alternate,slot,duplicate,count,compiled,hex(u.reg_read(UC_ARM_REG_PC)),trace)) from err
                        pair.append((trace,bytes(u.mem_read(state,0xa0))))
                    assert pair[0]==pair[1],(alternate,slot,duplicate,count,pair)
                    cases+=1
print('PASS_DISPLAY_BLE_MASTER_CACHE_NATIVE',cases)
