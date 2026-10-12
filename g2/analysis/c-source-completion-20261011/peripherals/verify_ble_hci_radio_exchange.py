"""Actual ARM C/native exchange with authenticated child cuts and MMIO ready."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_exchange.c'
W=lambda u,a,v:u.mem_write(a,struct.pack('<I',v))
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text('''#include <stdint.h>\nint32_t audio_ble_radio_exchange_begin_52e0d2(void*a,const void*b,uint32_t c){return 0;}\nint32_t audio_ble_radio_exchange_receive_52e1ea(void*a,void*b,uint32_t*c){return 0;}\nvoid audio_ble_hci_boot_delay_491102(uint32_t n){(void)n;}\n''')
 e=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_radio_exchange_52e612',str(S),str(p),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=l.split())==3}
 with e.open('rb') as f:segs=[(x['p_vaddr'],x.data()) for x in ELFFile(f).iter_segments() if x['p_type']=='PT_LOAD']
 cases=[('null_command',0,1,1,0,0),('null_response',1,0,1,0,0),('null_received',1,1,0,0,0),('begin_fail',1,1,1,4,0),('matched',1,1,1,0,0),('mismatch_then_match',1,1,1,0,1),('receive_fail',1,1,1,0,2)]
 for name,has_cmd,has_resp,has_count,begin_code,reply_mode in cases:
  results=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40010000,0x10000)
   for a,d in segs:u.mem_write(a,d)
   command=0x20001000;response=0x20002000;received=0x20003000
   u.mem_write(command,b'\x01\x01\xfd\x05\x00\x20\x40\x00\x04');u.mem_write(response,b'\x00'*16);W(u,0x40010410,0x00200000)
   calls=[];received_calls=[0]
   cuts={((syms['audio_ble_radio_exchange_begin_52e0d2']&~1) if is_c else 0x52e0d2):'begin',((syms['audio_ble_radio_exchange_receive_52e1ea']&~1) if is_c else 0x52e1ea):'receive',((syms['audio_ble_hci_boot_delay_491102']&~1) if is_c else 0x491102):'delay'}
   def hook(uc,a,size,_):
    label=cuts.get(a)
    if label is None:return
    calls.append(label)
    if label=='begin':
     calls[-1]=('begin',uc.reg_read(UC_ARM_REG_R2));uc.reg_write(UC_ARM_REG_R0,begin_code)
    if label=='receive':
     received_calls[0]+=1
     if reply_mode==2:uc.reg_write(UC_ARM_REG_R0,7)
     else:
      uc.mem_write(response+4,b'\x00\x00' if reply_mode==1 and received_calls[0]==1 else b'\x01\xfd')
      W(uc,received,6);uc.reg_write(UC_ARM_REG_R0,0)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   sp=0x200ff000;W(u,sp,received if has_count else 0)
   u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_R1,command if has_cmd else 0);u.reg_write(UC_ARM_REG_R2,9);u.reg_write(UC_ARM_REG_R3,response if has_resp else 0)
   entry=syms['audio_ble_radio_exchange_52e612'] if is_c else 0x52e612
   u.emu_start(entry|1,0x600000,count=500)
   results.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1),calls,bytes(u.mem_read(response,8))))
  assert results[0]==results[1],(name,results)
  print('PASS',name,results[0][:3])
