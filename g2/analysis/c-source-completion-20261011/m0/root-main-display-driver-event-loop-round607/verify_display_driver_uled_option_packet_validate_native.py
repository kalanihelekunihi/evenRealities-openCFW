#!/usr/bin/env python3
"""Compare S200 packet validator branches with direct native execution."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callees=[('g2_flashdb_candidate_flags',0x43d0ce),('g2_flashdb_candidate_log',0x43d574),('audio_log_simple',0x43ce9e)]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('typedef unsigned u32;\n'+'\n'.join(f'u32 {name}(u32 a,u32 b,u32 c,u32 d,u32 e,u32 f){{return 0;}}' for name,at in callees))
 image=Path(directory)/'validate.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_option_packet_validate.c'),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for variant in ('null','no_device','no_buffer','valid'):
  for flags in (0,1,2,4,7):
   observed=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
    u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
    for base,data in segments:u.mem_write(base,data)
    packet=0 if variant=='null' else 0x20001000
    u.mem_write(0x20001014,(0 if variant=='no_buffer' else 0x20005000).to_bytes(4,'little'))
    u.mem_write(0x20001018,(0 if variant=='no_device' else 0x20074200).to_bytes(4,'little'))
    calls=[]
    def lower(uc,at,size,user):
     name=next(n for n,a in callees if (syms[n]&~1 if compiled else a)==at)
     regs=tuple(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
     calls.append((name,regs[:0 if name=='g2_flashdb_candidate_flags' else 3 if name=='audio_log_simple' else 4]))
     uc.reg_write(UC_ARM_REG_R0,flags if name=='g2_flashdb_candidate_flags' else 0)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    for n,at in callees:
     target=syms[n]&~1 if compiled else at
     u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.reg_write(UC_ARM_REG_R0,packet);u.reg_write(UC_ARM_REG_R1,0x776e44)
    u.emu_start((syms['display_driver_uled_packet_validate_59cb42'] if compiled else 0x59cb42)|1,0x600000,count=1000)
    observed.append((calls,u.reg_read(UC_ARM_REG_R0)))
   assert observed[0]==observed[1],(variant,flags,observed)
   cases+=1
 print('PASS_ULED_OPTION_PACKET_VALIDATE_NATIVE',cases)
