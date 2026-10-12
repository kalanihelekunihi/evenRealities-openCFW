"""Actual ARM C/native receive branches at authenticated child cuts."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_exchange_receive.c'
W=lambda u,a,v:u.mem_write(a,struct.pack('<I',v))
Q=lambda u,a:struct.unpack('<I',u.mem_read(a,4))[0]
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text('''#include <stdint.h>\nvolatile uint8_t audio_ble_hci_radio_dispatch_cell_20074f4f;\nint32_t audio_ble_radio_begin_select_52e072(void*p){return 0;}\nint32_t audio_ble_radio_io_mode_52dd1c(void){return 0;}\nvoid audio_ble_radio_context_init_52e0a2(void*p){}\nvoid audio_ble_radio_serial_put_52dc98(uint32_t x){}\nuint32_t audio_ble_radio_serial_get_52dcde(void){return 0;}\nint32_t audio_ble_vendor_send_55cf40(uint32_t x,void*p){return 0;}\nint32_t audio_ble_vendor_receive_55cc1c(uint32_t x,void*p){return 0;}\nint32_t g2_gpio_hal_write(uint32_t x,uint32_t y){return 0;}\nvoid audio_ble_hci_boot_log_4733ee(const void*p,...){}\nconst uint8_t audio_ble_radio_busy_log_768ae4[4]={0};\nconst uint8_t audio_ble_radio_header_log_6f7d84[4]={0};\nconst uint8_t audio_ble_radio_length_log_71b778[4]={0};\nconst uint8_t audio_ble_radio_bulk_log_71b7b0[4]={0};\nvoid __aeabi_memclr(void*p,unsigned n){for(unsigned i=0;i<n;i++)((volatile unsigned char*)p)[i]=0;}\nvoid __aeabi_memclr4(void*p,unsigned n){for(unsigned i=0;i<n;i++)((volatile unsigned char*)p)[i]=0;}\n''')
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_radio_exchange_receive_52e1ea',str(S),str(p),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=l.split())==3}
 with e.open('rb') as f:segs=[(x['p_vaddr'],x.data()) for x in ELFFile(f).iter_segments() if x['p_type']=='PT_LOAD']
 targets={'select':('audio_ble_radio_begin_select_52e072',0x52e072),'mode':('audio_ble_radio_io_mode_52dd1c',0x52dd1c),'init':('audio_ble_radio_context_init_52e0a2',0x52e0a2),'serial_put':('audio_ble_radio_serial_put_52dc98',0x52dc98),'serial_get':('audio_ble_radio_serial_get_52dcde',0x52dcde),'vendor_send':('audio_ble_vendor_send_55cf40',0x55cf40),'vendor_receive':('audio_ble_vendor_receive_55cc1c',0x55cc1c),'gpio':('g2_gpio_hal_write',0x480fd6),'log':('audio_ble_hci_boot_log_4733ee',0x4733ee)}
 cases=[('busy',1,1,0,0),('not_ready',0,0,0,0),('select_fail',0,1,5,0),('serial_bad',0,1,0,1),('serial_data',0,1,0,2),('vendor_data',0,1,0,0)]
 for name,busy,ready,select,mode in cases:
  results=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40010000,0x10000)
   for a,d in segs:u.mem_write(a,d)
   cell=syms['audio_ble_hci_radio_dispatch_cell_20074f4f'] if is_c else 0x20074f4f
   u.mem_write(cell,bytes([busy]));W(u,0x40010410,0x00200000 if ready else 0);W(u,0x20003000,0);u.mem_write(0x20002000,b'\x00'*8);W(u,0x20004004,0x5678)
   calls=[];serial_reads=[0]
   cuts={((syms[s]&~1) if is_c else addr):key for key,(s,addr) in targets.items()}
   def hook(uc,a,size,_):
    key=cuts.get(a)
    if key is None:return
    if key=='gpio':calls.append((key,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
    elif key=='serial_put':calls.append((key,uc.reg_read(UC_ARM_REG_R0)))
    elif key=='log':calls.append((key,uc.reg_read(UC_ARM_REG_R1)))
    else:calls.append((key,))
    if key=='select':uc.reg_write(UC_ARM_REG_R0,select)
    elif key=='mode':uc.reg_write(UC_ARM_REG_R0,1 if mode else 0)
    elif key=='serial_get':
     serial_reads[0]+=1
     value=(0 if mode==1 else (2 if serial_reads[0]==1 else (0x41 if serial_reads[0]==2 else 0x42)))
     uc.reg_write(UC_ARM_REG_R0,value)
     if serial_reads[0]>=3:W(uc,0x40010410,0)
    elif key=='vendor_send':
     d=uc.reg_read(UC_ARM_REG_R1);header=Q(uc,d+0x1c);uc.mem_write(header,b'\xc0\x02');uc.reg_write(UC_ARM_REG_R0,0)
    elif key=='vendor_receive':
     d=uc.reg_read(UC_ARM_REG_R1);dst=Q(uc,d+0x1c);uc.mem_write(dst,b'AB');W(uc,0x40010410,0);uc.reg_write(UC_ARM_REG_R0,0)
    else:uc.reg_write(UC_ARM_REG_R0,0)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_R1,0x20002000);u.reg_write(UC_ARM_REG_R2,0x20003000)
   entry=syms['audio_ble_radio_exchange_receive_52e1ea'] if is_c else 0x52e1ea
   u.emu_start(entry|1,0x600000,count=3000)
   results.append((u.reg_read(UC_ARM_REG_R0),calls,Q(u,0x20003000),bytes(u.mem_read(0x20002000,4))))
  assert results[0]==results[1],(name,results)
  print('PASS',name,results[0][:3])
