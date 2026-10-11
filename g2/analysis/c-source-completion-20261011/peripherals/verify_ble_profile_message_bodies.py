"""Actual ARM C/native BLE profile state and call comparison."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_profile_message_bodies.c'
FAMILIES=[('ota',0x4bdc0c,0x200748b4,0xa7),('eus',0x4bded6,0x200748ac,0xa8),('ess',0x4be24e,0x200748a8,0xa9),('efs',0x4be420,0x200748a4,0xaa),('nus',0x4be76c,0x200748b0,0xab)]
CHILD={'audio_dm_conn_role':0x4b73c4,'audio_ble_ota_update':0x4bdb90,'audio_ble_eus_update':0x4bde4c,
 'audio_ble_ess_update':0x4be228,'audio_ble_efs_update':0x4be3a4,'audio_ble_nus_update':0x4be6f0,
 'audio_ble_ota_disconnect':0x448784,'audio_ble_ota_reset_event':0x4d3534,
 'audio_ble_ota_connection_changed':0x4bb04a,'audio_event_loop_push_delayed':0x47697e,
 'audio_ble_profile_write_event':0x533ed8}
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text('#include <stdint.h>\n'+
  '\n'.join('uint8_t audio_ble_'+n+'_handler_state[4];' for n,_,_,_ in FAMILIES)+'\n'+
  'void audio_ble_ota_delayed_callback(void){}\n'+
  '\n'.join('unsigned '+k+'(){return 1;}' for k in CHILD));elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_ota_message_body',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for name,entry,state,write_event in FAMILIES:
  for event,status,role in ((0x12,0,1),(0x12,1,1),(0x14,0,1),(0x28,0,1),(0x27,0,1),(write_event,0,1)) + (((0xa0,0,1),(0xa1,0,1)) if name=='ota' else ()):
   rows=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in segs:u.mem_write(a,d)
    cell=(syms['audio_ble_'+name+'_handler_state']&~1) if compiled else state
    u.mem_write(cell,b'\x05\x06\x07\x08')
    msg=bytearray(16);msg[0]=1;msg[2]=event;msg[3]=status;msg[4:8]=b'ABCD';msg[8:10]=b'EF';u.mem_write(0x20001000,bytes(msg))
    u.reg_write(UC_ARM_REG_R0,0x20001000);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    cuts={(syms[k]&~1 if compiled else v):k for k,v in CHILD.items()};calls=[]
    def hook(uc,a,size,_):
     if a not in cuts:return
     k=cuts[a]
     if k=='audio_event_loop_push_delayed':calls.append((k,uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)))
     else:calls.append((k,uc.reg_read(UC_ARM_REG_R0) if k in ('audio_dm_conn_role','audio_ble_ota_reset_event','audio_ble_ota_connection_changed','audio_ble_profile_write_event','audio_ble_ota_update','audio_ble_eus_update','audio_ble_ess_update','audio_ble_efs_update','audio_ble_nus_update') else None))
     uc.reg_write(UC_ARM_REG_R0,role if k=='audio_dm_conn_role' else 0)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((syms['audio_ble_'+name+'_message_body'] if compiled else entry)|1,0x600000,count=1500)
    rows.append((calls,bytes(u.mem_read(cell,4))))
   assert rows[0]==rows[1],(name,event,status,rows)
   print('PASS',name,hex(event),status)
