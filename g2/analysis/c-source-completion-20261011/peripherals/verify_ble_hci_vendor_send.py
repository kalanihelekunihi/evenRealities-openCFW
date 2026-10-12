"""Actual ARM C/native vendor FIFO send over guarded and one-word paths."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_vendor_send.c'
W=lambda u,a,v:u.mem_write(a,struct.pack('<I',v))
Q=lambda u,a:struct.unpack('<I',u.mem_read(a,4))[0]
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text('''#include <stdint.h>\nuint32_t audio_ble_vendor_transfer_guard_55c1e0(const uint8_t*a,const uint8_t*b,uint32_t c){return 0;}\nuint32_t audio_ble_vendor_transfer_encode_55bce8(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f,uint32_t g,uint32_t h){return 0x12345678;}\nint32_t audio_ble_vendor_wait_480826(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e){return 0;}\nvoid audio_ble_vendor_yield_4807a0(uint32_t a){}\nint32_t audio_ble_vendor_finish_55bd70(uint32_t a,uint32_t b){return 0;}\nvoid audio_ble_vendor_recover_55bdac(uint8_t*a,uint32_t b){}\n''')
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_vendor_send_55cf40',str(S),str(p),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=l.split())==3}
 with e.open('rb') as f:segs=[(x['p_vaddr'],x.data()) for x in ELFFile(f).iter_segments() if x['p_type']=='PT_LOAD']
 child={'guard':('audio_ble_vendor_transfer_guard_55c1e0',0x55c1e0),'encode':('audio_ble_vendor_transfer_encode_55bce8',0x55bce8),'wait':('audio_ble_vendor_wait_480826',0x480826),'yield':('audio_ble_vendor_yield_4807a0',0x4807a0),'finish':('audio_ble_vendor_finish_55bd70',0x55bd70),'recover':('audio_ble_vendor_recover_55bdac',0x55bdac)}
 cases=[('null_row',0,1,2,0),('bad_row',1,0,2,0),('null_desc',1,1,2,0),('bad_type',1,1,1,0),('guard_fail',1,1,2,0),('busy',1,1,2,1),('zero',1,1,2,0),('one_word',1,1,2,0),('partial',1,1,2,0),('wait_first_fail',1,1,2,0),('wait_second_fail',1,1,2,0),('wait_last_fail',1,1,2,0),('finish_fail',1,1,2,0)]
 for name,has_row,valid,typ,busy in cases:
  results=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40050000,0x10000)
   for a,d in segs:u.mem_write(a,d)
   row=0x20001000;d=0x20002000;output=0x20003000;input_=0x20004000;u.mem_write(row,b'\x00'*0x900);u.mem_write(d,b'\x00'*0x30);u.mem_write(output,b'ABCD');u.mem_write(input_,b'\x00'*4)
   W(u,row,0x01123456 if valid else 0);W(u,row+0x860,0x20005000);u.mem_write(row+0x82c,bytes([2 if busy else 0]));W(u,d+20,typ)
   if name in ('one_word','partial'):
    W(u,d+16,2 if name=='partial' else 4);W(u,d+24,output);W(u,d+28,input_);W(u,0x40050100,0x00040400);W(u,0x40050108,0x12345678)
   W(u,0x40050200,0xaabbccdd);W(u,0x40050218,0xffffffff);W(u,0x40050280,0xaaaa)
   calls=[];waits=[0];cuts={((syms[s]&~1) if is_c else addr):key for key,(s,addr) in child.items()}
   def hook(uc,a,size,_):
    key=cuts.get(a)
    if key is None:return
    if key=='wait':calls.append((key,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R2),uc.reg_read(UC_ARM_REG_R3)))
    else:calls.append((key,))
    if key=='wait':waits[0]+=1
    failure=(name=='wait_first_fail' and key=='wait' and waits[0]==1) or (name=='wait_second_fail' and key=='wait' and waits[0]==2) or (name=='wait_last_fail' and key=='wait' and waits[0]==3)
    uc.reg_write(UC_ARM_REG_R0,6 if key=='guard' and name=='guard_fail' else (7 if failure else (5 if key=='finish' and name=='finish_fail' else (0x12345678 if key=='encode' else 0))))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,row if has_row else 0);u.reg_write(UC_ARM_REG_R1,0 if name=='null_desc' else d)
   entry=syms['audio_ble_vendor_send_55cf40'] if is_c else 0x55cf40
   u.emu_start(entry|1,0x600000,count=1000)
   results.append((u.reg_read(UC_ARM_REG_R0),calls,bytes(u.mem_read(0x40050100,0x1cc)),bytes(u.mem_read(input_,4))))
  assert results[0]==results[1],(name,results[0][:2],results[1][:2])
  print('PASS',name,results[0][:2])
