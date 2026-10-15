#!/usr/bin/env python3
"""Native/C comparison for two option IRQ wrappers with Ambiq status/clear C."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_PRIMASK,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
root=here.parents[3]
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
foundation=root/'components/foundation/ambiq_mspi/ambiq_mspi_interrupts.c'
def set32(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'service.c'
 stub.write_text('''typedef unsigned u32;
u32 am_hal_mspi_interrupt_service(void *h,u32 s){
 *(volatile u32 *)0x20001000u=(u32)h;
 *(volatile u32 *)0x20001004u=s;
 return 0u;
}
''')
 image=Path(directory)/'irq.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
  '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
  '-Wl,-Ttext=0x100000',str(here/'display_driver_uled_option_irq_pair.c'),
  str(foundation),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 entries=[('display_driver_uled_option_type0_irq_592658',0x592658,0x20074524),
          ('display_driver_uled_option_type1_irq_5bbd48',0x5bbd48,0x20074510)]
 for name,native,cell in entries:
  for present in (0,1):
   for module in (0,1,2):
    for status in (0,0x1a80,0xffffffff):
     observed=[]
     for compiled in (False,True):
      u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
      u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
      u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
      u.mem_map(0x40060000,0x3000)
      for base,data in segments:u.mem_write(base,data)
      set32(u,cell,0x20080000 if present else 0)
      set32(u,0x20080000,0x01bebebe);set32(u,0x20080004,module)
      reg=0x40060000+module*0x1000
      set32(u,reg+0x204,status)
      trace=[]
      def mmio(uc,kind,address,size,value,user):
       if 0x40060000<=address<0x40063000:trace.append((kind,address,size,value if kind==UC_HOOK_MEM_WRITE else None))
      u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mmio)
      if not compiled:
       def service(uc,address,size,user):
        set32(uc,0x20001000,uc.reg_read(UC_ARM_REG_R0))
        set32(uc,0x20001004,uc.reg_read(UC_ARM_REG_R1))
        uc.reg_write(UC_ARM_REG_R0,0)
        uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
       u.hook_add(UC_HOOK_CODE,service,begin=0x4c240e,end=0x4c240e)
      u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
      u.reg_write(UC_ARM_REG_PRIMASK,1)
      u.emu_start((syms[name] if compiled else native)|1,0x600000,count=3000)
      observed.append((bytes(u.mem_read(0x20001000,8)),
                       bytes(u.mem_read(reg+0x200,12)),trace))
     assert observed[0]==observed[1],(name,present,module,status,observed)
     cases+=1
 print('PASS_DISPLAY_DRIVER_ULED_OPTION_IRQ_PAIR_NATIVE',cases)
