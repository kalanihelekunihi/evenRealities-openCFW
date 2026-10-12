"""Actual ARM C/native radio context handshake with controlled status edges."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_context_check.c'
W=lambda u,a,v:u.mem_write(a,struct.pack('<I',v))
Q=lambda u,a:struct.unpack('<I',u.mem_read(a,4))[0]
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text('''#include <stdint.h>\nvoid audio_ble_radio_context_setup_52e49a(uint32_t x){}\nint32_t g2_gpio_hal_write(uint32_t a,uint32_t b){return 0;}\nvoid audio_ble_hci_radio_reset_4910f4(uint32_t x){}\nvoid audio_ble_hci_boot_delay_491102(uint32_t n){}\nint32_t audio_ble_radio_exchange_receive_52e1ea(void*a,void*b,uint32_t*c){return 0;}\nvoid audio_ble_hci_boot_log_4733ee(const void*p,...){}\nvolatile uint32_t audio_ble_hci_radio_detect_word_20074228;\nconst uint8_t audio_ble_hci_radio_detect_log_774b04[4]={0};\nconst uint8_t audio_ble_hci_radio_detect_mismatch_log_7515cc[4]={0};\nconst uint8_t audio_ble_hci_radio_detect_bytes_log_711d58[4]={0};\nvoid __aeabi_memclr4(void*p,unsigned n){for(unsigned i=0;i<n;i++)((volatile unsigned char*)p)[i]=0;}\n''')
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_radio_context_check_52e4b4',str(S),str(p),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=l.split())==3}
 with e.open('rb') as f:segs=[(x['p_vaddr'],x.data()) for x in ELFFile(f).iter_segments() if x['p_type']=='PT_LOAD']
 child={'setup':('audio_ble_radio_context_setup_52e49a',0x52e49a),'gpio':('g2_gpio_hal_write',0x480fd6),'reset':('audio_ble_hci_radio_reset_4910f4',0x4910f4),'delay':('audio_ble_hci_boot_delay_491102',0x491102),'receive':('audio_ble_radio_exchange_receive_52e1ea',0x52e1ea),'log':('audio_ble_hci_boot_log_4733ee',0x4733ee)}
 cases=['null','match','mismatch','receive_fail']
 for name in cases:
  results=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40010000,0x10000)
   for a,d in segs:u.mem_write(a,d)
   cell=syms['audio_ble_hci_radio_detect_word_20074228'] if is_c else 0x20074228
   W(u,cell,0);W(u,0x40010410,0x00200000);calls=[];delays=[0]
   cuts={((syms[s]&~1) if is_c else addr):key for key,(s,addr) in child.items()}
   logs={((syms[s]&~1) if is_c else addr):key for key,s,addr in [('ok','audio_ble_hci_radio_detect_log_774b04',0x774b04),('mismatch','audio_ble_hci_radio_detect_mismatch_log_7515cc',0x7515cc),('bytes','audio_ble_hci_radio_detect_bytes_log_711d58',0x711d58)]}
   def hook(uc,a,size,_):
    key=cuts.get(a)
    if key is None:return
    if key=='log':calls.append((key,logs.get(uc.reg_read(UC_ARM_REG_R0)),uc.reg_read(UC_ARM_REG_R1) if name=='mismatch' else 0))
    elif key in ('setup','reset','delay'):calls.append((key,uc.reg_read(UC_ARM_REG_R0)))
    elif key=='gpio':calls.append((key,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
    else:calls.append((key,))
    if key=='delay':
     delays[0]+=1;W(uc,0x40010410,0 if delays[0]==1 else 0x00200000)
    if key=='receive':
     response=uc.reg_read(UC_ARM_REG_R1);uc.mem_write(response,b'\x04\xff\x01\x01\x00' if name=='match' else b'\x12\x34\x56\x78\x9a')
     W(uc,uc.reg_read(UC_ARM_REG_R2),5);uc.reg_write(UC_ARM_REG_R0,7 if name=='receive_fail' else 0)
    elif key=='gpio':uc.reg_write(UC_ARM_REG_R0,0)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0 if name=='null' else 0x20004000)
   entry=syms['audio_ble_radio_context_check_52e4b4'] if is_c else 0x52e4b4
   u.emu_start(entry|1,0x600000,count=1000)
   results.append((u.reg_read(UC_ARM_REG_R0),calls,Q(u,cell)))
  assert results[0]==results[1],(name,results)
  print('PASS',name,results[0])
