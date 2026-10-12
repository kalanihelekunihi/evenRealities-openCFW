#!/usr/bin/env python3
"""Direct native/C PMIC pump register read/write error tree."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_update_prepare.c'
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
int32_t audio_ble_radio_read_command_52ea28(void *x,uint32_t a,void *b,uint32_t c){(void)x;(void)a;(void)b;(void)c;return 0;}
int32_t audio_ble_radio_write_command_52eaf8(void *x,uint32_t a,const void *b,uint32_t c){(void)x;(void)a;(void)b;(void)c;return 0;}
void audio_ble_hci_boot_log_4733ee(const char *x,...){(void)x;}
''')
 e=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_radio_update_prepare_52ed34',str(S),str(shim),'-o',str(e)],check=True)
 with e.open('rb') as f:
  x=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 for fail_at in (0,1,2,3,4):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segments:u.mem_write(a,d)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x2007a000)
   ids={0x52ea28:'read',0x52eaf8:'write',0x4733ee:'log'} if not is_c else {sym[n]&~1:k for n,k in [('audio_ble_radio_read_command_52ea28','read'),('audio_ble_radio_write_command_52eaf8','write'),('audio_ble_hci_boot_log_4733ee','log')]}
   calls=[]
   def hook(uc,a,size,_):
    kind=ids.get(a)
    if kind is None:return
    r0,r1,r2,r3=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
    if kind=='log':calls.append(('log',bytes(uc.mem_read(r0,96)).split(b'\0',1)[0],r1))
    else:
     calls.append((kind,r0,r1,r3,int.from_bytes(uc.mem_read(r2,4),'little') if kind=='write' else None))
     if kind=='read':uc.mem_write(r2,(0x12345678).to_bytes(4,'little'))
    index=sum(c[0] in ('read','write') for c in calls)
    ret=7 if kind!='log' and index==fail_at else 0
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((sym['audio_ble_radio_update_prepare_52ed34'] if is_c else 0x52ed34)|1,0x600000,count=1000)
   pair.append((calls,u.reg_read(UC_ARM_REG_R0)))
  assert pair[0]==pair[1],(fail_at,pair)
 print('PASS_RADIO_UPDATE_PREPARE_NATIVE',5)
