#!/usr/bin/env python3
"""Actual compiled C/native nanopb varint bytes and stream effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
D=R/'components/audio/uart_thread_source_candidate'
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_write_varint_490ce0',str(D/'display_pb_varint.c'),str(D/'display_pb_stream_write.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 values=[(0,0),(1,0),(127,0),(128,0),(300,0),(0xffffffff,0),(0,1),(0xffffffff,0xffffffff)]
 total=0
 for low,high in values:
  for max_size,cb_result in ((20,1),(1,1),(20,0)):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    stream=0x20080000;cb=0x20084000;u.mem_write(stream,struct.pack('<IIIII',cb+1,0,max_size,0,0));calls=[]
    def hook(uc,pc,n,user):
     ptr=uc.reg_read(UC_ARM_REG_R1);count=uc.reg_read(UC_ARM_REG_R2)
     calls.append(bytes(uc.mem_read(ptr,count)))
     uc.reg_write(UC_ARM_REG_R0,cb_result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=cb,end=cb)
    u.reg_write(UC_ARM_REG_R0,stream);u.reg_write(UC_ARM_REG_R1,0);u.reg_write(UC_ARM_REG_R2,low);u.reg_write(UC_ARM_REG_R3,high);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.emu_start((sy['audio_pb_write_varint_490ce0'] if is_c else 0x490ce0)|1,0x600000,count=3000)
    written=struct.unpack('<I',u.mem_read(stream+12,4))[0];ptr=struct.unpack('<I',u.mem_read(stream+16,4))[0]
    err=bytes(u.mem_read(ptr,12)).split(b'\0')[0] if ptr else b''
    pair.append((calls,written,u.reg_read(UC_ARM_REG_R0),err))
   assert pair[0]==pair[1],(low,high,max_size,cb_result,pair)
   total+=1
print('PASS_PB_VARINT_STREAM_NATIVE',total)
