"""Actual ARM C/native wait and finish conditions with yield cut."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_vendor_wait_finish.c'
W=lambda u,a,v:u.mem_write(a,struct.pack('<I',v))
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text('''#include <stdint.h>\nvoid audio_ble_vendor_yield_4807a0(uint32_t n){}\n''')
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_vendor_wait_480826',str(S),str(p),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=l.split())==3}
 with e.open('rb') as f:segs=[(x['p_vaddr'],x.data()) for x in ELFFile(f).iter_segments() if x['p_type']=='PT_LOAD']
 cases=[('wait_equal_now','wait',1,4,4,1,0),('wait_unequal_now','wait',1,3,4,0,0),('wait_timeout','wait',0,3,4,1,0),('wait_after_yield','wait',2,3,4,1,1),('finish_zero','finish',0,0,0,0,0),('finish_mask','finish',0,0x40,0,0,0),('finish_error1','finish',0,0x200,0,0,0),('finish_error2','finish',0,0x10,0,0,0),('finish_active','finish',0,0x4800,0,0,0),('finish_extra','finish',0,0,0,0,0x200)]
 for name,kind,timeout,current,expected,equal,extra in cases:
  results=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40050000,0x10000)
   for a,d in segs:u.mem_write(a,d)
   reg=0x40050204 if kind=='finish' else 0x20001000;W(u,reg,current);calls=[];cut=(syms['audio_ble_vendor_yield_4807a0']&~1) if is_c else 0x4807a0
   def hook(uc,a,size,_):
    if a!=cut:return
    calls.append(uc.reg_read(UC_ARM_REG_R0))
    if name=='wait_after_yield':W(uc,reg,expected)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   sp=0x200ff000;u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x600001)
   if kind=='wait':
    u.reg_write(UC_ARM_REG_R0,timeout);u.reg_write(UC_ARM_REG_R1,reg);u.reg_write(UC_ARM_REG_R2,0xffffffff);u.reg_write(UC_ARM_REG_R3,expected);W(u,sp,equal)
    entry=syms['audio_ble_vendor_wait_480826'] if is_c else 0x480826
   else:
    u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_R1,extra)
    entry=syms['audio_ble_vendor_finish_55bd70'] if is_c else 0x55bd70
   u.emu_start(entry|1,0x600000,count=300)
   results.append((u.reg_read(UC_ARM_REG_R0),calls))
  assert results[0]==results[1],(name,results)
  print('PASS',name,results[0])
