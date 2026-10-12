"""Compare actual ARM C and native vendor stop/DMA close with refresh cut."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_vendor_stop_hal.c'
W=lambda u,a,v:u.mem_write(a,struct.pack('<I',v))
Q=lambda u,a:struct.unpack('<I',u.mem_read(a,4))[0]
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text('''#include <stdint.h>\n#include <stdbool.h>\nuint32_t g2_gpio_critical_save(void){return 0;}\nbool g2_log_is_privileged(void){return true;}\n''')
 e=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_vendor_stack_stop_hal_55c11a',str(S),str(p),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=l.split())==3}
 with e.open('rb') as f:segs=[(x['p_vaddr'],x.data()) for x in ELFFile(f).iter_segments() if x['p_type']=='PT_LOAD']
 cases=[('stop_empty','stop',0,0,0),('stop_close','stop',0x01cdcdcd,7,7),('close_null','close',0,0,0),('close_bad','close',0x12345678,0,0),('close_busy','close',0x01cdcdcd,8,7),('close_success','close',0x01cdcdcd,7,7)]
 for name,kind,flags,prod,cons in cases:
  results=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40050000,0x10000)
   for a,d in segs:u.mem_write(a,d)
   outer=0x20010000;row=0x20011000;desc=0x20012000;W(u,outer+0x828,row if kind=='stop' and flags else 0);W(u,row,flags);W(u,row+28,prod);W(u,row+32,cons);W(u,row+36,desc);W(u,desc,0x40051000);W(u,desc+16,0x40051004);W(u,desc+20,0x55);W(u,0x40051000,0xff);W(u,0x40051004,0xff)
   calls=[];cut=(syms['audio_ble_vendor_dma_refresh_538d18']&~1) if is_c else 0x538d18
   def hook(uc,a,size,_):
    if a==cut:
     calls.append((uc.reg_read(UC_ARM_REG_R0)-row)&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   entry=(syms['audio_ble_vendor_stack_stop_hal_55c11a'] if kind=='stop' else syms['audio_ble_vendor_dma_close_53909a']) if is_c else (0x55c11a if kind=='stop' else 0x53909a)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0 if name=='close_null' else (outer if kind=='stop' else row));u.reg_write(UC_ARM_REG_R1,1 if kind=='stop' or name=='close_success' else 0)
   u.emu_start(entry|1,0x600000,count=300)
   results.append((u.reg_read(UC_ARM_REG_R0),calls,Q(u,outer+0x828),bytes(u.mem_read(row,40)),Q(u,0x40051000),Q(u,0x40051004)))
  assert results[0]==results[1],(name,results)
  print('PASS',name,results[0][0:2])
