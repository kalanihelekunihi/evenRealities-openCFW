"""Compiled-C/native BLE startup register and state leaves, connected HCI chain."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint8_t audio_ble_stack_state_20072cb8[0x50],audio_ble_hci_stack_state_20073870[0x24],audio_ble_dm_stack_rows_200738dc[0x19],audio_ble_hci_controller_state_20071478[0xb0],audio_ble_hci_cmd_state_20073a90[0x20];
uint8_t audio_ble_dm_config[0x50],audio_ble_dm_privacy_state[0x20],audio_ble_other_handler_id;
uint8_t audio_ble_dm_stack_table_78a88c[1];
void audio_ble_stack_callback_536234(void){} void audio_ble_stack_callback_536470(void){}
void audio_ble_stack_callback_536620(void){} void audio_ble_stack_callback_5366dc(void){}
void WsfTaskLock(void){} void WsfTaskUnlock(void){} void audio_ble_other_handler_start(void){}
''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_stack_lower_536324',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_stack_lowers.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 state={'audio_ble_stack_state_20072cb8':(0x20072cb8,0x50),'audio_ble_hci_stack_state_20073870':(0x20073870,0x24),'audio_ble_dm_stack_rows_200738dc':(0x200738dc,0x19),'audio_ble_hci_controller_state_20071478':(0x20071478,0xb0),'audio_ble_hci_cmd_state_20073a90':(0x20073a90,0x20),'audio_ble_dm_config':(0x20000694,0x50),'audio_ble_dm_privacy_state':(0x20073b78,0x20),'audio_ble_other_handler_id':(0x20074f92,1)}
 callbacks={'audio_ble_stack_callback_536234':0x536235,'audio_ble_stack_callback_536470':0x536471,'audio_ble_stack_callback_536620':0x536621,'audio_ble_stack_callback_5366dc':0x5366dd,'audio_ble_dm_stack_table_78a88c':0x78a88c}
 cases=[('audio_ble_stack_lower_536324',0x536324,0),('audio_ble_stack_lower_53648e',0x53648e,0),('audio_ble_stack_lower_5366cc',0x5366cc,0),('audio_ble_stack_lower_5367ca',0x5367ca,0),('audio_ble_stack_lower_5367f8',0x5367f8,7),('audio_ble_stack_lower_5369ea',0x5369ea,0),('audio_ble_stack_lower_4bae6c',0x4bae6c,7)]
 for name,native,arg in cases:
  obs=[]
  for c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_map(0x20000000,0x100000)
   for k,(native_addr,n) in state.items():u.mem_write(syms[k] if c else native_addr,b'\xaa'*n)
   privacy=syms['audio_ble_dm_privacy_state'] if c else 0x20073b78
   u.mem_write(privacy+0xc,b'\x05')
   cuts={syms['WsfTaskLock']&~1:'lock',syms['WsfTaskUnlock']&~1:'unlock',syms['audio_ble_other_handler_start']&~1:'other'} if c else {0x52b8c8:'lock',0x52b8d0:'unlock',0x47a85c:'other'}
   calls=[]
   def hook(uc,a,size,_):
    if a in cuts:calls.append(cuts[a]);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.reg_write(UC_ARM_REG_R0,arg);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((syms[name] if c else native)|1,0x600000,count=12000)
   data=[]
   for k,(native_addr,n) in state.items():
    addr=syms[k] if c else native_addr;d=bytearray(u.mem_read(addr,n))
    if c:
     rev={syms[s]|(0 if s.startswith('audio_ble_dm_stack') else 1):v for s,v in callbacks.items()}
     for i in range(0,len(d)-3,4):
      val=struct.unpack_from('<I',d,i)[0]
      if val in rev:struct.pack_into('<I',d,i,rev[val])
    data.append(bytes(d))
   obs.append((data,calls))
  assert obs[0]==obs[1],(name,[(x[1],[(i, [j for j,(a,b) in enumerate(zip(y,obs[1-z][0][i])) if a!=b][:12]) for i,y in enumerate(x[0]) if y!=obs[1-z][0][i]]) for z,x in enumerate(obs)])
  print('PASS BLE stack lower',name)
