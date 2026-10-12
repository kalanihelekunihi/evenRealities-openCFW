"""Bounded actual ARM C/native content-size call order and arithmetic with child cuts."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_lv_content_size.c'
NAMES=[('audio_uart_lv_style_pad_left_43efc6',0x43efc6),('audio_uart_lv_style_pad_right_43eff4',0x43eff4),
       ('audio_uart_lv_obj_width_43fd9e',0x43fd9e),('audio_uart_lv_style_pad_top_43f022',0x43f022),
       ('audio_uart_lv_style_pad_bottom_43f050',0x43f050),('audio_uart_lv_obj_height_43fdda',0x43fdda)]
SHIM='''
void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){(void)a;(void)b;(void)c;(void)d;}
'''+''.join('int '+n+'(void *a,unsigned b,unsigned c,unsigned d){(void)a;(void)b;(void)c;(void)d;return 0;}\n' for n,_ in NAMES)
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text(SHIM);elf=Path(td)/'content.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_obj_content_width_43fe16',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 total=0
 for width in (True,False):
  entry=('audio_uart_lv_obj_content_width_43fe16',0x43fe16) if width else ('audio_uart_lv_obj_content_height_43fe70',0x43fe70)
  for vals in ((0,0,0),(4,7,120),(30,40,20)):
   outs=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
    u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in segs:u.mem_write(a,d)
    selected=[NAMES[i] for i in ((0,1,2) if width else (3,4,5))]
    cut={((syms[n] if is_c else native)&~1):i for i,(n,native) in enumerate(selected)}
    calls=[]
    def hook(uc,address,size,user):
     if address not in cut:return
     i=cut[address]
     calls.append((i,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2),uc.reg_read(UC_ARM_REG_R3)))
     uc.reg_write(UC_ARM_REG_R0,vals[i]);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    for reg,val in ((UC_ARM_REG_R0,0x20003000),(UC_ARM_REG_R1,0xabababab),(UC_ARM_REG_R2,0x12345678),(UC_ARM_REG_R3,0x87654321)):
     u.reg_write(reg,val)
    u.emu_start((syms[entry[0]] if is_c else entry[1])|1,0x600000,count=200)
    outs.append((u.reg_read(UC_ARM_REG_R0),calls))
   assert outs[0][0]==outs[1][0],(entry,vals,outs)
   assert [c[0] for c in outs[0][1]]==[c[0] for c in outs[1][1]]==[0,1,2],(entry,vals,outs)
   assert outs[0][0]==((vals[2]-vals[0]-vals[1])&0xffffffff),(entry,vals,outs)
   total+=1
 print(f'PASS {total} compiled-C/native LV content dimension cases with ordered child cuts')
