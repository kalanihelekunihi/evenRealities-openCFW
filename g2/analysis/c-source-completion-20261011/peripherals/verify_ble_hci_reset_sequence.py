"""Bounded actual ARM compiled-C/native reset opcode and callback comparison."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_reset_sequence.c'
BDADDR=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_get_bd_addr.c'
NAMES='HciLeSetEventMaskCmd HciVscUpdateNvdsParam HciReadBdAddrCmd HciLeReadBufSizeCmd HciSetEventMaskPage2Cmd HciLeReadSupStatesCmd audio_ble_hci_read_resolving_list_size HciLeReadLocalSupFeatCmd HciLeRandCmd HciLeReadWhiteListSizeCmd audio_ble_hci_read_max_data_len HciLeWriteDefDataLen HciSetEventMaskCmd HciVscSetRfPowerLevelEx'.split()
SHIM='''#include <stdint.h>
uint8_t audio_ble_hci_controller_state_20071478[0xb0],audio_ble_hci_stack_state_20073870[0x40];
volatile uint8_t audio_ble_hci_reset_rand_count;
const uint8_t audio_ble_hci_event_mask_78d6dc[8]={0},audio_ble_hci_le_event_mask_78d6e4[8]={0},audio_ble_hci_event_mask_page2_78d6ec[8]={0};
void __aeabi_memcpy(void*d,const void*s,unsigned n){uint8_t*a=d;const uint8_t*b=s;for(unsigned i=0;i<n;i++)a[i]=b[i];}
''' + '\n'.join('void '+n+'(){ }' for n in NAMES)+'\n'
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_reset_sequence_body',str(SRC),str(BDADDR),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 native={0x4b4c8a:'HciVscUpdateNvdsParam',0x52b37c:'HciLeReadSupStatesCmd',0x52b304:'HciLeRandCmd',0x52b31e:'HciLeReadBufSizeCmd',0x52b396:'HciLeReadWhiteListSizeCmd'}
 compiled={syms[n]&~1:n for n in native.values()}
 for name,opcode,count,option in (('nonreset',0x0c03,0,False),('nvds',0x0c03,2,False),('bdaddr',0x1009,0,False),('whitelist',0x201c,0,False),('buffer',0x2002,0,False),('rand',0x2018,2,False),('rand_cb',0x2018,3,False),('option_null',0x2024,0,False),('option_cb',0x2024,0,True)):
  results=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   controller=syms['audio_ble_hci_controller_state_20071478'] if is_c else 0x20071478
   stack=syms['audio_ble_hci_stack_state_20073870'] if is_c else 0x20073870
   counter=syms['audio_ble_hci_reset_rand_count'] if is_c else 0x20074fd0
   u.mem_write(controller,b'\x00'*0xb0);u.mem_write(stack,b'\x00'*0x40);u.mem_write(counter,bytes([count]));u.mem_write(stack+0x21,b'\x01')
   if option:u.mem_write(controller+0xa0,struct.pack('<I',0x100700|1))
   if name=='rand_cb':u.mem_write(stack+8,struct.pack('<I',0x100700|1))
   message=0x20005000;data=bytearray(32);data[0]=0 if name=='nonreset' else 0x0e;struct.pack_into('<H',data,3,opcode);data[6]=0x34;data[7]=0x12;data[8]=0x56;u.mem_write(message,bytes(data))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,message);u.reg_write(UC_ARM_REG_R3,0x12345678)
   calls=[];cuts=compiled if is_c else native
   def hook(uc,a,size,_):
    if a==0x100700:
     calls.append(('callback',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
    if a in cuts:
     calls.append((cuts[a],));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['audio_ble_hci_reset_sequence_body'] if is_c else 0x569b56)|1,0x600000,count=700)
   # Product memory addresses differ between native and compiled linker models.
   normalized=[(x[0],) if x[0]!='callback' else ('callback',x[2] if option else struct.unpack('<I',u.mem_read(x[1],4))[0]) for x in calls]
   result=(u.reg_read(UC_ARM_REG_R0),normalized,bytes(u.mem_read(controller+0x60,0x10)),bytes(u.mem_read(controller+0x7e,0x20)),bytes(u.mem_read(stack+0x21,1)),bytes(u.mem_read(counter,1)))
   u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((syms['HciGetBdAddr'] if is_c else 0x530d30)|1,0x600000,count=50)
   results.append((*result,(u.reg_read(UC_ARM_REG_R0)-controller)&0xffffffff))
  assert results[0]==results[1],(name,results)
  print('PASS',name,results[0][0],results[0][1])
