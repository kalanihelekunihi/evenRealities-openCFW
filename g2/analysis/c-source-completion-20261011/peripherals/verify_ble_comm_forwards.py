"""Actual ARM C/native BLE application forward-chain comparison."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_comm_forwards.c'
EXT={'audio_ble_adv_message_preprocess':0x46e098,'audio_ble_msgtx_message':0x4782dc,
 'audio_ble_ota_message':0x4bdd70,'audio_ble_eus_message':0x4bdfe6,'audio_ble_ess_message':0x4be2e8,
 'audio_ble_efs_message':0x4be572,'audio_ble_nus_message':0x4be848,'audio_ble_ancc_message':0x4bf780,
 'audio_ble_master_message_preprocess':0x4a06d4,'audio_ble_master_message':0x4c4910}
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text('\n'.join('void '+k+'(){}' for k in EXT));elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_comm_forward_a',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for name,stock in (('audio_ble_comm_forward_a',0x46ef74),('audio_ble_comm_forward_b',0x4a19c0)):
  for message in (0,0x20001000):
   rows=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in segs:u.mem_write(a,d)
    for r,v in [(UC_ARM_REG_R0,4),(UC_ARM_REG_R1,message),(UC_ARM_REG_R2,0x55),(UC_ARM_REG_R3,0x12345678),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)]:u.reg_write(r,v)
    cuts={(syms[k]&~1 if compiled else v):k for k,v in EXT.items()};calls=[]
    def hook(uc,a,size,_):
     if a not in cuts:return
     calls.append(cuts[a]);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook);u.emu_start((syms[name] if compiled else stock)|1,0x600000,count=2000)
    rows.append((calls,u.reg_read(UC_ARM_REG_R0)))
   assert rows[0]==rows[1],(name,message,rows)
   print('PASS',name,hex(message),rows[0])
