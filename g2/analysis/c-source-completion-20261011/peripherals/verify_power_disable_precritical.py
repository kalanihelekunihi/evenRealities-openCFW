#!/usr/bin/env python3
"""Actual descriptor/product plus native/C disable pre-critical effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
D=R/'components/audio/power_vendor_candidate'
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
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,g2_power_vendor_enable','-I'+str(D),*[str(D/x) for x in ('power.c','power_descriptor_native.c','power_product_native.c')],str(shim),'-o',str(e)],check=True)
 with e.open('rb') as f:
  x=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD']
  sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 mappings={False:{0x48032c:'postpone',0x480312:'spot',0x4c44bc:'clock',0x47f11c:'gpu_mode',0x473940:'critical'},True:{sym[{'spot_update':'audio_ble_flash_control','clock_request':'audio_uart_pin_mux_enable'}.get(name,'g2_power_'+name)]&~1:kind for name,kind in [('tempco_postpone','postpone'),('spot_update','spot'),('clock_request','clock'),('gpu_mode_select','gpu_mode'),('critical_save','critical')]}}
 count=0
 for selector in (0,1,2,3,6,7,11,15,20,29,30,31,32,33):
  for gpu_mode in (0,3):
   for callback_return in (0,7):
    pair=[]
    for is_c in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
     u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40000000,0x100000)
     for a,d in segments:u.mem_write(a,d)
     u.mem_write(0x20074f60,bytes([gpu_mode]));u.mem_write(0x20074f61,bytes([gpu_mode]))
     u.mem_write(0x40021004,(0xffffffff).to_bytes(4,'little'));u.mem_write(0x4002100c,(0xffffffff).to_bytes(4,'little'))
     u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,selector)
     events=[]
     def hook(uc,a,size,_):
      kind=mappings[is_c].get(a)
      if kind is None:return
      r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2)
      if kind=='postpone':events.append((kind,))
      elif kind=='spot':events.append((kind,r0,r1,uc.mem_read(r2,1)[0]))
      elif kind=='clock':events.append((kind,r0,r1))
      elif kind=='gpu_mode':events.append((kind,r0))
      else:events.append((kind,));uc.emu_stop();return
      uc.reg_write(UC_ARM_REG_R0,callback_return if kind=='spot' else 0)
      uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     u.hook_add(UC_HOOK_CODE,hook)
     u.emu_start((sym['g2_power_vendor_disable'] if is_c else 0x47f7ae)|1,0x600000,count=3000)
     pair.append(events)
    assert pair[0]==pair[1],(selector,gpu_mode,callback_return,pair)
    if selector not in (29,):
     assert ('critical',) in pair[0],(selector,pair)
    count+=1
 print('PASS_POWER_DISABLE_PRECRITICAL',count)
