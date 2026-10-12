"""Bounded ARM C/native space-getter proof with the shared style child cut."""
from pathlib import Path
import subprocess,tempfile,json,hashlib
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_lv_theme_basic_children.c'
with tempfile.TemporaryDirectory() as td:
 td=Path(td);shim=td/'shim.c';shim.write_text('unsigned audio_uart_buffer_zero(void*a,unsigned b,unsigned c){(void)a;(void)b;(void)c;return 0;}')
 elf=td/'space.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_basic_box_clear_454746',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as fp:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(fp).iter_segments() if s['p_type']=='PT_LOAD']
 count=0
 for fill in range(256):
  for high in [0,0x100,0x87650000]:
   for length in [0,1,12,32,4096]:
    outputs=[]
    for isc in [False,True]:
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
     for a,d in segs:u.mem_write(a,d)
     cut=(syms['audio_uart_buffer_zero'] if isc else 0x43c0e4)&~1;calls=[]
     def hook(uc,address,size,user):
      if address!=cut:return
      args=tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2));calls.append(args);uc.reg_write(UC_ARM_REG_R0,0xabcddcba);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
     for reg,v in [(UC_ARM_REG_R0,0x20003000),(UC_ARM_REG_R1,fill|high),(UC_ARM_REG_R2,length),(UC_ARM_REG_R3,0xdeadbeef)]:u.reg_write(reg,v)
     u.emu_start((syms['audio_uart_lv_basic_box_clear_454746'] if isc else 0x454746)|1,0x600000,count=1000);outputs.append((u.reg_read(UC_ARM_REG_R0),calls,u.reg_read(UC_ARM_REG_SP)))
    assert outputs[0]==outputs[1],(fill,high,length,outputs)
    assert outputs[0][1]==[(0x20003000,length,fill)];count+=1
 r={'status':'PASS_BOUNDED_COMPILED_ARM_NATIVE_WRAPPER','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'limits':['Buffer child is cut to verify argument order, low-byte truncation, incidental R0 propagation and restored SP.','Buffer child runtime and complete Main image remain separate gates.']}
 (Path(__file__).parent/'root-main-init-round55/box-clear-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
