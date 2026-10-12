#!/usr/bin/env python3
"""Actual C/native wire type, tag key and invalid diagnostic effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_pb_encode_tag.c'
STUB='''unsigned audio_pb_write_varint_490ce0(void *s,unsigned a,unsigned b,unsigned c){(void)s;(void)a;(void)b;(void)c;return 1;}'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_encode_tag_490d66',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 total=0
 for typ in range(16):
  for tag in (1,129):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    stream=0x20080000;it=0x20081000;u.mem_write(stream,bytes(20));u.mem_write(it,bytes(40));u.mem_write(it+16,struct.pack('<H',tag));u.mem_write(it+22,bytes([typ]))
    cut=(sy['audio_pb_write_varint_490ce0']&~1) if is_c else 0x490ce0;calls=[]
    def hook(uc,pc,n,user):
     calls.append(tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)))
     uc.reg_write(UC_ARM_REG_R0,1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=cut,end=cut)
    u.reg_write(UC_ARM_REG_R0,stream);u.reg_write(UC_ARM_REG_R1,it);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.emu_start((sy['audio_pb_encode_tag_490d66'] if is_c else 0x490d66)|1,0x600000,count=1000)
    ptr=struct.unpack('<I',u.mem_read(stream+16,4))[0];err=bytes(u.mem_read(ptr,19)).split(b'\0')[0] if ptr else b''
    pair.append((calls,u.reg_read(UC_ARM_REG_R0),err))
   assert pair[0]==pair[1],(typ,tag,pair)
   total+=1
print('PASS_PB_ENCODE_TAG_NATIVE',total)
