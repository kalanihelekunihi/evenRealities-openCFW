#!/usr/bin/env python3
"""Actual C/native callback and first-char predicate branch effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_pb_encode_callback.c'
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'c.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_encode_callback_490aea',str(S),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 total=0
 for mode in ('callback','char'):
  cases=[(False,0,False),(True,0,False),(True,1,False),(True,0,True)] if mode=='callback' else [(False,0,False),(True,0,False)]
  for has_cb,result,existing in cases:
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    stream=0x20080000;it=0x20081000;desc=0x20082000;value=0x20083000;cb=0x20084000
    u.mem_write(stream,bytes(20));u.mem_write(it,bytes(40));u.mem_write(desc,bytes(16));u.mem_write(it,struct.pack('<I',desc));u.mem_write(desc+12,struct.pack('<I',cb+1 if has_cb else 0));u.mem_write(value,bytes([1 if has_cb else 0]))
    if existing:u.mem_write(stream+16,struct.pack('<I',0x787cf0))
    calls=[]
    def hook(uc,pc,n,user):
     calls.append((uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
     uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=cb,end=cb)
    u.reg_write(UC_ARM_REG_R0,stream if mode=='callback' else value);u.reg_write(UC_ARM_REG_R1,it);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    addr=(sy['audio_pb_encode_callback_490aea'] if mode=='callback' else sy['audio_pb_first_char_nonzero_490678']) if is_c else (0x490aea if mode=='callback' else 0x490678)
    u.emu_start(addr|1,0x600000,count=1000)
    ptr=struct.unpack('<I',u.mem_read(stream+16,4))[0];err=bytes(u.mem_read(ptr,15)).split(b'\0')[0] if ptr else b''
    pair.append((calls,u.reg_read(UC_ARM_REG_R0),err))
   assert pair[0]==pair[1],(mode,has_cb,result,existing,pair)
   total+=1
print('PASS_PB_ENCODE_CALLBACK_NATIVE',total)
