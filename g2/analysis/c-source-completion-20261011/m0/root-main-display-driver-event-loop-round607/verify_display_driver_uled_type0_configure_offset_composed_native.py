#!/usr/bin/env python3
"""Compare JBD4010 configure native/C command sequence and output."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callees=[('display_driver_uled_mode_45a568',0x45a568),('display_driver_uled_type0_context_46bfe8',0x46bfe8),('display_driver_uled_type0_context_snapshot_46c410',0x46c410),('display_driver_uled_command_5926ee',0x5926ee),('audio_ble_hci_radio_reset_4910f4',0x4910f4),('display_driver_uled_delay_449376',0x449376),('display_driver_uled_type0_frame_start_5931c0',0x5931c0),('audio_ble_hci_boot_delay_491102',0x491102),('g2_flashdb_candidate_flags',0x43d0ce),('g2_flashdb_candidate_log',0x43d574),('audio_log_simple',0x43ce9e)]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('typedef unsigned u32;\n'+'\n'.join(f'u32 {name}(u32 a,u32 b,u32 c,u32 d,u32 e,u32 f,u32 g,u32 h){{return 0;}}' for name,at in callees))
 image=Path(directory)/'configure.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_type0_configure.c'),str(here/'display_driver_uled_type0_set_offset.c'),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for flags in (0,1,2,4,7):
  observations=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
   u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
   for base,data in segments:u.mem_write(base,data)
   u.mem_write(0x20003994+0x2c,b'\x09\x0b')
   calls=[]
   def memzero(uc,at,size,user):
    dst=uc.reg_read(UC_ARM_REG_R0);n=uc.reg_read(UC_ARM_REG_R1);v=uc.reg_read(UC_ARM_REG_R2)
    uc.mem_write(dst,bytes([v&255])*n);uc.reg_write(UC_ARM_REG_R0,dst);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   if not compiled:u.hook_add(UC_HOOK_CODE,memzero,begin=0x43c0e4,end=0x43c0e4)
   def lower(uc,at,size,user):
    name=next(n for n,a in callees if (syms[n]&~1 if compiled else a)==at)
    regs=tuple(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3));sp=uc.reg_read(UC_ARM_REG_SP)
    if name=='display_driver_uled_mode_45a568':calls.append((name,));value=0
    elif name=='display_driver_uled_type0_context_46bfe8':calls.append((name,));value=17
    elif name=='display_driver_uled_type0_context_snapshot_46c410':
     calls.append((name,regs[0]));uc.mem_write(regs[1],(0x1234).to_bytes(4,'little'));uc.mem_write(regs[2],(0x5678).to_bytes(4,'little'));value=0
    elif name=='display_driver_uled_command_5926ee':calls.append((name,regs[0],regs[2],bytes(uc.mem_read(regs[1],regs[2])) if regs[2] else b''));value=0
    elif name=='g2_flashdb_candidate_flags':calls.append((name,));value=flags
    elif name=='g2_flashdb_candidate_log':calls.append((name,regs,tuple(int.from_bytes(uc.mem_read(sp+4*i,4),'little') for i in range(4))));value=0
    elif name=='audio_log_simple':calls.append((name,regs,int.from_bytes(uc.mem_read(sp,4),'little')));value=0
    elif name=='display_driver_uled_type0_frame_start_5931c0':calls.append((name,));value=0
    else:calls.append((name,regs[0]));value=0
    uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for name,at in callees:
    target=syms[name]&~1 if compiled else at;u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((syms['display_driver_uled_type0_step_5927ca'] if compiled else 0x5927ca)|1,0x600000,count=4000)
   observations.append((calls,u.reg_read(UC_ARM_REG_R0)))
  assert observations[0]==observations[1],(flags,observations)
  cases+=1
 print('PASS_ULED_TYPE0_CONFIGURE_OFFSET_COMPOSED_NATIVE',cases)
