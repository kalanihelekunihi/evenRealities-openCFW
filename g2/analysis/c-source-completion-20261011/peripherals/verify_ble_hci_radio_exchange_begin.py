"""Actual ARM C/native send-chunk effects at authenticated child cuts."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_exchange_begin.c'
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text('''#include <stdint.h>\nint32_t audio_ble_radio_begin_select_52e072(void*p){return 0;}\nuint32_t audio_ble_radio_tx_space_52df50(void*p){return 0;}\nvoid audio_ble_radio_tx_release_52e058(void*p){}\nint32_t audio_ble_radio_io_mode_52dd1c(void){return 0;}\nvoid audio_ble_radio_serial_put_52dc98(uint32_t x){}\nint32_t audio_ble_vendor_send_55cf40(uint32_t x,void*p){return 0;}\nvoid audio_ble_radio_context_init_52e0a2(void*p){}\nvoid audio_ble_hci_boot_log_4733ee(const void*p,...){}\nconst uint8_t audio_ble_radio_send_log_71b740[4]={0};\nconst uint8_t audio_ble_radio_send_oversize_log_730e54[4]={0};\nvoid __aeabi_memclr(void*p,unsigned n){for(unsigned i=0;i<n;i++)((volatile unsigned char*)p)[i]=0;}\nvoid __aeabi_memclr4(void*p,unsigned n){for(unsigned i=0;i<n;i++)((volatile unsigned char*)p)[i]=0;}\nvoid __aeabi_memcpy(void*p,const void*q,unsigned n){for(unsigned i=0;i<n;i++)((volatile unsigned char*)p)[i]=((const volatile unsigned char*)q)[i];}\n''')
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_radio_exchange_begin_52e0d2',str(S),str(p),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=l.split())==3}
 with e.open('rb') as f:segs=[(x['p_vaddr'],x.data()) for x in ELFFile(f).iter_segments() if x['p_type']=='PT_LOAD']
 targets={'select':('audio_ble_radio_begin_select_52e072',0x52e072),'space':('audio_ble_radio_tx_space_52df50',0x52df50),'release':('audio_ble_radio_tx_release_52e058',0x52e058),'mode':('audio_ble_radio_io_mode_52dd1c',0x52dd1c),'serial':('audio_ble_radio_serial_put_52dc98',0x52dc98),'vendor':('audio_ble_vendor_send_55cf40',0x55cf40),'init':('audio_ble_radio_context_init_52e0a2',0x52e0a2),'log':('audio_ble_hci_boot_log_4733ee',0x4733ee)}
 cases=[('select_fail',2,0,0,0,0),('oversize',0,0,0,0,0x104),('empty',0,0,0,0,0),('no_space',0,0,0,0,2),('serial',0,2,1,0,2),('vendor_ok',0,2,0,0,2),('vendor_error',0,2,0,7,2)]
 for name,select,space,mode,vendor,length in cases:
  results=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_write(0x20001000,b'ABCD');u.mem_write(0x20004000,struct.pack('<II',0x1234,0x5678));calls=[]
   cuts={((syms[s]&~1) if is_c else addr):key for key,(s,addr) in targets.items()}
   def hook(uc,a,size,_):
    key=cuts.get(a)
    if key is None:return
    if key=='vendor':
     d=uc.reg_read(UC_ARM_REG_R1);count=struct.unpack('<I',uc.mem_read(d+16,4))[0];payload=struct.unpack('<I',uc.mem_read(d+24,4))[0]
     calls.append((key,uc.reg_read(UC_ARM_REG_R0),count,uc.mem_read(d+20,1)[0],bytes(uc.mem_read(payload,count))))
    elif key=='log':calls.append((key,uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)))
    elif key=='serial':calls.append((key,uc.reg_read(UC_ARM_REG_R0)))
    else:calls.append((key,))
    if key in ('select','space','mode','vendor'):
     uc.reg_write(UC_ARM_REG_R0,{'select':select,'space':space,'mode':mode,'vendor':vendor}[key])
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_R1,0x20001000);u.reg_write(UC_ARM_REG_R2,length)
   entry=syms['audio_ble_radio_exchange_begin_52e0d2'] if is_c else 0x52e0d2
   u.emu_start(entry|1,0x600000,count=3000)
   results.append((u.reg_read(UC_ARM_REG_R0),calls))
  assert results[0]==results[1],(name,results)
  print('PASS',name,results[0])
