#!/usr/bin/env python3
"""Connected native/C crypto precheck through actual descriptor and product C."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
DIR=R/'components/audio/power_vendor_candidate'
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include "power.h"
uint32_t g2_power_tempco_postpone(void){return 0;}
uint32_t g2_power_tempco_pending(void){return 0;}
uint32_t audio_ble_flash_control(uint32_t a,uint32_t b,const uint32_t *c){(void)a;(void)b;(void)c;return 0;}
uint32_t g2_power_gpu_mode_select(uint32_t a){(void)a;return 0;}
uint32_t audio_uart_pin_mux_enable(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}
uint32_t audio_uart_pin_mux_disable(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}
uint32_t audio_uart_font_pin_mux_disable(uint32_t a){(void)a;return 0;}
uint32_t g2_power_critical_save(void){return 0;}
void g2_power_critical_restore(uint32_t a){(void)a;}
uint32_t audio_wait5(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e){(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}
uint32_t audio_wait4(uint32_t a,uint32_t b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}
void audio_delay_us(uint32_t a){(void)a;}
''')
 e=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,g2_power_vendor_enable','-I'+str(DIR),*[str(DIR/x) for x in ('power.c','power_descriptor_native.c','power_product_native.c')],str(shim),'-o',str(e)],check=True)
 with e.open('rb') as f:
  x=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD']
  sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 for value in [0,0x08000000,0x08000001,0xffffffff]:
  for selector in [0x17,0x117,0x217]:
   pair=[]
   for is_c in [False,True]:
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
    u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40000000,0x100000)
    for a,b in segments:u.mem_write(a,b)
    u.mem_write(0x40021004,(0).to_bytes(4,'little'));u.mem_write(0x40021008,value.to_bytes(4,'little'))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,selector)
    hit=[];stop=(sym['g2_power_tempco_postpone']&~1) if is_c else 0x48032c
    def hook(uc,a,size,_):
     if a==stop:hit.append(True);uc.emu_stop()
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((sym['g2_power_vendor_enable'] if is_c else 0x47f5b8)|1,0x600000,count=3000)
    pair.append((bool(hit),None if hit else u.reg_read(UC_ARM_REG_R0)))
   assert pair[0]==pair[1],(value,selector,pair)
 print('PASS_POWER_CRYPTO_CONNECTED',12)
