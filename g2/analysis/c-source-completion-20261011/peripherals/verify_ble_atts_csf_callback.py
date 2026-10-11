"""Actual ARM compiled-C/native ATTS CSF callback and child comparisons."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_atts_csf_callback.c'
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text('#include <stdint.h>\nuint8_t audio_ble_atts_connection_rows[0x100];\nvoid *audio_queue_copy_bytes(void*a,const void*b,uint32_t c){(void)a;(void)b;(void)c;return a;}\n')
 elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_atts_csf_callback_53482c',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for kind,row_present,source_present in (('callback',0,1),('callback',1,0),('callback',1,1),('copy',1,1),('getter',1,1)):
  rows=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   table=syms['audio_ble_atts_connection_rows'] if compiled else 0x200717b0
   u.mem_write(table+0x30,struct.pack('<I',0x20003000 if row_present else 0))
   u.mem_write(0x20003000,b'X'*0x90);u.mem_write(0x20004000,b'Z')
   u.reg_write(UC_ARM_REG_R0,0x20003000 if kind=='copy' else 2)
   u.reg_write(UC_ARM_REG_R1,0x47)
   u.reg_write(UC_ARM_REG_R2,0x20004000 if source_present else 0)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   calls=[]
   def hook(uc,a,size,_):
    cut=(syms['audio_queue_copy_bytes']&~1 if compiled else 0x439be4)
    if a!=cut:return
    dst=uc.reg_read(UC_ARM_REG_R0);src=uc.reg_read(UC_ARM_REG_R1);n=uc.reg_read(UC_ARM_REG_R2)
    calls.append((dst,src,n));uc.mem_write(dst,bytes(uc.mem_read(src,n)))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   name={'callback':'audio_ble_atts_csf_callback_53482c','copy':'audio_ble_atts_csf_copy','getter':'audio_ble_atts_row_by_connection'}[kind]
   native={'callback':0x53482c,'copy':0x47b418,'getter':0x4bb07c}[kind]
   u.emu_start((syms[name] if compiled else native)|1,0x600000,count=700)
   rows.append((bytes(u.mem_read(0x20003000,0x90)),u.reg_read(UC_ARM_REG_R0) if kind=='getter' else 0,len(calls)))
  assert rows[0]==rows[1],(kind,row_present,source_present,rows)
  print('PASS',kind,row_present,source_present,rows[0][2])
