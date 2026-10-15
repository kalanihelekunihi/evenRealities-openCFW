#!/usr/bin/env python3
"""Compare the used binary osSemaphoreNew path against selected C provider."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
source=here.parents[3]/'components/audio/uart_thread_source_candidate/semaphore_new.c'
callees=[('audio_cmsis_irq_context',0x44900e),('audio_queue_create_dynamic',0x441636),('audio_queue_create_static',0x4415ca),('audio_uart_queue_send',0x4417ee),('audio_queue_delete',0x441ea2)]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('typedef unsigned u32;\n'+'\n'.join(f'u32 {name}(u32 a,u32 b,u32 c,u32 d,u32 e,u32 f,u32 g,u32 h){{return 0;}}' for name,at in callees))
 image=Path(directory)/'sem.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for maximum in (0,1):
  for initial in (0,1):
   for context in (0,1):
    for attr in ('none','invalid','static'):
     for give_result in (0,1):
      observations=[]
      for compiled in (False,True):
       u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
       u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
       for base,data in segments:u.mem_write(base,data)
       if attr!='none':
        u.mem_write(0x20001008,(0x20002000 if attr=='static' else 0x20002000).to_bytes(4,'little'))
        u.mem_write(0x2000100c,(0x50 if attr=='static' else 0x20).to_bytes(4,'little'))
       calls=[]
       def lower(uc,at,size,user):
        name=next(n for n,a in callees if (syms[n]&~1 if compiled else a)==at)
        regs=tuple(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
        if name=='audio_cmsis_irq_context':calls.append((name,));value=context
        elif name=='audio_queue_create_dynamic':calls.append((name,regs[:3]));value=0x20003000
        elif name=='audio_queue_create_static':calls.append((name,regs, int.from_bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4),'little')));value=0x20003000
        elif name=='audio_uart_queue_send':calls.append((name,regs));value=give_result
        else:calls.append((name,regs[0]));value=0
        uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
       for name,at in callees:
        target=syms[name]&~1 if compiled else at;u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
       u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
       u.reg_write(UC_ARM_REG_R0,maximum);u.reg_write(UC_ARM_REG_R1,initial);u.reg_write(UC_ARM_REG_R2,0 if attr=='none' else 0x20001000)
       u.emu_start((syms['audio_uart_sync_sem_new'] if compiled else 0x44989a)|1,0x600000,count=500)
       observations.append((calls,u.reg_read(UC_ARM_REG_R0)))
      assert observations[0]==observations[1],(maximum,initial,context,attr,give_result,observations)
      cases+=1
 print('PASS_ULED_BINARY_SEMAPHORE_NEW_NATIVE',cases)
