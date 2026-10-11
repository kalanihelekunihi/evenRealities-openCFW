"""Actual ARM C/native BLE dispatcher child-order comparison, external calls cut."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_comm_handler.c'
EXTERNAL={
 'audio_log_level':0x43d0ce,'audio_log_extended':0x43d574,'compressed_log_output':0x43ce9e,
 'audio_dm_conn_role':0x4b73c4,'audio_ble_connection_get':0x46ef60,
 'audio_ble_comm_dm_dispatch_a':0x532924,'audio_ble_comm_dm_dispatch_b':0x53484c,
 'audio_ble_comm_master_dispatch_a':0x503b92,'audio_ble_comm_master_dispatch_b':0x503c32,
 'audio_ble_comm_slave_dispatch':0x4b3ca4,'audio_ble_comm_slave_finish':0x4b45b0,
 'audio_ble_comm_message_release':0x4b75ce,'audio_ble_comm_forward_a':0x46ef74,
 'audio_ble_comm_forward_b':0x4a19c0}
SHIM='\n'.join('unsigned '+name+'(){return 0;}' for name in EXTERNAL)+'\n'
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_handler_4b7d32',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for event,connection,role,getter,flags in ((0,0,0,0,0),(2,1,0,0,0),(0x20,0,0,0,0),(0x22,1,1,1,0),(0x20,1,0,0,2),(0x22,1,1,1,1)):
  rows=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_write(0x20001000,bytes((connection&255,connection>>8,event))+b'\0'*13)
   u.reg_write(UC_ARM_REG_R0,3);u.reg_write(UC_ARM_REG_R1,0 if event==0 else 0x20001000)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   cuts={(syms[k]&~1 if compiled else v):k for k,v in EXTERNAL.items()};calls=[]
   def hook(uc,a,size,_):
    if a not in cuts:return
    name=cuts[a];calls.append(name)
    uc.reg_write(UC_ARM_REG_R0,role if name=='audio_dm_conn_role' else getter if name=='audio_ble_connection_get' else flags if name=='audio_log_level' else 0)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['audio_ble_handler_4b7d32'] if compiled else 0x4b7d32)|1,0x600000,count=2000)
   rows.append(calls)
  assert rows[0]==rows[1],((event,connection,role,getter,flags),rows)
  print('PASS',hex(event),connection,rows[0])
