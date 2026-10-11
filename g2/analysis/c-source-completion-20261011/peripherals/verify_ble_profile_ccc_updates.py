"""Actual ARM C/native profile CCC state and diagnostic-call comparison."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_profile_ccc_updates.c'
FAMILIES=[('ota',0x4bdb90,0x200748b4,1),('eus',0x4bde4c,0x200748ac,2),('ess',0x4be228,0x200748a8,3),('efs',0x4be3a4,0x200748a4,4),('nus',0x4be6f0,0x200748b0,5)]
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text('#include <stdint.h>\n'+'\n'.join('uint8_t audio_ble_'+n+'_handler_state[4];' for n,_,_,_ in FAMILIES)+
 '\nunsigned audio_log_level(void){return 0;}\nvoid audio_log_extended(){}\nunsigned compressed_log_output(){return 0;}\n');elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_ota_update',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for name,entry,state,index in FAMILIES:
  for actual,value,flags in ((index,1,0),(index,2,0),(index+1,1,0),(index,1,2),(index,1,1)):
   rows=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in segs:u.mem_write(a,d)
    cell=(syms['audio_ble_'+name+'_handler_state']&~1) if compiled else state
    u.mem_write(cell,b'\x05\x06\x07\x08')
    msg=bytearray(12);msg[0]=3;msg[4:6]=b'AB';msg[6]=value;msg[8]=actual;u.mem_write(0x20001000,bytes(msg))
    u.reg_write(UC_ARM_REG_R0,0x20001000);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    cuts={(syms['audio_log_level']&~1 if compiled else 0x43d0ce):'level',
          (syms['audio_log_extended']&~1 if compiled else 0x43d574):'extended',
          (syms['compressed_log_output']&~1 if compiled else 0x43ce9e):'compressed'};calls=[]
    def hook(uc,a,size,_):
     if a not in cuts:return
     k=cuts[a];calls.append(k);uc.reg_write(UC_ARM_REG_R0,flags if k=='level' else 0)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((syms['audio_ble_'+name+'_update'] if compiled else entry)|1,0x600000,count=2000)
    rows.append((calls,bytes(u.mem_read(cell,4))))
   assert rows[0]==rows[1],(name,actual,value,flags,rows)
   print('PASS',name,actual,value,flags)
