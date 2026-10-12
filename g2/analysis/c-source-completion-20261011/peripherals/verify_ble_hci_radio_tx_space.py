"""Actual ARM C/native transmit-space query with vendor/serial child cuts."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_tx_space.c'
W=lambda u,a,v:u.mem_write(a,struct.pack('<I',v))
Q=lambda u,a:struct.unpack('<I',u.mem_read(a,4))[0]
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text('''#include <stdint.h>\nvolatile uint8_t audio_ble_hci_radio_dispatch_cell_20074f4f;\nint32_t g2_gpio_hal_write(uint32_t a,uint32_t b){return 0;}\nvoid audio_ble_hci_boot_delay_491102(uint32_t n){}\nint32_t audio_ble_radio_io_mode_52dd1c(void){return 0;}\nint32_t audio_ble_vendor_send_55cf40(uint32_t a,void*b){return 0;}\nvoid audio_ble_radio_serial_put_52dc98(uint32_t a){}\nuint32_t audio_ble_radio_serial_get_52dcde(void){return 0;}\nvoid audio_ble_hci_boot_log_4733ee(const void*a,...){}\nconst uint8_t audio_ble_radio_tx_space_log_6ff930[4]={0};\nvoid __aeabi_memclr(void*p,unsigned n){for(unsigned i=0;i<n;i++)((volatile unsigned char*)p)[i]=0;}\nvoid __aeabi_memclr4(void*p,unsigned n){for(unsigned i=0;i<n;i++)((volatile unsigned char*)p)[i]=0;}\n''')
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_radio_tx_space_52df50',str(S),str(p),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=l.split())==3}
 with e.open('rb') as f:segs=[(x['p_vaddr'],x.data()) for x in ELFFile(f).iter_segments() if x['p_type']=='PT_LOAD']
 child={'gpio':('g2_gpio_hal_write',0x480fd6),'delay':('audio_ble_hci_boot_delay_491102',0x491102),'mode':('audio_ble_radio_io_mode_52dd1c',0x52dd1c),'vendor':('audio_ble_vendor_send_55cf40',0x55cf40),'put':('audio_ble_radio_serial_put_52dc98',0x52dc98),'get':('audio_ble_radio_serial_get_52dcde',0x52dcde),'log':('audio_ble_hci_boot_log_4733ee',0x4733ee)}
 cases=[('vendor_ok',0,0),('vendor_retry',0,1),('vendor_error',0,2),('serial_ok',1,0),('serial_retry',1,1)]
 for name,mode,variant in cases:
  results=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40010000,0x10000)
   for a,d in segs:u.mem_write(a,d)
   cell=syms['audio_ble_hci_radio_dispatch_cell_20074f4f'] if is_c else 0x20074f4f
   u.mem_write(cell,b'\x00');W(u,0x40010410,0x00200000);W(u,0x20004004,0x5678);calls=[];attempt=[0]
   cuts={((syms[s]&~1) if is_c else addr):key for key,(s,addr) in child.items()}
   def hook(uc,a,size,_):
    key=cuts.get(a)
    if key is None:return
    if key=='gpio':calls.append((key,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
    elif key=='put':calls.append((key,uc.reg_read(UC_ARM_REG_R0)))
    elif key=='log':calls.append((key,uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)))
    else:calls.append((key,))
    if key=='mode':uc.reg_write(UC_ARM_REG_R0,mode)
    elif key=='vendor':
     attempt[0]+=1;d=uc.reg_read(UC_ARM_REG_R1);response=Q(uc,d+0x1c)
     uc.mem_write(response,b'\xc0'+bytes([0 if variant==1 and attempt[0]==1 else 3]))
     uc.reg_write(UC_ARM_REG_R0,7 if variant==2 else 0)
    elif key=='get':
     attempt[0]+=1;uc.reg_write(UC_ARM_REG_R0,0 if variant==1 and attempt[0]==1 else 3)
    else:uc.reg_write(UC_ARM_REG_R0,0)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x20004000)
   entry=syms['audio_ble_radio_tx_space_52df50'] if is_c else 0x52df50
   u.emu_start(entry|1,0x600000,count=1000)
   results.append((u.reg_read(UC_ARM_REG_R0),calls,bytes(u.mem_read(cell,1))))
  assert results[0]==results[1],(name,results)
  print('PASS',name,results[0])
