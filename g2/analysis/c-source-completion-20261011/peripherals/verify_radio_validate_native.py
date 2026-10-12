#!/usr/bin/env python3
"""Native/C radio firmware header validation with log policy disabled."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_validate.c'
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
const char *audio_ble_radio_file_mode_52f3a0(uint32_t a){(void)a;return "r+";}
int32_t audio_ble_radio_file_size_52f3f8(void *a){(void)a;return 0;}
void *audio_file_open(const char *a,const char *b){(void)a;(void)b;return 0;}
uint32_t audio_file_read(void *a,uint32_t b,uint32_t c,void *d){(void)a;(void)b;(void)c;(void)d;return 0;}
int32_t audio_file_close(void *a){(void)a;return 0;}
''')
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_radio_validate_52fcfc',str(S),str(shim),'-o',str(e)],check=True)
 with e.open('rb') as f:
  x=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 cases=[('null',0,0,0),('open_fail',1,0,0),('size_fail',1,-1,0),('short',1,8,0),('read_short',1,16,8),('success',1,16,16)]
 count=0
 for label,valid,size,read in cases:
  log_flags=2 if label in ('null','success') else 0
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segments:u.mem_write(a,d)
   u.mem_write(0x2007b000,(0xaabbccdd).to_bytes(4,'little'))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x2007b000 if valid else 0)
   native={0x43d0ce:'flags',0x43d574:'extended',0x52f3a0:'mode',0x474550:'open',0x52f3f8:'size',0x474634:'read',0x4745f4:'close'}
   source={sym[n]&~1:k for n,k in [('audio_log_flags','flags'),('audio_log_extended','extended'),('audio_ble_radio_file_mode_52f3a0','mode'),('audio_file_open','open'),('audio_ble_radio_file_size_52f3f8','size'),('audio_file_read','read'),('audio_file_close','close')]}
   events=[]
   def hook(uc,a,sz,_):
    kind=(source if is_c else native).get(a)
    if kind is None:return
    r0,r1,r2,r3=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
    if kind=='flags':events.append((kind,));ret=log_flags
    elif kind=='mode':events.append((kind,r0));ret=(sym['audio_ble_radio_file_mode_52f3a0'] if False else 0x2007c000);uc.mem_write(0x2007c000,b'r+\0')
    elif kind=='open':events.append((kind,bytes(uc.mem_read(r0,40)).split(b'\0',1)[0],bytes(uc.mem_read(r1,4)).split(b'\0',1)[0]));ret=0 if label=='open_fail' else 0x2007a000
    elif kind=='size':events.append((kind,r0));ret=size
    elif kind=='read':events.append((kind,r1,r2,r3));uc.mem_write(r0,bytes.fromhex('112233445566778899aabbccddeeff00'));ret=read
    elif kind=='close':events.append((kind,r0));ret=0
    elif kind=='extended':
     sp=uc.reg_read(UC_ARM_REG_SP);line=int.from_bytes(uc.mem_read(sp,4),'little');fmt=int.from_bytes(uc.mem_read(sp+4,4),'little')
     events.append((kind,r0,bytes(uc.mem_read(r1,24)).split(b'\0',1)[0],line,
                    bytes(uc.mem_read(fmt,128)).split(b'\0',1)[0]));ret=0
    else:events.append((kind,));ret=0
    uc.reg_write(UC_ARM_REG_R0,ret&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((sym['audio_ble_hci_radio_validate_52fcfc'] if is_c else 0x52fcfc)|1,0x600000,count=3000)
   pair.append((events,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x2007b000,4)),bytes(u.mem_read(0x20074948,4))))
  assert pair[0]==pair[1],(label,pair)
  count+=1
 print('PASS_RADIO_VALIDATE_NATIVE',count)
