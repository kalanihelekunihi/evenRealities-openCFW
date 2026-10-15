#!/usr/bin/env python3
"""Compare four uLED option callbacks to native with setup lower calls bounded."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
def set32(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
entries=[('display_driver_uled_option_type0_setup_592680',0x592680),
         ('display_driver_uled_option_type1_setup_5bbd70',0x5bbd70),
         ('display_driver_uled_option_type1_mask_5bcc10',0x5bcc10),
         ('display_driver_uled_option_type1_noop_5bd39c',0x5bd39c)]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c'
 stub.write_text('''typedef unsigned u32;
u32 display_driver_uled_option_config_59cf1a(u32 a,u32 b,u32 c,u32 d){
 *(volatile u32 *)0x20001000u=a;*(volatile u32 *)0x20001004u=b;
 *(volatile u32 *)0x20001008u=c;*(volatile u32 *)0x2000100cu=d;return 0;
}
u32 display_driver_uled_option_type0_enable_5926b4(u32 a){
 *(volatile u32 *)0x20001010u=0x10u;*(volatile u32 *)0x20001014u=a;return 0x33u;
}
u32 display_driver_uled_option_type1_enable_5bbda4(u32 a){
 *(volatile u32 *)0x20001010u=0x11u;*(volatile u32 *)0x20001014u=a;return 0x33u;
}
''')
 image=Path(directory)/'callbacks.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
  '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
  '-Wl,-Ttext=0x100000',str(here/'display_driver_uled_option_setup_pair.c'),
  str(here/'display_driver_uled_option_leaf_pair.c'),
  str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for name,native in entries:
  for value in (0,1,0x12345678,0xffffffff):
   for cell in (0,0x20090000):
    observed=[]
    for compiled in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
     u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
     for base,data in segments:u.mem_write(base,data)
     set32(u,0x20074524,cell);set32(u,0x20074510,cell)
     if not compiled:
      def lower(uc,at,size,user):
       if at==0x59cf1a:
        for i,reg in enumerate((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)):
         set32(uc,0x20001000+4*i,uc.reg_read(reg))
        uc.reg_write(UC_ARM_REG_R0,0)
       else:
        set32(uc,0x20001010,0x10 if at==0x5926b4 else 0x11)
        set32(uc,0x20001014,uc.reg_read(UC_ARM_REG_R0))
        uc.reg_write(UC_ARM_REG_R0,0x33)
       uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
      for target in (0x59cf1a,0x5926b4,0x5bbda4):
       u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
     u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
     u.reg_write(UC_ARM_REG_R0,value)
     u.reg_write(UC_ARM_REG_R1,0x87654321)
     u.reg_write(UC_ARM_REG_R2,0x11223344)
     u.emu_start((syms[name] if compiled else native)|1,0x600000,count=2000)
     observed.append((u.reg_read(UC_ARM_REG_R0),
       bytes(u.mem_read(0x20074510,0x20)),bytes(u.mem_read(0x20001000,0x18))))
    assert observed[0]==observed[1],(name,value,cell,observed)
    cases+=1
 print('PASS_DISPLAY_DRIVER_ULED_OPTION_SMALL_CALLBACKS_NATIVE',cases)
