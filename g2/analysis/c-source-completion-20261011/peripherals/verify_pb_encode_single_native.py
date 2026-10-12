#!/usr/bin/env python3
"""Actual C/native single-field dispatch over all 16 nanopb low types."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_pb_encode_single.c'
N=['tag_490d66','bool_490e90','int_490eae','fixed_490f72','bytes_490fa2','string_490fe4','submessage_49104c','fixed_length_bytes_4910e8']
A=[0x490d66,0x490e90,0x490eae,0x490f72,0x490fa2,0x490fe4,0x49104c,0x4910e8]
STUB='\n'.join('unsigned audio_pb_encode_'+n+'(void *a,const void *b){(void)a;(void)b;return 1;}' for n in N)
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_encode_single_490a46',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 total=0
 for typ in range(16):
  for data_present,fail_tag in [(False,False),(True,False),(True,True)]:
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    stream=0x20080000;it=0x20081000;u.mem_write(stream,bytes(20));u.mem_write(it,bytes(40));u.mem_write(it+22,bytes([typ]));u.mem_write(it+28,struct.pack('<I',0x20082000 if data_present else 0))
    addr=[sy['audio_pb_encode_'+n]&~1 for n in N] if is_c else A;calls=[]
    def hook(uc,pc,n,user):
     ix=addr.index(pc);calls.append(ix);uc.reg_write(UC_ARM_REG_R0,0 if (ix==0 and fail_tag) else 1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    for a in addr:u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
    u.reg_write(UC_ARM_REG_R0,stream);u.reg_write(UC_ARM_REG_R1,it);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.emu_start((sy['audio_pb_encode_single_490a46'] if is_c else 0x490a46)|1,0x600000,count=1000)
    ptr=struct.unpack('<I',u.mem_read(stream+16,4))[0];err=bytes(u.mem_read(ptr,19)).split(b'\0')[0] if ptr else b''
    pair.append((calls,u.reg_read(UC_ARM_REG_R0),err))
   assert pair[0]==pair[1],(typ,data_present,fail_tag,pair)
   total+=1
print('PASS_PB_ENCODE_SINGLE_NATIVE',total)
