#!/usr/bin/env python3
"""Compare transform-area corners, lower calls, and bounds with Apollo."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/transform_area.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callees=[('audio_uart_lv_memzero_48949c',0x48949c),('audio_uart_lv_transform_point_4513ae',0x4513ae)]
def rd32(u,a):return int.from_bytes(u.mem_read(a,4),'little')
def wr32(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
def signed(v):return v if v<0x80000000 else v-0x100000000
with tempfile.TemporaryDirectory() as temp:
 d=Path(temp);asm=d/'stubs.s'
 asm.write_text('.syntax unified\n.thumb\n.text\n'+''.join(f'.global {n}\n.thumb_func\n{n}:\n bx lr\n' for n,_ in callees))
 image=d/'area.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),str(asm),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,w,h,rot,sx,sy):
  cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
  cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
  for address,data in segments:cpu.mem_write(address,data)
  out=0x20012000;pivot=0x20013000
  cpu.mem_write(out,bytes([0xcc])*16)
  cpu.reg_write(UC_ARM_REG_R0,out);cpu.reg_write(UC_ARM_REG_R1,w&0xffffffff)
  cpu.reg_write(UC_ARM_REG_R2,h&0xffffffff);cpu.reg_write(UC_ARM_REG_R3,rot&0xffffffff)
  sp=0x200ff000;cpu.reg_write(UC_ARM_REG_SP,sp);cpu.reg_write(UC_ARM_REG_LR,0x600001)
  for i,val in enumerate((sx,sy,pivot)):wr32(cpu,sp+i*4,val)
  targets={((syms[n] if compiled else a)&~1):n for n,a in callees};events=[]
  def hook(u,address,_size,_user):
   n=targets.get(address)
   if n is None:return
   ptr=u.reg_read(UC_ARM_REG_R0)
   if n.endswith('48949c'):
    size=u.reg_read(UC_ARM_REG_R1);events.append(('zero',size))
    u.mem_write(ptr,bytes(size))
   else:
    r=u.reg_read(UC_ARM_REG_R1);scale_x=u.reg_read(UC_ARM_REG_R2)
    scale_y=u.reg_read(UC_ARM_REG_R3);stack=u.reg_read(UC_ARM_REG_SP)
    pv=rd32(u,stack);flag=rd32(u,stack+4)
    x,y=rd32(u,ptr),rd32(u,ptr+4)
    events.append(('point',x,y,r,scale_x,scale_y,pv,flag))
    index=sum(1 for e in events if e[0]=='point')
    dx=(signed(r)//7)+(index*3)+(scale_x&7)
    dy=-(signed(r)//11)+(index*5)-(scale_y&7)
    wr32(u,ptr,x+dx);wr32(u,ptr+4,y+dy)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  cpu.hook_add(UC_HOOK_CODE,hook)
  cpu.emu_start((syms['audio_uart_ambiq_transform_area_488cda'] if compiled else 0x488cda)|1,0x600000,count=700)
  return events,bytes(cpu.mem_read(out,16))
 cases=[(w,h,rot,sx,sy) for w,h in ((0,0),(1,1),(8,13),(-3,7),(0x10001,0x20003))
        for rot,sx,sy in ((0,256,256),(0,0x10100,0x20100),(90,256,256),(-45,0x80,0x180),(13,0x10000,0xffffffff))]
 for i in range(50):cases.append((i-25,47-i,(i*17)-400,(i*0x1234)&0xffffffff,(i*0x2345)&0xffffffff))
 for case in cases:
  native=run(False,*case);compiled=run(True,*case)
  assert native==compiled,(case,native,compiled)
 print('PASS_AMBIQ_TRANSFORM_AREA_NATIVE',len(cases))
