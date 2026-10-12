"""Bounded actual ARM C/native recursive LV child movement."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_lv_move_children.c'
SHIM='''
unsigned audio_uart_lv_child_count_44ddea(void *o){void *s=*(void **)((char*)o+8);return s?*(unsigned short*)((char*)s+0x30):0;}
unsigned audio_uart_lv_obj_has_flag_43e0e0(void *o,unsigned f){return (*(unsigned*)((char*)o+0x24)&f)==f;}
'''
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text(SHIM);elf=Path(td)/'move.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_obj_move_children_44035e',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 total=0
 for count in (0,1,2):
  for nested in (False,True):
   for skip in (0,1):
    for dx,dy in ((0,0),(3,-4)):
     outs=[]
     for is_c in (False,True):
      u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
      u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
      for a,d in segs:u.mem_write(a,d)
      root=0x20003000;child=0x20003100;second=0x20003200;grand=0x20003300
      def obj(addr,kids,flag=0):
       u.mem_write(addr,b'\0'*0x40)
       u.mem_write(addr+0x14,struct.pack('<iiii',10,20,30,40))
       u.mem_write(addr+0x24,struct.pack('<I',flag))
       if kids:
        spec=addr+0x1000;arr=addr+0x2000
        u.mem_write(addr+8,struct.pack('<I',spec))
        u.mem_write(spec,struct.pack('<I',arr))
        u.mem_write(spec+0x30,struct.pack('<H',len(kids)))
        u.mem_write(arr,struct.pack('<'+'I'*len(kids),*kids))
      obj(root,[child,second][:count]);obj(child,[grand] if nested else []);obj(second,[],0x40000);obj(grand,[])
      u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
      for reg,val in ((UC_ARM_REG_R0,root),(UC_ARM_REG_R1,dx&0xffffffff),(UC_ARM_REG_R2,dy&0xffffffff),(UC_ARM_REG_R3,skip)):
       u.reg_write(reg,val)
      u.emu_start((syms['audio_uart_lv_obj_move_children_44035e'] if is_c else 0x44035e)|1,0x600000,count=500)
      outs.append(tuple(u.mem_read(a+0x14,16) for a in (root,child,second,grand)))
     assert outs[0]==outs[1],(count,nested,skip,dx,dy,outs)
     total+=1
 print(f'PASS {total} compiled-C/native recursive LV child movement cases')
