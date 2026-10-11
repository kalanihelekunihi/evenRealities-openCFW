#!/usr/bin/env python3
"""Bounded original-byte/source checks for nonfloat Main IAR formatting."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
SRC=R/'g2/components/main/full_formatter_outer_candidate';E=D/'main-general-oracle.elf'
objects=[]
for name in ('general_format','float_bridge','float_render','fp_primitives'):
 o=D/('main-'+name+'-m4.o')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mfpu=fpv5-d16','-mfloat-abi=softfp',
                 '-mthumb','-O2','-c',str(SRC/(name+'.c')),'-o',str(o)],check=True)
 objects.append(o)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=__aeabi_memclr4=0x11f001',
                '--defsym=__aeabi_memcpy=0x11f011',
                '-o',str(E),*map(str,objects)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,fmt,args):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M7)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(a,n)
 u.mem_write(0x438000,B)
 if not stock:
  for a,d in segs:u.mem_write(a,d)
 def w(a,v):u.mem_write(a,int(v&0xffffffff).to_bytes(4,'little'))
 def rd(a):return int.from_bytes(u.mem_read(a,4),'little')
 ctx,buf,format_addr,cursor,words,sp=0x20001000,0x20002000,0x20003000,0x20004000,0x20005000,0x200f0000
 u.mem_write(buf,b'\xa5'*256);u.mem_write(format_addr,fmt.encode()+b'\x00')
 u.mem_write(0x20006000,b'hello world\x00')
 w(0x200044ac,0x20007000);u.mem_write(0x20007000,b'.\x00')
 for i,v in enumerate(args):w(words+4*i,v)
 w(ctx,buf);w(ctx+4,255);w(ctx+8,0);w(cursor,words);w(sp,0)
 for reg,val in ((A.UC_ARM_REG_R0,0x439c8b),(A.UC_ARM_REG_R1,ctx),(A.UC_ARM_REG_R2,format_addr),(A.UC_ARM_REG_R3,cursor),(A.UC_ARM_REG_SP,sp),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,val)
 done=[False]
 def hook(cpu,pc,size,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop()
  elif pc==0x11f000:
   cpu.mem_write(cpu.reg_read(A.UC_ARM_REG_R0),b'\x00'*cpu.reg_read(A.UC_ARM_REG_R1))
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  elif pc==0x11f010:
   cpu.mem_write(cpu.reg_read(A.UC_ARM_REG_R0),bytes(cpu.mem_read(cpu.reg_read(A.UC_ARM_REG_R1),cpu.reg_read(A.UC_ARM_REG_R2))))
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 try:u.emu_start((0x481836 if stock else sy['g2_iar_general_format'])|1,0,count=50000)
 except Exception as error:raise AssertionError((stock,fmt,hex(u.reg_read(A.UC_ARM_REG_PC)),str(error))) from error
 assert done[0],(stock,fmt)
 return u.reg_read(A.UC_ARM_REG_R0),bytes(u.mem_read(buf,rd(ctx+8))),rd(ctx+8),rd(cursor)-words
# This default oracle deliberately excludes FP: Unicorn's Cortex-M7 model
# faults on a stock VFP helper instruction at 0x4d435c for the first %f case.
cases=[('plain',[]),('%%',[]),('%c',[65]),('%d',[123]),('%d',[0xffffffff]),('%u',[0xffffffff]),('%x',[0x1234]),('%X',[0x1234]),('%o',[0x1234]),('%p',[0x1234]),('%08x',[0x1234]),('%-8d',[42]),('%+d',[42]),('% d',[42]),('%#x',[0x1234]),('%.4d',[23]),('%8.4d',[23]),('%04d',[23]),('%qX',[0,0x1234,0]),('%qd',[0,0xffffffff,0]),('%s',[0x20006000]),('%.5s',[0x20006000]),('%10s',[0x20006000]),('%*d',[8,42]),('%*d',[0xfffffff8,42]),('%.*s',[5,0x20006000]),('x:%d y:%x',[42,0xabcd])]
n=0
for fmt,args in cases:
 a=run(True,fmt,args);b=run(False,fmt,args)
 assert a==b,(fmt,args,a,b)
 n+=1
print('PASS_MAIN_GENERAL_FORMAT',n)
