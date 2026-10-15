#!/usr/bin/env python3
"""Native/C comparison of main MSPI service branches before lower calls."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
def set32(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c'
 stub.write_text('''typedef unsigned u32;
u32 display_driver_uled_mspi_queue_snapshot_53901a(u32 a,u32 *b){(void)a;b[0]=*(volatile u32 *)0x20001008u;b[1]=0;b[2]=0;((volatile unsigned char *)b)[14]=*(volatile unsigned char *)0x2000100cu;*(volatile u32 *)0x20001000u=1;return 0;}
u32 display_driver_uled_mspi_dma_stop_4bfd62(u32 *a){(void)a;*(volatile u32 *)0x20001000u=2;return 0;}
u32 display_driver_uled_mspi_queue_release_5390fc(u32 a){(void)a;*(volatile u32 *)0x20001000u=3;return 0;}
u32 display_driver_uled_mspi_dma_start_4bfd44(u32 *a){(void)a;*(volatile u32 *)0x20001000u=4;return 0;}
u32 display_driver_uled_mspi_dma_next_4bfdf4(u32 *a){(void)a;*(volatile u32 *)0x20001000u=5;return 0;}
u32 display_driver_uled_mspi_pin_control_4c4530(u32 a,u32 b){(void)a;(void)b;*(volatile u32 *)0x20001000u=6;return *(volatile u32 *)0x2000100cu;}
''')
 image=Path(directory)/'service.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
  '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
  '-Wl,-Ttext=0x100000',str(here/'display_driver_uled_mspi_interrupt_service.c'),
  str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 covered=set()
 for branch in ('null','invalid','idle','hp_quiet','hp_complete','hp_error',
                'hp_callback','hp_more','hp_clock','hp_clock_fail','cq_no_queue','cq_snapshot',
                'cq_complete','cq_callback','cq_error','cq_restart','cq_clock'):
  for module in (0,1,2):
   observed=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
    u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
    u.mem_map(0x40060000,0x3000)
    for base,data in segments:u.mem_write(base,data)
    handle=0x20080000
    set32(u,handle,0 if branch=='invalid' else 0x01bebebe)
    set32(u,handle+4,module)
    set32(u,handle+0x848,1)
    set32(u,handle+0x854,0x20090000)
    set32(u,handle+0x840,2 if branch=='hp_more' else 1)
    set32(u,handle+0x8c8,0 if branch in ('hp_clock','hp_clock_fail','cq_clock') else 4<<8)
    if branch in ('hp_callback','cq_callback','cq_error','cq_restart'):
     set32(u,0x20090010,0x600101)
     set32(u,0x20090014,0x200a0000)
     set32(u,handle+0x2c,0x600101)
     set32(u,handle+0x42c,0x200a0000)
    if branch.startswith('hp_'):u.mem_write(handle+0x83c,b'\x01')
    if branch.startswith('cq_'):
     set32(u,handle+0x20,2 if branch=='cq_restart' else 1)
     if branch!='cq_no_queue':
      set32(u,0x200523d8+module*0x8d0+0x828,0x20090000)
      set32(u,0x20001008,1 if branch in ('cq_complete','cq_callback','cq_clock') else 0)
      set32(u,0x2000100c,1 if branch in ('cq_error','cq_restart') else 0)
    if branch=='hp_clock_fail':set32(u,0x2000100c,3)
    status=0x80 if branch=='hp_error' else 0x40 if branch in (
        'hp_complete','hp_callback','hp_more','hp_clock','hp_clock_fail') else 0
    reg=0x40060000+module*0x1000
    set32(u,reg+0x204,0)
    if not compiled:
     def native_coverage(uc,at,size,user):
      if 0x4c240e<=at<0x4c26d6:covered.update(range(at,at+size))
     u.hook_add(UC_HOOK_CODE,native_coverage)
     for number,address in enumerate((0x53901a,0x4bfd62,0x5390fc,0x4bfd44,0x4bfdf4,0x4c4530),1):
      def lower(uc,at,size,user,n=number):
       if at==0x53901a:
        out=uc.reg_read(UC_ARM_REG_R1)
        set32(uc,out,uc.reg_read(UC_ARM_REG_R0) and int.from_bytes(uc.mem_read(0x20001008,4),'little'))
        set32(uc,out+4,0);set32(uc,out+8,0)
        uc.mem_write(out+14,bytes(uc.mem_read(0x2000100c,1)))
       set32(uc,0x20001000,n)
       uc.reg_write(UC_ARM_REG_R0,int.from_bytes(uc.mem_read(0x2000100c,4),'little') if at==0x4c4530 else 0)
       uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
      u.hook_add(UC_HOOK_CODE,lower,begin=address,end=address)
    def callback(uc,at,size,user):
     set32(uc,0x20001010,uc.reg_read(UC_ARM_REG_R0))
     set32(uc,0x20001014,uc.reg_read(UC_ARM_REG_R1))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,callback,begin=0x600100,end=0x600100)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.reg_write(UC_ARM_REG_R0,0 if branch=='null' else handle)
    u.reg_write(UC_ARM_REG_R1,status)
    start=syms['am_hal_mspi_interrupt_service'] if compiled else 0x4c240e
    u.emu_start(start|1,0x600000,count=20000)
    observed.append((u.reg_read(UC_ARM_REG_R0),
      bytes(u.mem_read(handle,0x8d0)),
      bytes(u.mem_read(reg,0x300)),
      bytes(u.mem_read(0x20001000,4)),
      bytes(u.mem_read(0x20001010,8)),
      bytes(u.mem_read(0x20090000,0x18))))
   assert observed[0]==observed[1],(branch,module,observed)
   cases+=1
 print('PASS_DISPLAY_DRIVER_ULED_MSPI_SERVICE_NATIVE',cases,
       'service_bytes_covered',len(covered),'of',0x4c26d6-0x4c240e)
 missing=sorted(set(range(0x4c240e,0x4c26d6))-covered)
 spans=[]
 for address in missing:
  if not spans or address>spans[-1][1]+1:spans.append([address,address])
  else:spans[-1][1]=address
 print('UNCOVERED_SERVICE_SPANS',[(hex(a),hex(b)) for a,b in spans])
