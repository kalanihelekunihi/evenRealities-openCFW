#!/usr/bin/env python3
"""Native/compiled-C bounded image-load branch and live-cell effects."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_image_load.c'
names=['audio_ble_radio_file_mode_52f3a0','audio_file_open','audio_ble_radio_file_size_52f3f8','file_heap_allocate','audio_file_read','audio_file_close','audio_file_heap_free','audio_ble_radio_header_copy_52f86a','audio_ble_radio_records_52f87c','audio_ble_radio_record_data_52f99e','audio_log_flags','audio_log_extended','compressed_log_output','__aeabi_memclr']
native=[0x52f3a0,0x474550,0x52f3f8,0x474cd2,0x474634,0x4745f4,0x474d16,0x52f86a,0x52f87c,0x52f99e,0x43d0ce,0x43d574,0x43ce9e,0x43c0e4]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
const char *audio_ble_radio_file_mode_52f3a0(uint32_t x){(void)x;return 0;}
void *audio_file_open(const char *a,const char *b){(void)a;(void)b;return 0;}
int32_t audio_ble_radio_file_size_52f3f8(void *a){(void)a;return 0;}
void *file_heap_allocate(uint32_t a){(void)a;return 0;}
uint32_t audio_file_read(void *a,uint32_t b,uint32_t c,void*d){(void)a;(void)b;(void)c;(void)d;return 0;}
int32_t audio_file_close(void*a){(void)a;return 0;}
void audio_file_heap_free(void*a){(void)a;}
uint32_t audio_ble_radio_header_copy_52f86a(void*a,void*b){(void)a;(void)b;return 0;}
uint32_t audio_ble_radio_records_52f87c(const void*a,uint32_t b){(void)a;(void)b;return 0;}
uint32_t audio_ble_radio_record_data_52f99e(const void*a,uint32_t b){(void)a;(void)b;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
void __aeabi_memclr(void*a,unsigned b){(void)a;(void)b;}
''')
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_radio_image_load_52f442',str(S),str(shim),'-o',str(e)],check=True)
 with e.open('rb') as f:
  x=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for stage in ('open','size','allocate','read','header','records','data','success'):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segments:u.mem_write(a,d)
   u.mem_write(0x20074948,b'\0'*48);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   mapping=dict(zip((sym[n]&~1 for n in names) if is_c else native,names));events=[]
   def hook(uc,a,size,_):
    n=mapping.get(a)
    if n is None:return
    idx=names.index(n);r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2)
    if idx==0:ret=0x20010000
    elif idx==1:ret=0 if stage=='open' else 0x20020000
    elif idx==2:ret=0xffffffff if stage=='size' else 32
    elif idx==3:ret=0 if stage=='allocate' else 0x20030000
    elif idx==4:ret=16 if stage=='read' else 32
    elif idx==7:
     uc.mem_write(r1,struct.pack('<IIII',0x12345678,0x20,1,1));ret=0 if stage=='header' else 1
    elif idx==8:ret=0 if stage=='records' else 1
    elif idx==9:ret=0 if stage=='data' else 1
    elif idx==10:ret=0
    elif idx==13:
     uc.mem_write(r0,b'\0'*r1);ret=r0
    else:ret=0
    if idx in (1,2,3,4,5,6,7,8,9):events.append((idx,r2 if idx in (3,4,8,9) else 0))
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((sym['audio_ble_radio_image_load_52f442'] if is_c else 0x52f442)|1,0x600000,count=7000)
   pair.append((u.reg_read(UC_ARM_REG_R0),events,bytes(u.mem_read(0x20074948,44))))
  assert pair[0]==pair[1],(stage,pair)
  cases+=1
 print('PASS_RADIO_IMAGE_LOAD_NATIVE',cases)
