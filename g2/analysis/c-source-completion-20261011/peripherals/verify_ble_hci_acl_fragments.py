"""Controlled ARM C/native ACL start/continue/complete effects; children cut identically."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_acl_fragments.c'
SHIM='''#include <stdint.h>
uint16_t audio_ble_hci_get_buf_size(void){return 5;}
uint32_t audio_ble_hci_send_acl_data(void*c,void*p){(void)c;(void)p;return 1;}
uint8_t *audio_ble_hci_next_conn_fragment(void){return 0;}
void audio_ble_wsf_message_free(void*p){(void)p;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_tx_acl_start',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 native={'size':0x530d34,'send':0x52a76c,'next':0x52a72e,'free':0x4bf9b0}
 compiled={'size':syms['audio_ble_hci_get_buf_size']&~1,'send':syms['audio_ble_hci_send_acl_data']&~1,'next':syms['audio_ble_hci_next_conn_fragment']&~1,'free':syms['audio_ble_wsf_message_free']&~1}
 starts={'start':(0x52a850,'audio_ble_hci_tx_acl_start'),'continue':(0x52a8b0,'audio_ble_hci_tx_acl_continue'),'complete':(0x52a936,'audio_ble_hci_tx_acl_complete')}
 for label,body,length,send_ok,remaining,active in [('full','start',4,1,0,0),('split','start',8,1,0,0),('reject','start',8,0,0,0),('cont_more','continue',0,1,8,1),('cont_done','continue',0,1,4,1),('cont_reject','continue',0,0,8,1),('complete_plain','complete',0,1,0,0),('complete_frag','complete',0,1,0,1)]:
  rows=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   conn=0x20006000;packet=0x20007000
   cr=bytearray(0x20);struct.pack_into('<I',cr,0,packet);struct.pack_into('<I',cr,4,packet);struct.pack_into('<H',cr,0x10,0x1234);struct.pack_into('<H',cr,0x12,remaining);cr[0x16]=active
   u.mem_write(conn,bytes(cr));u.mem_write(packet,struct.pack('<HH',0x1234,length)+bytes(range(4,36)))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,conn)
   u.reg_write(UC_ARM_REG_R1,length if body=='start' else packet);u.reg_write(UC_ARM_REG_R2,packet)
   cuts={v:k for k,v in (compiled if is_c else native).items()};calls=[]
   def hook(uc,a,size,_):
    if a not in cuts:return
    name=cuts[a];calls.append(name);val={'size':5,'send':send_ok,'next':conn,'free':0}[name]
    uc.reg_write(UC_ARM_REG_R0,val);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   entry=(syms[starts[body][1]] if is_c else starts[body][0])|1
   u.emu_start(entry,0x600000,count=500)
   rows.append((u.reg_read(UC_ARM_REG_R0) if body!='complete' else None,calls,bytes(u.mem_read(conn,0x1c)),bytes(u.mem_read(packet,12))))
  assert rows[0]==rows[1],(label,rows)
  print('PASS',label,rows[0][:2])
