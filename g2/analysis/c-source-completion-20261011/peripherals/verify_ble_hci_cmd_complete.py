"""ARM C/native command-complete opcode, callback, ownership comparison."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_cmd_complete.c'
SHIM='''#include <stdint.h>
uint8_t audio_ble_hci_stack_state_20073870[0x40];uint8_t audio_ble_hci_event_sizes_6e3720[128];uint32_t audio_ble_hci_event_decoders_6c910c[128];
void *audio_wsf_buffer_alloc(uint16_t n){(void)n;return 0;}
void g2_wsf_candidate_buffer_free_word(uint32_t a){(void)a;}
void audio_ble_hci_cmd_receive_complete(uint32_t a){(void)a;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_event_cmd_complete_body',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for label,opcode,typ in (('unknown',0x1234,0),('mapped',0x0c2d,9),('rand',0x2018,0x1c),('vendor',0xfc00,0x12)):
  results=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   state=syms['audio_ble_hci_stack_state_20073870'] if is_c else 0x20073870
   u.mem_write(state,b'\x00'*0x40);u.mem_write(state+8,struct.pack('<II',0x100701,0x100741))
   decoder=0
   if typ:
    decoder=struct.unpack_from('<I',BLOB,0x6c910c-0x438000+typ*4)[0]&~1
    size=BLOB[0x6e3720-0x438000+typ]
    if is_c:
     u.mem_write(syms['audio_ble_hci_event_sizes_6e3720']+typ,bytes([size]))
     u.mem_write(syms['audio_ble_hci_event_decoders_6c910c']+typ*4,struct.pack('<I',0x100721))
   message=0x20005000;data=bytearray(16);data[0]=7;struct.pack_into('<H',data,1,opcode);u.mem_write(message,bytes(data))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,message);u.reg_write(UC_ARM_REG_R1,13);u.reg_write(UC_ARM_REG_R3,0x12345678)
   cuts={syms['audio_wsf_buffer_alloc']&~1:'alloc',syms['g2_wsf_candidate_buffer_free_word']&~1:'free',syms['audio_ble_hci_cmd_receive_complete']&~1:'receive'} if is_c else {0x530446:'alloc',0x5304d4:'free',0x52aef8:'receive'}
   calls=[]
   def hook(uc,a,size,_):
    if a in (0x100700,0x100740,0x100720,decoder) and a!=0:
     calls.append('decoder' if a in (0x100720,decoder) else 'alt_callback' if a==0x100740 else 'callback')
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
    if a not in cuts:return
    name=cuts[a];calls.append((name,uc.reg_read(UC_ARM_REG_R0)))
    uc.reg_write(UC_ARM_REG_R0,0x20006000 if name=='alloc' else 0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['audio_ble_hci_event_cmd_complete_body'] if is_c else 0x56b182)|1,0x600000,count=1200)
   results.append((u.reg_read(UC_ARM_REG_R0),calls,bytes(u.mem_read(0x20006000,4))))
  assert results[0]==results[1],(label,results)
  print('PASS',label,results[0])
