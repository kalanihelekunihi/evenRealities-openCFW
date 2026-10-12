"""Bounded actual ARM C/native stop transition comparison; children cut at ABI."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_recover_stop.c'
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text('''#include <stdint.h>\nvoid audio_ble_hci_radio_reset_52e8a4(void){}\nvoid audio_ble_radio_wait_pulse_52e854(uint32_t x){}\nint32_t audio_ble_radio_exchange_receive_52e1ea(void*a,void*b,uint32_t*c){return 0;}\nint32_t g2_lfs_memcmp(const void*a,const void*b,uint32_t n){return 0;}\nvoid audio_ble_hci_boot_log_4733ee(const void*a,...){}\nconst uint8_t audio_ble_radio_stop_start_log_751638[]={0};\nconst uint8_t audio_ble_radio_stop_retry_log_730e84[]={0};\nconst uint8_t audio_ble_radio_stop_done_log_75d570[]={0};\nvoid __aeabi_memclr(void*p,unsigned n){for(unsigned i=0;i<n;i++)((volatile unsigned char*)p)[i]=0;}\n''')
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_radio_recover_stop_52e8be',str(S),str(p),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=l.split())==3}
 with e.open('rb') as f:segs=[(x['p_vaddr'],x.data()) for x in ELFFile(f).iter_segments() if x['p_type']=='PT_LOAD']
 pairs={'reset':('audio_ble_hci_radio_reset_52e8a4',0x52e8a4),'wait':('audio_ble_radio_wait_pulse_52e854',0x52e854),'receive':('audio_ble_radio_exchange_receive_52e1ea',0x52e1ea),'compare':('g2_lfs_memcmp',0x4751c8),'log':('audio_ble_hci_boot_log_4733ee',0x4733ee)}
 for path in ('success','retry','mismatch','not_ready'):
  results=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40010000,0x10000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_write(0x40010410,(0 if path=='not_ready' else 0x200000).to_bytes(4,'little'))
   cuts={(syms[c]&~1) if is_c else n:k for k,(c,n) in pairs.items()}
   calls=[];state={'receive':0,'compare':0,'wait':0}
   def hook(uc,a,size,_):
    k=cuts.get(a)
    if k is None:return
    if k=='wait':
     calls.append((k,uc.reg_read(UC_ARM_REG_R0)));state[k]+=1
     if path=='not_ready' and state[k]==2:uc.mem_write(0x40010410,(0x200000).to_bytes(4,'little'))
    elif k=='receive':
     state[k]+=1;calls.append((k,uc.reg_read(UC_ARM_REG_R0)))
     value=7 if path=='retry' and state[k]==1 else 0
     uc.mem_write(uc.reg_read(UC_ARM_REG_R1),bytes([4,0xff,1,3])+bytes(12))
     uc.reg_write(UC_ARM_REG_R0,value)
    elif k=='compare':
     state[k]+=1;calls.append((k,uc.reg_read(UC_ARM_REG_R2)))
     uc.reg_write(UC_ARM_REG_R0,1 if path=='mismatch' and state[k]==1 else 0)
    elif k=='log':calls.append((k,))
    else:calls.append((k,))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x20004000)
   u.emu_start((syms['audio_ble_radio_recover_stop_52e8be'] if is_c else 0x52e8be)|1,0x600000,count=10000)
   results.append((u.reg_read(UC_ARM_REG_R0),calls))
  assert results[0]==results[1],(path,results)
  print('PASS',path,results[0])
