#!/usr/bin/env python3
"""Compare native/C GPU SPOT callback failure continuation to IRQ save."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=R/'components/audio/power_vendor_candidate/power.c'
PRODUCT=R/'components/audio/power_vendor_candidate/power_product_native.c'
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c'
 p.write_text('''#include "power.h"
uint32_t g2_power_get_descriptor(g2_power_descriptor *p,uint32_t x){(void)p;(void)x;return 0;}
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
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,g2_power_vendor_enable','-I'+str(SRC.parent),str(SRC),str(PRODUCT),str(p),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=l.split())==3}
 with e.open('rb') as f:segs=[(x['p_vaddr'],x.data()) for x in ELFFile(f).iter_segments() if x['p_type']=='PT_LOAD']
 for mode in [0,3]:
  for spot_return in [0,1,7]:
   observations=[]
   for is_c in [False,True]:
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000)
    u.mem_map(0x20000000,0x100000);u.mem_map(0x40000000,0x100000)
    for a,d in segs:u.mem_write(a,d)
    # The ROM literals authenticate the native current and previous cells.
    u.mem_write(0x20074f60,bytes([mode]));u.mem_write(0x20074f61,b'\x00')
    u.mem_write(0x40020100,(0).to_bytes(4,'little'))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x14)
    native={0x47ef18:'descriptor',0x48032c:'tempco',0x4c44bc:'clock',0x480312:'spot',0x473940:'critical'}
    source={syms[{'spot_update':'audio_ble_flash_control','clock_request':'audio_uart_pin_mux_enable','clock_release_all':'audio_uart_font_pin_mux_disable','wait5':'audio_wait5'}.get(n,'g2_power_'+n)]&~1:kind for n,kind in [('get_descriptor','descriptor'),('tempco_postpone','tempco'),('clock_request','clock'),('spot_update','spot'),('critical_save','critical')]}
    calls=[]
    def hook(uc,a,size,_):
     kind=(source if is_c else native).get(a)
     if not kind:return
     r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2)
     if kind=='descriptor':
      calls.append((kind,r1))
      vals=([0x40020100,0x40020104,1,1] if is_c else [0x40020100,1,0x40020104,1])
      uc.mem_write(r0,b''.join(x.to_bytes(4,'little') for x in vals));ret=0
     elif kind=='tempco':calls.append((kind,));ret=0
     elif kind=='clock':calls.append((kind,r0,r1));ret=0
     elif kind=='spot':
      calls.append((kind,r0,r1,uc.mem_read(r2,1)[0]));ret=spot_return
     else:calls.append((kind,));uc.emu_stop();return
     uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((syms['g2_power_vendor_enable'] if is_c else 0x47f5b8)|1,0x600000,count=500)
    observations.append(calls)
   assert observations[0]==observations[1],(mode,spot_return,observations)
 for spot_return in [0,1,7]:
  reached=[]
  for is_c in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000)
   u.mem_map(0x20000000,0x100000);u.mem_map(0x40000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_write(0x20074f60,b'\x00');u.mem_write(0x20074f61,b'\x00')
   u.mem_write(0x40020100,(1).to_bytes(4,'little'))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x14)
   native={0x47ef18:'descriptor',0x48032c:'tempco',0x473940:'critical',0x47f6f2:'last',0x480826:'wait',0x480312:'spot',0x4c45a4:'release_all'}
   source={syms[{'spot_update':'audio_ble_flash_control','clock_request':'audio_uart_pin_mux_enable','clock_release_all':'audio_uart_font_pin_mux_disable','wait5':'audio_wait5'}.get(n,'g2_power_'+n)]&~1:kind for n,kind in [('get_descriptor','descriptor'),('tempco_postpone','tempco'),('critical_save','critical'),('wait5','wait'),('spot_update','spot'),('clock_release_all','release_all')]}
   events=[]
   def hook(uc,a,size,_):
    kind=(source if is_c else native).get(a)
    if kind is None:return
    r0=uc.reg_read(UC_ARM_REG_R0)
    if kind=='descriptor':
     vals=([0x40020100,0x40020104,1,1] if is_c else [0x40020100,1,0x40020104,1])
     uc.mem_write(r0,b''.join(x.to_bytes(4,'little') for x in vals));ret=0
    elif kind=='last':ret=1
    elif kind=='spot':events.append(('spot',r0));ret=spot_return
    elif kind=='release_all':events.append(('release_all',r0));uc.emu_stop();return
    else:ret=0
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['g2_power_vendor_disable'] if is_c else 0x47f7ae)|1,0x600000,count=1000)
   reached.append(events)
  assert reached[0]==reached[1]==[('spot',1),('release_all',0x14)],(spot_return,reached)
 for seed in [0xffffffff,0x12345678,0x0100000f]:
  observations=[]
  for is_c in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000)
   u.mem_map(0x20000000,0x100000);u.mem_map(0x40000000,0x100000);u.mem_map(0xe000e000,0x1000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_write(0x40020100,(1).to_bytes(4,'little'))
   u.mem_write(0xe000edfc,seed.to_bytes(4,'little'));u.mem_write(0x40020250,seed.to_bytes(4,'little'))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x1c)
   desc=(syms['g2_power_get_descriptor']&~1) if is_c else 0x47ef18
   stop=(syms['g2_power_tempco_postpone']&~1) if is_c else 0x48032c
   writes=[];stopped=[]
   def hook(uc,a,size,_):
    if a==stop:stopped.append(True);uc.emu_stop();return
    if a==desc:
     r0=uc.reg_read(UC_ARM_REG_R0)
     vals=([0x40020100,0x40020104,1,1] if is_c else [0x40020100,1,0x40020104,1])
     uc.mem_write(r0,b''.join(x.to_bytes(4,'little') for x in vals))
     uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   def written(uc,access,a,size,value,_):writes.append((a,value&0xffffffff))
   u.hook_add(UC_HOOK_CODE,hook)
   u.hook_add(UC_HOOK_MEM_WRITE,written,begin=0x40020250,end=0x40020253)
   u.hook_add(UC_HOOK_MEM_WRITE,written,begin=0xe000edfc,end=0xe000edff)
   u.emu_start((syms['g2_power_vendor_disable'] if is_c else 0x47f7ae)|1,0x600000,count=300)
   observations.append((stopped,writes))
  assert observations[0]==observations[1],(seed,observations)
 print('PASS_POWER_GPU_SPOT_AND_DEBUG',12)
