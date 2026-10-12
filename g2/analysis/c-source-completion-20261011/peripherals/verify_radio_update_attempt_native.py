#!/usr/bin/env python3
"""Compare 0x52edf0 stock and compiled C update branch effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_update_attempt.c'
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint32_t audio_ble_radio_io_mode_52dd1c(uint32_t x){(void)x;return 0;}
void audio_ble_radio_alt_mode_52dd24(void){}
int32_t audio_ble_radio_recover_stop_52e8be(void *x){(void)x;return 0;}
int32_t audio_ble_radio_update_current_52e7c0(void *x){(void)x;return 0;}
void audio_ble_radio_update_prepare_52ed34(void *x){(void)x;}
int32_t audio_ble_radio_update_erase_52e9b4(void *x){(void)x;return 0;}
int32_t audio_ble_radio_update_write_52ebca(void *x,uint32_t y){(void)x;(void)y;return 0;}
int32_t audio_ble_radio_update_check_52ec84(void *x){(void)x;return 0;}
uint32_t g2_codec_pin_function(uint32_t x,uint32_t y){(void)x;(void)y;return 0;}
void audio_ble_hci_boot_log_4733ee(const char *s,...){(void)s;}
''')
 e=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_radio_attempt_52edf0',str(S),str(shim),'-o',str(e)],check=True)
 with e.open('rb') as f:
  x=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 children={'mode':(0x52dd1c,'audio_ble_radio_io_mode_52dd1c'),'alt':(0x52dd24,'audio_ble_radio_alt_mode_52dd24'),'stop':(0x52e8be,'audio_ble_radio_recover_stop_52e8be'),'current':(0x52e7c0,'audio_ble_radio_update_current_52e7c0'),'prepare':(0x52ed34,'audio_ble_radio_update_prepare_52ed34'),'erase':(0x52e9b4,'audio_ble_radio_update_erase_52e9b4'),'write':(0x52ebca,'audio_ble_radio_update_write_52ebca'),'check':(0x52ec84,'audio_ble_radio_update_check_52ec84'),'pin':(0x480f0c,'g2_codec_pin_function'),'log':(0x4733ee,'audio_ble_hci_boot_log_4733ee')}
 cases=[(0,0,0,0,0,0,0,0),(1,0,0,0,0,0,0,1),(0,7,0,0,0,0,1,0),(0,0,1,0,0,0,0,0),(0,0,0,7,0,0,1,1),(0,0,0,0,7,0,1,0),(0,0,0,0,0,7,1,1)]
 count=0
 for mode,stop,current,erase,write,check,force,prepare in cases:
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segments:u.mem_write(a,d)
   u.mem_write(0x20074230,(0x1234).to_bytes(4,'little'));u.mem_write(0x20074240,(0x5678).to_bytes(4,'little'));u.mem_write(0x20074f51,bytes([prepare]))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x2007a000);u.reg_write(UC_ARM_REG_R1,force)
   byaddr={(sym[n]&~1 if is_c else a):k for k,(a,n) in children.items()};events=[]
   def hook(uc,a,size,_):
    kind=byaddr.get(a)
    if kind is None:return
    r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
    if kind=='log':
     raw=bytes(uc.mem_read(r0,96)).split(b'\0',1)[0];events.append(('log',raw,r1 if b'%d' in raw else None))
    elif kind in ('write','pin'):events.append((kind,r0,r1))
    elif kind in ('alt',):events.append((kind,))
    else:events.append((kind,r0))
    ret={'mode':mode,'stop':stop,'current':current,'erase':erase,'write':write,'check':check}.get(kind,0)
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((sym['audio_ble_radio_attempt_52edf0'] if is_c else 0x52edf0)|1,0x600000,count=1000)
   pair.append((events,u.reg_read(UC_ARM_REG_R0)))
  assert pair[0]==pair[1],((mode,stop,current,erase,write,check,force,prepare),pair)
  count+=1
 print('PASS_RADIO_UPDATE_ATTEMPT_NATIVE',count)
