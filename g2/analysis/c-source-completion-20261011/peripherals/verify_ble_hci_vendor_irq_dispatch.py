"""Actual ARM C/native seven-bank IRQ disable/enable routing."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_vendor_irq_dispatch.c'
dis=['4c3bfc','4c3c60','4c3d9e','4c3cd4','4c3f2a','4c4086','4c427e']
ena=['4c3c2e','4c3ca2','4c3e9a','4c3d28','4c4016','4c420c','4c43ec']
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c'
 p.write_text('#include <stdint.h>\n'+''.join(f'uint32_t audio_ble_vendor_irq_{kind}_bank{i}_{addr}(uint32_t x){{return {10+i}u;}}\n' for kind,arr in [('disable',dis),('enable',ena)] for i,addr in enumerate(arr)))
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_vendor_irq_disable_4c44bc',str(S),str(p),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=l.split())==3}
 with e.open('rb') as f:segs=[(x['p_vaddr'],x.data()) for x in ELFFile(f).iter_segments() if x['p_type']=='PT_LOAD']
 for kind,arr,entry in [('disable',dis,0x4c44bc),('enable',ena,0x4c4530)]:
  for bank,irq in [(i,0x20) for i in range(7)]+[(7,0x20),(2,0x39),(2,0xff)]:
   results=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in segs:u.mem_write(a,d)
    cuts={((syms[f'audio_ble_vendor_irq_{kind}_bank{i}_{addr}']&~1) if is_c else int(addr,16)):i for i,addr in enumerate(arr)};calls=[]
    def hook(uc,a,size,_):
     i=cuts.get(a)
     if i is None:return
     calls.append((i,uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,10+i);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,bank);u.reg_write(UC_ARM_REG_R1,irq)
    start=syms[f'audio_ble_vendor_irq_{kind}_{entry:x}'] if is_c else entry
    u.emu_start(start|1,0x600000,count=200)
    results.append((u.reg_read(UC_ARM_REG_R0),calls))
   assert results[0]==results[1],(kind,bank,irq,results)
   print('PASS',kind,bank,irq,results[0])
