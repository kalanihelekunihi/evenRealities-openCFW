#!/usr/bin/env python3
"""Actual C/native BLE advertising init config, payload and effect order."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_adv_init.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_slave_registration_table[16],audio_ble_adv_name_buffer[80];
uint8_t *audio_ble_slave_mode_context;
uint32_t audio_uart_command_pending(void){return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t l,const char *m,const char *s,const char *f,uint32_t n,const char *t,...){(void)l;(void)m;(void)s;(void)f;(void)n;(void)t;}
uint32_t compressed_log_output(uint32_t n,const char *a,const char *b,...){(void)n;(void)a;(void)b;return 0;}
uint32_t g2_log_module_length(const char *p){uint32_t n=0;while(p[n])n++;return n;}
void AppAdvSetData(uint8_t l,uint8_t n,const uint8_t *p){(void)l;(void)n;(void)p;}
void DmDevSetRandAddr(const uint8_t *a){(void)a;}
void DmAdvSetAddrType(uint8_t a){(void)a;}
void AppAdvStart(uint8_t m){(void)m;}
void AppSetBondable(uint8_t b){(void)b;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_adv_init',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 native={'config':0x200003e0,'name':0x200003ec,'slot':0x20074330,'mode':0x4abe60,'flags':0x43d0ce,'log':0x43d574,'compact':0x43ce9e,'length':0x44a43c,'setdata':0x4b2cec,'random':0x4b304c,'addrtype':0x4b32b8,'start':0x4b2d22,'bond':0x4b467c}
 compiled={'config':sy['audio_ble_slave_registration_table'],'name':sy['audio_ble_adv_name_buffer'],'slot':sy['audio_ble_slave_mode_context'],'mode':sy['audio_uart_command_pending']&~1,'flags':sy['audio_log_flags']&~1,'log':sy['audio_log_extended']&~1,'compact':sy['compressed_log_output']&~1,'length':sy['g2_log_module_length']&~1,'setdata':sy['AppAdvSetData']&~1,'random':sy['DmDevSetRandAddr']&~1,'addrtype':sy['DmAdvSetAddrType']&~1,'start':sy['AppAdvStart']&~1,'bond':sy['AppSetBondable']&~1}
 for mode,flags in ((1,0),(0,0),(1,2),(0,1)):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for x,d in seg:u.mem_write(x,d)
   a=compiled if is_c else native;u.mem_write(a['config'],bytes([0xa5]*16));u.mem_write(a['name'],bytes([0]*80))
   u.mem_write(a['name']+0x38,b'abc\x00');u.mem_write(a['slot'],(0x20080000).to_bytes(4,'little'))
   calls=[];targets={a[k]:k for k in ('mode','flags','log','compact','length','setdata','random','addrtype','start','bond')}
   def hook(uc,pc,n,user):
    k=targets[pc]
    if k=='mode':uc.reg_write(UC_ARM_REG_R0,mode)
    elif k=='flags':uc.reg_write(UC_ARM_REG_R0,flags)
    elif k=='length':
     p=uc.reg_read(UC_ARM_REG_R0);calls.append(('length',p-a['name']))
     uc.reg_write(UC_ARM_REG_R0,len(bytes(uc.mem_read(p,32)).split(b'\0')[0]))
    elif k=='setdata':
     p=uc.reg_read(UC_ARM_REG_R2);calls.append(('setdata',uc.reg_read(UC_ARM_REG_R0)&255,uc.reg_read(UC_ARM_REG_R1)&255,p-a['name']))
    elif k=='random':calls.append(('random',uc.reg_read(UC_ARM_REG_R0)-0x20080000))
    elif k in ('addrtype','start','bond'):calls.append((k,uc.reg_read(UC_ARM_REG_R0)&255))
    elif k=='log':calls.append(('log',uc.reg_read(UC_ARM_REG_R0)&255,bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R3),20)).split(b'\0')[0]))
    else:calls.append(('compact',uc.reg_read(UC_ARM_REG_R0)))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for addr in targets:u.hook_add(UC_HOOK_CODE,hook,begin=addr,end=addr)
   u.reg_write(UC_ARM_REG_R0,0x20080020);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['audio_ble_adv_init'] if is_c else 0x46db04)|1,0x600000,count=3000)
   pair.append((calls,bytes(u.mem_read(a['config'],12))))
  assert pair[0]==pair[1],(mode,flags,pair)
print('PASS_BLE_ADV_INIT_NATIVE 4')
