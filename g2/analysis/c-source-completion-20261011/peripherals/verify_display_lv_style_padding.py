"""Bounded ARM C/native space-getter proof with the shared style child cut."""
from pathlib import Path
import subprocess,tempfile,json,hashlib
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_lv_style_padding.c'
FUN=[('left',0x43efc6,18,4),('right',0x43eff4,19,8),('top',0x43f022,16,2),('bottom',0x43f050,17,1)]
with tempfile.TemporaryDirectory() as td:
 td=Path(td);shim=td/'shim.c';shim.write_text('unsigned audio_uart_lv_style_property_44bdea(void*a,unsigned b,unsigned c){(void)a;(void)b;(void)c;return 0;}')
 elf=td/'space.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_style_pad_left_43efc6',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as fp:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(fp).iter_segments() if s['p_type']=='PT_LOAD']
 count=0
 for label,addr,prop,edge in FUN:
  for sides in list(range(16))+[0x100,0x1ff,0xffffffff]:
   for padding,border in [(0,0),(4,7),(0xfffffff0,32),(0x7fffffff,1),(0x80000000,0xffffffff)]:
    outputs=[]
    for isc in [False,True]:
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
     for a,d in segs:u.mem_write(a,d)
     cut=(syms['audio_uart_lv_style_property_44bdea'] if isc else 0x44bdea)&~1;calls=[]
     def hook(uc,address,size,user):
      if address!=cut:return
      args=tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2));calls.append(args);v={prop:padding,48:border,52:sides}[args[2]];uc.reg_write(UC_ARM_REG_R0,v);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
     for reg,v in [(UC_ARM_REG_R0,0x20003000),(UC_ARM_REG_R1,0x1234),(UC_ARM_REG_R2,0xabcd),(UC_ARM_REG_R3,0xdcba)]:u.reg_write(reg,v)
     name='audio_uart_lv_style_pad_'+label+'_'+format(addr,'x');u.emu_start((syms[name] if isc else addr)|1,0x600000,count=1000);outputs.append((u.reg_read(UC_ARM_REG_R0),calls))
    assert outputs[0]==outputs[1],(label,sides,padding,border,outputs)
    assert outputs[0][1]==[(0x20003000,0x1234,p) for p in (prop,48,52)]
    assert outputs[0][0]==((padding+(border if sides&edge else 0))&0xffffffff);count+=1
 r={'status':'PASS_BOUNDED_COMPILED_ARM_NATIVE','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'limits':['Shared style property provider is a synthetic child-call cut.','No physical hardware execution or complete Main image proof.']}
 (Path(__file__).parent/'root-padding-getters/receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
