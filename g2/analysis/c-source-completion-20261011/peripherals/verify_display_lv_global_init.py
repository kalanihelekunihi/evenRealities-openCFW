"""Actual compiled ARM C/native LV global initializer bytes and zero extent."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_lv_global_init.c'
SHIM='''#include <stdint.h>
#include <stddef.h>
uint8_t audio_uart_display_lv_root[0x200];
void *memset(void*p,int v,size_t n){(void)v;(void)n;return p;}
void audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,...)
{(void)a;(void)b;(void)c;(void)d;}'''
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_init_global_4734cc',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    traces=[]
    for is_c in (False,True):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
        for a,d in segs:u.mem_write(a,d)
        root=syms['audio_uart_display_lv_root'] if is_c else 0x2006f548
        u.mem_write(root,b'\xa5'*0x200)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        u.reg_write(UC_ARM_REG_R0,root)
        zero=(syms['memset']&~1) if is_c else 0x4734c0
        calls=[]
        def hook(uc,a,size,_):
            if a!=zero:return
            dest=uc.reg_read(UC_ARM_REG_R0)
            length=uc.reg_read(UC_ARM_REG_R2) if is_c else uc.reg_read(UC_ARM_REG_R1)
            calls.append((dest==root,length));uc.mem_write(dest,b'\x00'*length)
            uc.reg_write(UC_ARM_REG_R0,dest);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        start=syms['audio_uart_lv_init_global_4734cc'] if is_c else 0x4734cc
        u.emu_start(start|1,0x600000,count=180)
        traces.append((calls,bytes(u.mem_read(root,0x200))))
    assert traces[0]==traces[1],(traces[0][0],traces[1][0])
    print('PASS compiled-C/native LV global init 0x200-byte state comparison')
