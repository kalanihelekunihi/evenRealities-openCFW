#!/usr/bin/env python3
"""Compare Apollo NEMA mode calls and generated instruction words."""
from pathlib import Path
import json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,
                               UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP)
base=Path(__file__).parent
sources=[base/'display_driver_nema_mode.c',base/'display_driver_nema_mode_tables.c']
blob=(Path(__file__).resolve().parents[4]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
targets=[('display_driver_nema_select_522a16',0x522a16,'select'),
         ('display_driver_gpu_mode_mask_4b1588',0x4b1588,'mask'),
         ('audio_uart_nema_rop_blend_mode_522956',0x522956,'blend'),
         ('display_driver_nema_mode_control_5226d6',0x5226d6,'control'),
         ('audio_uart_nema_instruction_upload_522920',0x522920,'upload'),
         ('display_driver_nema_mode_commit_52294c',0x52294c,'commit')]
with tempfile.TemporaryDirectory() as directory:
 d=Path(directory);stub=d/'stubs.s'
 stub.write_text('.syntax unified\n.thumb\n.text\n'+''.join(
  f'.global {name}\n.thumb_func\n{name}:\n bx lr\n' for name,_,_ in targets)+
  '.bss\n.global audio_uart_nema_context_cell\n'
  'audio_uart_nema_context_cell:\n.space 4\n'
  '.global audio_uart_nema_boot_state_200043a8\n'
  'audio_uart_nema_boot_state_200043a8:\n.space 8\n')
 image=d/'mode.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000',*[str(x) for x in sources],str(stub),'-o',str(image)],
                check=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=[]
 for mode in (1,0,0x101,2,0x100,0x1000000,0x80000000,0x40000001,
              0x20000001,0x10000001,0x40000102):
  for surface in (0xffffffff,0,1):
   cases.append((mode,0,surface,0xffffffff,0,0,0))
 for mode in (1,0x101,2,0x80000000,0x20000001):
  cases.append((mode,1,0xffffffff,2,1,0,0))
 for mode in (1,2,0x101):
  cases.append((mode,0,0xffffffff,0xffffffff,0,1,1))
 for low in range(16):
  for high in range(4):
   for flag in (0,1<<20,1<<21,1<<22,1<<23,1<<25,
                1<<26,1<<27,1<<28,1<<29,1<<30,1<<31):
    cases.append((flag|(high<<8)|low,0,0xffffffff,0xffffffff,0,0,0))
 failures=[]
 for mode,target,surface,alternate,boot_flag,override,context_bit in cases:
  observations=[]
  for compiled in (False,True):
   cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
   cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
   cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
   for address,data in segments:cpu.mem_write(address,data)
   context=0x20090000
   cell=syms['audio_uart_nema_context_cell'] if compiled else 0x20074efc
   boot=syms['audio_uart_nema_boot_state_200043a8'] if compiled else 0x200043a8
   cpu.mem_write(cell,context.to_bytes(4,'little'))
   cpu.mem_write(context,bytes([0])*0x80)
   cpu.mem_write(context+10,bytes([context_bit]))
   cpu.mem_write(boot,bytes([boot_flag,override,0,0])+(0x8000).to_bytes(4,'little'))
   cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
   for reg,val in ((UC_ARM_REG_R0,mode),(UC_ARM_REG_R1,target),
                   (UC_ARM_REG_R2,surface)):
    cpu.reg_write(reg,val)
   from unicorn.arm_const import UC_ARM_REG_R3
   cpu.reg_write(UC_ARM_REG_R3,alternate)
   hook_targets={(syms[name] if compiled else address)&~1:label
                 for name,address,label in targets}
   events=[]
   def hook(u,address,_size,_user):
    label=hook_targets.get(address)
    if label is None:return
    r0=u.reg_read(UC_ARM_REG_R0);r1=u.reg_read(UC_ARM_REG_R1)
    if label=='upload':
     count=r1
     assert count<=16,(mode,count)
     events.append((label,count,u.reg_read(UC_ARM_REG_R2),
                    bytes(u.mem_read(r0,count*8)).hex()))
    else:events.append((label,r0))
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   cpu.hook_add(UC_HOOK_CODE,hook)
   start=syms['display_driver_nema_mode_513924'] if compiled else 0x513924
   cpu.emu_start(start|1,0x600000,count=3000)
   observations.append(events)
  if observations[0]!=observations[1]:
   failures.append((hex(mode),target,hex(surface),hex(alternate),boot_flag,
                    override,context_bit,observations))
 print('DISPLAY_DRIVER_NEMA_MODE_NATIVE',len(cases)-len(failures),
       'passed of',len(cases),'cases;',len(failures),'mismatches')
 report=base/'nema-mode-round649-discriminator.json'
 report.write_text(json.dumps({'cases':len(cases),'passed':len(cases)-len(failures),
                               'mismatches':failures},indent=2)+'\n')
 for failure in failures[:5]:print('MISMATCH',failure)
 assert not failures,'NEMA mode draft remains unadmitted'
