#!/usr/bin/env python3
"""Actual ARM/native bounded comparison of group-2 IRQ release 0x4c3e9a."""
from pathlib import Path
import itertools,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_vendor_irq_bank2_enable.c'
names=['audio_uart_mux_bit_get','audio_uart_mux_bit_set','audio_uart_mux_any','g2_gpio_critical_save','audio_oscillator_control']
native=[0x4c37a8,0x4c37fe,0x4c377a,0x473940,0x4809c4]
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text('#include <stdint.h>\n'+''.join(f'uint32_t {n}(void){{return 0;}}\n' for n in names))
 e=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_vendor_irq_enable_bank2_4c3e9a',str(S),str(p),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=l.split())==3}
 with e.open('rb') as f:segs=[(x['p_vaddr'],x.data()) for x in ELFFile(f).iter_segments() if x['p_type']=='PT_LOAD']
 for bit,anybit,pin,flag,live in itertools.product([0,1],[0,1],[0,0x102],[0,0x7f],[0,0x12345678]):
  observations=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_write(0x20074f56,bytes([flag]));u.mem_write(0x20074260,live.to_bytes(4,'little'))
   cuts={((syms[n]&~1) if is_c else addr):i for i,(n,addr) in enumerate(zip(names,native))};calls=[]
   def hook(uc,a,size,_):
    i=cuts.get(a)
    if i is None:return
    r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2)
    detail=uc.mem_read(r1,1)[0] if i==4 else None
    calls.append((i,r0,r1 if i in (0,1) else detail,r2 if i==1 else None))
    uc.reg_write(UC_ARM_REG_R0,[bit,0,anybit,1,0][i]);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,pin)
   u.emu_start((syms['audio_ble_vendor_irq_enable_bank2_4c3e9a'] if is_c else 0x4c3e9a)|1,0x600000,count=500)
   observations.append((u.reg_read(UC_ARM_REG_R0),calls,bytes(u.mem_read(0x20074f56,1)),bytes(u.mem_read(0x20074260,4))))
  assert observations[0]==observations[1],(bit,anybit,pin,flag,live,observations)
 print('PASS_VENDOR_IRQ_BANK2_ENABLE',2*2*2*2*2)
