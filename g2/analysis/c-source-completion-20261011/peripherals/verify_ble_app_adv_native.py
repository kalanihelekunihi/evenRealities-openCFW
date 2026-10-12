#!/usr/bin/env python3
"""Compare compiled C/native advertising entry effects with intercepted children."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_app_adv_public.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_subsystem_link_state_200719c8[0x80];
const uint8_t *audio_ble_slave_registration_slot;
int appSlaveAdvMode(void){return 0;}
void appSlaveAdvStart(uint8_t n,const uint8_t *h,const uint8_t *i,const uint8_t *d,const uint8_t *m,uint8_t r,uint8_t mode){(void)n;(void)h;(void)i;(void)d;(void)m;(void)r;(void)mode;}
void appAdvStop(uint8_t n,const uint8_t *h){(void)n;(void)h;}
void appSetAdvType(uint8_t h,uint8_t t,uint16_t i,uint16_t d,uint8_t m,uint8_t r){(void)h;(void)t;(void)i;(void)d;(void)m;(void)r;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,AppAdvStart',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data(),v['p_memsz']) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 entry={'AppAdvStart':0x4b2d22,'AppAdvStop':0x4b2d62,'AppSetAdvType':0x4b2d7c}
 native_children={0x4b2bde:'mode',0x4b446a:'start',0x4b43fc:'stop',0x4b4510:'type'}
 compiled_children={sy['appSlaveAdvMode']&~1:'mode',sy['appSlaveAdvStart']&~1:'start',sy['appAdvStop']&~1:'stop',sy['appSetAdvType']&~1:'type'}
 for name in entry:
  for enabled in (0,1):
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
    u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d,n in seg:u.mem_write(a,d)
    state=(sy['audio_ble_subsystem_link_state_200719c8'] if compiled else 0x200719c8)
    slot=(sy['audio_ble_slave_registration_slot'] if compiled else 0x2007434c)
    cfg=0x20080000;u.mem_write(cfg,bytes([0x34,0x12,0x55,0x66,0x77,0x88,0x78,0x56,0x99,0xaa]))
    u.mem_write(slot,cfg.to_bytes(4,'little'));u.mem_write(state+0x57,b'\x09')
    calls=[];children=compiled_children if compiled else native_children
    def hook(uc,pc,n,user):
     kind=children[pc];sp=uc.reg_read(UC_ARM_REG_SP)
     if kind=='mode':uc.reg_write(UC_ARM_REG_R0,enabled)
     elif kind=='start':
      calls.append((kind,uc.reg_read(UC_ARM_REG_R0),bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1),1)),bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R2),2)),bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R3),2)),bytes(uc.mem_read(int.from_bytes(uc.mem_read(sp,4),'little'),1)),int.from_bytes(uc.mem_read(sp+4,4),'little'),int.from_bytes(uc.mem_read(sp+8,4),'little')))
     elif kind=='stop':calls.append((kind,uc.reg_read(UC_ARM_REG_R0),bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1),1))))
     else:calls.append((kind,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2),uc.reg_read(UC_ARM_REG_R3),int.from_bytes(uc.mem_read(sp,4),'little'),int.from_bytes(uc.mem_read(sp+4,4),'little')))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    for addr in children:u.hook_add(UC_HOOK_CODE,hook,begin=addr,end=addr)
    u.reg_write(UC_ARM_REG_R0,2 if name=='AppAdvStart' else 4)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.emu_start((sy[name] if compiled else entry[name])|1,0x600000,count=1000)
    result=(calls,bytes(u.mem_read(state+0x57,1)))
    if not compiled:reference=result
    else:assert result==reference,(name,enabled,reference,result)
print('PASS_BLE_APP_ADV_NATIVE 6')
