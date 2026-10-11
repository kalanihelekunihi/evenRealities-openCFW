"""Actual ARM C/native nonnull profile message routing comparison."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_profile_message_wrappers.c'
PAIRS=[('ota',0x4bdd70,0x4bdc0c),('eus',0x4bdfe6,0x4bded6),('ess',0x4be2e8,0x4be24e),('efs',0x4be572,0x4be420),('nus',0x4be848,0x4be76c)]
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text('\n'.join('void audio_ble_'+n+'_message_body(void *p){(void)p;}' for n,_,_ in PAIRS));elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_ota_message',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for name,stock,child in PAIRS:
  for message in (0,0x20001000):
   rows=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in segs:u.mem_write(a,d)
    u.reg_write(UC_ARM_REG_R0,5);u.reg_write(UC_ARM_REG_R1,message);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    target=(syms['audio_ble_'+name+'_message_body']&~1) if compiled else child;calls=[]
    def hook(uc,a,size,_):
     if a!=target:return
     calls.append(uc.reg_read(UC_ARM_REG_R0));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook);u.emu_start((syms['audio_ble_'+name+'_message'] if compiled else stock)|1,0x600000,count=100)
    rows.append(calls)
   assert rows[0]==rows[1],(name,message,rows)
   print('PASS',name,hex(message),rows[0])
