#!/usr/bin/env python3
"""Compare three compiled SMP/WSF child bodies with authenticated stock ARM."""
from pathlib import Path
import subprocess, tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import *

R = Path(__file__).resolve().parents[3]
B = (R / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S = R / 'components/audio/uart_thread_source_candidate/display_ble_smp_action_children.c'
STUB = '''#include <stdint.h>
uint32_t call_log[12], call_count, alloc_result;
static void record(uint32_t k,uint32_t a,uint32_t b){uint32_t i=call_count++*3;call_log[i]=k;call_log[i+1]=a;call_log[i+2]=b;}
void *audio_ble_hci_msg_data_alloc(uint16_t a,uint8_t b){record(1,a,b);return (void *)alloc_result;}
void *WsfBufAlloc(uint16_t a){record(2,a,0);return (void *)alloc_result;}
void smpSmExecute(void *a,void *b){record(3,(uint32_t)a,(uint32_t)b);}
void audio_ble_wsf_timer_insert(void *a,uint32_t b){record(4,(uint32_t)a,b);}
'''
with tempfile.TemporaryDirectory() as tmp:
    t = Path(tmp); (t/'stub.c').write_text(STUB)
    elf=t/'candidate.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                    '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,smpMsgAlloc',
                    str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        e=ELFFile(f)
        segments=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
        symbols={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
    cases=[('msg',0x537bca,'smpMsgAlloc',0x345,0,0,0x20082000),
           ('alloc-ok',0x56cf04,'SmpScAlloc',0x31,0x20080000,0x20080100,0x20082000),
           ('alloc-fail',0x56cf04,'SmpScAlloc',0x31,0x20080000,0x20080100,0),
           ('timer',0x52a4b8,'WsfTimerStartSec',0x20080200,0x12345,0,0)]
    for label,native,c_name,a,b,c,ret in cases:
        pair=[]
        for compiled in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
            u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            for addr,data in segments:u.mem_write(addr,data)
            u.mem_write(0x20080100,bytes([0xa5]*16))
            if compiled:u.mem_write(symbols['alloc_result'],ret.to_bytes(4,'little'))
            observed=[]
            if not compiled:
                hooks={0x4bf990:1,0x530446:2,0x56ee62:3,0x52a424:4}
                def hook(uc,pc,size,user):
                    x=uc.reg_read(UC_ARM_REG_R0);y=uc.reg_read(UC_ARM_REG_R1)
                    observed.append((hooks[pc],x,y if hooks[pc] != 2 else 0))
                    if pc in (0x4bf990,0x530446):uc.reg_write(UC_ARM_REG_R0,ret)
                    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
                for addr in hooks:u.hook_add(UC_HOOK_CODE,hook,begin=addr,end=addr)
            u.reg_write(UC_ARM_REG_R0,a);u.reg_write(UC_ARM_REG_R1,b)
            u.reg_write(UC_ARM_REG_R2,c);u.reg_write(UC_ARM_REG_SP,0x200ff000)
            u.reg_write(UC_ARM_REG_LR,0x600001)
            u.emu_start((symbols[c_name] if compiled else native)|1,0x600000,count=3000)
            if compiled:
                val=lambda name:int.from_bytes(u.mem_read(symbols[name],4),'little')
                log=u.mem_read(symbols['call_log'],val('call_count')*12)
                observed=[tuple(int.from_bytes(log[i+j:i+j+4],'little') for j in (0,4,8))
                          for i in range(0,len(log),12)]
            result=u.reg_read(UC_ARM_REG_R0) if label!='timer' else None
            pair.append((result,bytes(u.mem_read(0x20080100,16)),observed))
        assert pair[0]==pair[1],(label,pair)
print('PASS_BLE_SMP_ACTION_CHILDREN_NATIVE 4')
