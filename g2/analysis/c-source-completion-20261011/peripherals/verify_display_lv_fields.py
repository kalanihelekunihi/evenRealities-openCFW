"""Actual compiled-C/native LV display field branches, explicit/default display."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
NATIVE={'audio_uart_display_buffer_attach':0x44fbfc,'audio_uart_display_buffer_mode':0x44fc18,'audio_uart_display_flush_bind':0x44fc2e,'audio_uart_display_buffer_size':0x44fa3e,'audio_uart_display_buffer_origin':0x44fa5e}
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint8_t audio_uart_display_lv_root[64]; uint32_t calls;
void audio_uart_display_size_changed(void *p){(void)p;calls++;}
''')
    elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_display_buffer_attach',str(ROOT/'components/audio/uart_thread_source_candidate/display_lv_core_fields.c'),str(shim),'-o',str(elf)],check=True)
    syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    for name,addr in NATIVE.items():
      for explicit in [False,True]:
       out=[]
       for c in [False,True]:
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
        for a,d in segs:u.mem_write(a,d)
        u.mem_map(0x20000000,0x100000);root=syms['audio_uart_display_lv_root'] if c else 0x2006f548;d=0x20080000
        u.mem_write(d,b'\x00'*1024);u.mem_write(root+20,struct.pack('<I',d));u.mem_write(d+700,struct.pack('<I',0x20080100))
        calls=[0]
        if not c:
         def hook(uc,a,size,_):
          if a==0x440656:
           calls[0]+=1;uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
         u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        for reg,val in ((UC_ARM_REG_R0,d if explicit else 0),(UC_ARM_REG_R1,0x20080200),(UC_ARM_REG_R2,0x1357)):u.reg_write(reg,val)
        u.emu_start((syms[name] if c else addr)|1,0x600000,count=2000)
        if c:calls[0]=struct.unpack('<I',u.mem_read(syms['calls'],4))[0]
        out.append((bytes(u.mem_read(d,0x40)),calls[0]))
       assert out[0]==out[1],(name,explicit,out)
       print('PASS LV fields',name,explicit)
