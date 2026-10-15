#!/usr/bin/env python3
"""Controlled native/C comparison of Apollo advertising resume and send wrapper."""
from pathlib import Path
import hashlib,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *

root=Path(__file__).resolve().parents[3]
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
src=root/'components/audio/uart_thread_source_candidate/display_ble_adv_resume.c'
stub='''#include <stdint.h>
volatile uint8_t audio_ble_adv_resume_state_20074f38[2];
uint32_t audio_ble_adv_route_ready_52c628(uint8_t a,uint8_t b){(void)a;(void)b;return 0;}
uint32_t audio_ble_att_write_request(uint8_t a,uint16_t b,uint8_t c,uint32_t d,uint32_t e,uint8_t f,uint8_t g){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;(void)g;return 0;}
'''
with tempfile.TemporaryDirectory() as directory:
    temp=Path(directory);st=temp/'stub.c';st.write_text(stub);elf=temp/'fixture.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-O2','-fno-inline','-nostdlib','-Wl,-Ttext=0x100000',
                    '-Wl,-e,audio_ble_dm_advertising_resume_4b5a44',str(src),str(st),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        obj=ELFFile(f)
        segments=[(s['p_vaddr'],s.data()) for s in obj.iter_segments() if s['p_type']=='PT_LOAD']
        symbols={s.name:s['st_value'] for s in obj.get_section_by_name('.symtab').iter_symbols()}
    cases=0
    for enabled in (0,1):
        for connection in (0,1,2,3):
            for ready_mask in (0,1,2,4,7):
                for route in (0,3):
                    pair=[]
                    for compiled in (False,True):
                        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
                        u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
                        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
                        u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
                        for addr,data in segments:u.mem_write(addr,data)
                        state=symbols['audio_ble_adv_resume_state_20074f38'] if compiled else 0x20074f38
                        u.mem_write(state,bytes([enabled,route]))
                        trace=[]
                        hooks=[('ready','audio_ble_adv_route_ready_52c628',0x52c628),
                               ('send','audio_ble_adv_send_533ebc',0x533ebc)]
                        for kind,symbol,native in hooks:
                            addr=symbols[symbol] if compiled else native
                            def hook(uc,pc,width,user,kind=kind):
                                r0,r1,r2,r3=(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
                                if kind=='ready':
                                    trace.append((kind,r0,r1))
                                    uc.reg_write(UC_ARM_REG_R0,1 if ready_mask & (1<<(r0-1)) else 0)
                                else:
                                    trace.append((kind,r0,r1,r2,bytes(uc.mem_read(r3,4))))
                                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
                            u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
                        u.reg_write(UC_ARM_REG_SP,0x200ff000)
                        u.reg_write(UC_ARM_REG_LR,0x600001)
                        for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),
                                             (connection,0x1234,0xabcd,0x87654321)):
                            u.reg_write(reg,value)
                        try:u.emu_start((symbols['audio_ble_dm_advertising_resume_4b5a44'] if compiled else 0x4b5a44)|1,0x600000,count=5000)
                        except Exception as err:raise AssertionError((enabled,connection,ready_mask,route,compiled,hex(u.reg_read(UC_ARM_REG_PC)),trace)) from err
                        pair.append((trace,u.reg_read(UC_ARM_REG_R0)))
                    assert pair[0]==pair[1],(enabled,connection,ready_mask,route,pair)
                    cases+=1
    for connection in (1,3):
        pair=[]
        for compiled in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
            u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            for addr,data in segments:u.mem_write(addr,data)
            u.mem_write(0x20071000,b'ABCD')
            trace=[];addr=symbols['audio_ble_att_write_request'] if compiled else 0x533c6c
            def hook(uc,pc,width,user):
                regs=tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
                stack=struct.unpack('<IIII',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),16))
                trace.append((regs,stack[:3],bytes(uc.mem_read(stack[0],4))))
                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
            u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
            for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),
                                 (connection,0x12,4,0x20071000)):u.reg_write(reg,value)
            u.emu_start((symbols['audio_ble_adv_send_533ebc'] if compiled else 0x533ebc)|1,0x600000,count=2000)
            pair.append(trace)
        assert pair[0]==pair[1],(connection,pair)
        cases+=1
print('PASS_DISPLAY_BLE_ADV_RESUME_NATIVE',cases)
