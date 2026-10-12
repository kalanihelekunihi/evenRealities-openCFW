#!/usr/bin/env python3
"""Native/C firmware staging deinit RAM and logging effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_finalize.c'
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
void audio_file_heap_free(void *x){(void)x;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
void __aeabi_memclr(void *p,unsigned n){volatile unsigned char *q=p;for(unsigned i=0;i<n;i++)q[i]=0;}
void __aeabi_memclr4(void *p,unsigned n){volatile unsigned char *q=p;for(unsigned i=0;i<n;i++)q[i]=0;}
void __aeabi_memclr8(void *p,unsigned n){volatile unsigned char *q=p;for(unsigned i=0;i<n;i++)q[i]=0;}
''')
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_radio_finalize_52fc04',str(S),str(shim),'-o',str(e)],check=True)
 with e.open('rb') as f:
  x=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 count=0
 for buffer in (0,0x2007a000):
  for log_flags in (0,2):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in segments:u.mem_write(a,d)
    u.mem_write(0x2007494c,buffer.to_bytes(4,'little'))
    u.mem_write(0x20074950,(0x12345678).to_bytes(4,'little'))
    u.mem_write(0x200731f0,b'\xaa'*0x40);u.mem_write(0x2007348c,b'\xbb'*0x30)
    u.mem_write(0x20074958,b'\xcc'*16);u.mem_write(0x20075016,b'\xdd')
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    mapping={0x474d16:'free',0x43d0ce:'flags',0x43d574:'extended'} if not is_c else {sym[n]&~1:k for n,k in [('audio_file_heap_free','free'),('audio_log_flags','flags'),('audio_log_extended','extended')]}
    calls=[]
    def hook(uc,a,size,_):
     kind=mapping.get(a)
     if kind is None:return
     if kind=='free':calls.append((kind,uc.reg_read(UC_ARM_REG_R0)));ret=0
     elif kind=='flags':calls.append((kind,));ret=log_flags
     else:
      sp=uc.reg_read(UC_ARM_REG_SP);line=int.from_bytes(uc.mem_read(sp,4),'little');fmt=int.from_bytes(uc.mem_read(sp+4,4),'little')
      calls.append((kind,uc.reg_read(UC_ARM_REG_R0),line,bytes(uc.mem_read(fmt,64)).split(b'\0',1)[0]));ret=0
     uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((sym['audio_ble_hci_radio_finalize_52fc04'] if is_c else 0x52fc04)|1,0x600000,count=2000)
    ram=b''.join(bytes(u.mem_read(a,n)) for a,n in ((0x2007494c,8),(0x200731f0,0x40),(0x2007348c,0x30),(0x20074958,16),(0x20075016,1)))
    pair.append((calls,ram))
   assert pair[0]==pair[1],(buffer,log_flags,pair)
   count+=1
 print('PASS_RADIO_FINALIZE_NATIVE',count)
