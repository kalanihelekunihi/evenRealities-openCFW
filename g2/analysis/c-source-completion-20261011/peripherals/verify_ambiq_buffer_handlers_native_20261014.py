#!/usr/bin/env python3
"""Compare Ambiq buffer table and eight wrapper dispatches with Apollo S200."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/handlers.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
wrappers=[('audio_uart_ambiq_buffer_call_base_53d56a',0x53d56a),('audio_uart_ambiq_buffer_call_update_53d57a',0x53d57a),('audio_uart_ambiq_buffer_call_mask_53d586',0x53d586),('audio_uart_ambiq_buffer_call_layout_53d594',0x53d594),('audio_uart_ambiq_buffer_call_base2_53d5a2',0x53d5a2),('audio_uart_ambiq_buffer_call_update2_53d5b2',0x53d5b2),('audio_uart_ambiq_buffer_call_mask2_53d5be',0x53d5be),('audio_uart_ambiq_buffer_call_layout2_53d5cc',0x53d5cc)]
lowers=[('audio_uart_ambiq_buffer_base_53cf78',0x53cf78),('audio_uart_ambiq_buffer_update_53cf8a',0x53cf8a),('audio_uart_ambiq_buffer_mask_53d006',0x53d006),('audio_uart_ambiq_buffer_layout_53d062',0x53d062)]
direct=[('audio_uart_ambiq_buffer_round_bytes_53cfe4',0x53cfe4),('audio_uart_ambiq_buffer_format_bytes_53cff0',0x53cff0),('audio_uart_ambiq_buffer_blend_53d0b6',0x53d0b6),('audio_uart_ambiq_buffer_render_53d25a',0x53d25a)]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('typedef unsigned u32;\n'+'\n'.join(f'u32 {name}(u32 a,u32 b,u32 c){{return 0;}}' for name,at in lowers+direct))
 image=Path(directory)/'handlers.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def engine():
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
  for base,data in segments:u.mem_write(base,data)
  u.mem_write(0x2006f548,bytes([0xa5])*0x128)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  return u
 native=engine();compiled=engine()
 native.emu_start(0x53d5db,0x600000,count=300)
 compiled.emu_start(syms['audio_uart_ambiq_buffer_handlers_53d5da']|1,0x600000,count=300)
 table_native=[int.from_bytes(native.mem_read(0x2006f548+i*4,4),'little') for i in range(0x128//4)]
 table_source=[int.from_bytes(compiled.mem_read(0x2006f548+i*4,4),'little') for i in range(0x128//4)]
 normalize={syms[n]:a|1 for n,a in wrappers+direct}
 assert [normalize.get(v,v) for v in table_source]==table_native,(table_native,table_source)
 count=0
 for name,at in wrappers:
  for a,b in ((0,0),(0x12345678,0x102),(0xffffffff,0xff)):
   results=[]
   for is_source in (False,True):
    u=engine();calls=[]
    def lower(uc,pc,size,user):
     target=next(n for n,x in lowers if (syms[n]&~1 if is_source else x)==pc)
     r=tuple(uc.reg_read(z) for z in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
     calls.append((target,r));uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    for n,x in lowers:
     target=syms[n]&~1 if is_source else x;u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
    u.reg_write(UC_ARM_REG_R0,a);u.reg_write(UC_ARM_REG_R1,b)
    u.emu_start((syms[name] if is_source else at)|1,0x600000,count=100)
    results.append(calls)
   assert results[0]==results[1],(name,a,b,results)
   count+=1
 print('PASS_AMBIQ_BUFFER_HANDLERS_NATIVE',len(table_native),count)
