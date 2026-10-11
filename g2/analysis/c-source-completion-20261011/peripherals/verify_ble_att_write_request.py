"""Actual ARM C/native bounded ATT write scheduler comparisons at child cuts."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_att_write_request.c'
CHILD={'WsfTaskLock':0x52b8c8,'WsfTaskUnlock':0x52b8d0,
 'audio_ble_att_registration_lookup':0x534f14,'audio_ble_att_connection_valid':0x52c928,
 'audio_ble_att_send_error':0x533934,'audio_wsf_msg_alloc':0x4bf99e,
 'g2_wsf_candidate_buffer_free_word':0x4bf9b0,'audio_queue_copy_bytes':0x439be4,
 'audio_wsf_msg_send':0x4bf9ba}
SHIM='#include <stdint.h>\nuint8_t audio_ble_att_runtime[128];\n'+'\n'.join('unsigned '+k+'(){return 0;}' for k in CHILD)
def w(u,a,v):u.mem_write(a,struct.pack('<I',v))
def h(u,a,v):u.mem_write(a,struct.pack('<H',v))
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_att_write_request',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for scenario in ('no_record','zero_max','blocked','invalid','too_long','no_msg','no_buffer','success'):
  rows=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   runtime=(syms['audio_ble_att_runtime']&~1) if compiled else 0x200610ac
   u.mem_write(runtime+96,b'\x09')
   w(u,0x20002010,0x20002100);h(u,0x20002100,0 if scenario=='zero_max' else 5 if scenario=='too_long' else 64)
   u.mem_write(0x20002102,b'\x04' if scenario=='blocked' else b'\x00')
   u.mem_write(0x20003000,b'X'*12);u.mem_write(0x20004000,b'Y'*40);u.mem_write(0x20005000,b'DATA')
   u.mem_write(0x200ff000,struct.pack('<III',0x20005000,0x1b,0))
   for r,v in [(UC_ARM_REG_R0,7),(UC_ARM_REG_R1,0x824),(UC_ARM_REG_R2,0),(UC_ARM_REG_R3,4),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)]:u.reg_write(r,v)
   cuts={(syms[k]&~1 if compiled else v):k for k,v in CHILD.items()};calls=[];allocs=[0]
   def hook(uc,a,size,_):
    if a not in cuts:return
    k=cuts[a];r0=uc.reg_read(UC_ARM_REG_R0)
    if k=='audio_wsf_msg_alloc':
     allocs[0]+=1;calls.append((k,r0))
     result=0 if (scenario=='no_msg' and allocs[0]==1) or (scenario=='no_buffer' and allocs[0]==2) else (0x20003000 if allocs[0]==1 else 0x20004000)
    elif k=='audio_ble_att_registration_lookup':calls.append((k,r0,uc.reg_read(UC_ARM_REG_R1)));result=0 if scenario=='no_record' else 0x20002000
    elif k=='audio_ble_att_connection_valid':calls.append((k,r0,uc.reg_read(UC_ARM_REG_R1)));result=0 if scenario=='invalid' else 1
    elif k=='audio_ble_att_send_error':calls.append((k,r0,uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)));result=0
    elif k=='audio_queue_copy_bytes':
     count=uc.reg_read(UC_ARM_REG_R2);calls.append((k,count));uc.mem_write(r0,bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1),count)));result=r0
    elif k=='audio_wsf_msg_send':calls.append((k,r0,bytes(uc.mem_read(0x20003000,12)),bytes(uc.mem_read(0x20004000,15))));result=0
    elif k=='g2_wsf_candidate_buffer_free_word':calls.append(('free',r0+(8 if compiled else 0)));result=0
    else:calls.append((k,));result=0
    uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['audio_ble_att_write_request'] if compiled else 0x533c6c)|1,0x600000,count=1500)
   rows.append((calls,u.reg_read(UC_ARM_REG_R0)))
  assert rows[0]==rows[1],(scenario,rows)
  print('PASS',scenario,len(rows[0][0]),rows[0][1])
