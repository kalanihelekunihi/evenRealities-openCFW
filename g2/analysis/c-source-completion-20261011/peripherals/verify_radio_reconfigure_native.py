#!/usr/bin/env python3
"""Native/C retry parent 0x4b480a, with authentic lower call ABI cuts."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_reconfigure.c'
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
void audio_ble_radio_configure_52e5ce(void *a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_ble_radio_tune_52e5f2(uint32_t a,uint32_t b){(void)a;(void)b;}
int32_t audio_ble_radio_attempt_52edf0(void *a,uint32_t b){(void)a;(void)b;return 0;}
void audio_ble_radio_commit_52eefa(void *a,uint32_t b){(void)a;(void)b;}
void audio_ble_radio_ready_44b0ae(void){}
int32_t audio_ble_radio_context_check_52e4b4(void *a){(void)a;return 0;}
void audio_ble_radio_dispatch_set_52edd8(uint32_t a){(void)a;}
void audio_ble_hci_boot_log_4733ee(const char *s,...){(void)s;}
''')
 e=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_radio_reconfigure_4b480a',str(S),str(shim),'-o',str(e)],check=True)
 with e.open('rb') as f:
  x=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 kinds={'config':(0x52e5ce,'audio_ble_radio_configure_52e5ce'),'tune':(0x52e5f2,'audio_ble_radio_tune_52e5f2'),'attempt':(0x52edf0,'audio_ble_radio_attempt_52edf0'),'commit':(0x52eefa,'audio_ble_radio_commit_52eefa'),'ready':(0x44b0ae,'audio_ble_radio_ready_44b0ae'),'check':(0x52e4b4,'audio_ble_radio_context_check_52e4b4'),'dispatch':(0x52edd8,'audio_ble_radio_dispatch_set_52edd8'),'log':(0x4733ee,'audio_ble_hci_boot_log_4733ee')}
 count=0
 for results in ((0,),(7,0),(7,8)):
  for cell0,cell1,cell2,cell3 in ((0,0,0,0),(3,5,7,9),(0xffffffff,0x100,0x2345,0xabcdef01)):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in segments:u.mem_write(a,d)
    for a,v in ((0x20074970,cell0),(0x2007496c,cell1),(0x20074968,cell2),(0x20074954,cell3)):u.mem_write(a,v.to_bytes(4,'little'))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    for reg,val in ((UC_ARM_REG_R0,0x2007a000),(UC_ARM_REG_R1,0x1234),(UC_ARM_REG_R2,0x5678),(UC_ARM_REG_R3,0xdeadbeef)):u.reg_write(reg,val)
    byaddr={(sym[n]&~1 if is_c else a):k for k,(a,n) in kinds.items()};events=[];attempts=[]
    def hook(uc,a,size,_):
     kind=byaddr.get(a)
     if kind is None:return
     r0,r1,r2=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]
     if kind=='log':events.append(('log',r1 if r0 in (0x7602d0,sym['audio_ble_hci_radio_reconfigure_fail_log_7602d0']) else 0))
     elif kind=='config':events.append((kind,r0,r1,r2))
     elif kind=='tune':events.append((kind,r0,r1))
     elif kind in ('attempt','commit'):events.append((kind,r0,r1))
     elif kind=='dispatch':events.append((kind,r0))
     else:events.append((kind,))
     ret=results[len(attempts)] if kind=='attempt' else 0
     if kind=='attempt':attempts.append(ret)
     uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((sym['audio_ble_hci_radio_reconfigure_4b480a'] if is_c else 0x4b480a)|1,0x600000,count=1000)
    pair.append((events,u.reg_read(UC_ARM_REG_R0)))
   assert pair[0]==pair[1],(results,cell0,cell1,cell2,cell3,pair)
   count+=1
 print('PASS_RADIO_RECONFIGURE_NATIVE',count)
