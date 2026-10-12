"""Actual compiled ARM C/native 0x473548 ordered startup and idempotent branch."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_lv_init.c'
CHILDREN=[('global',0x4734cc),('memory',0x48aa60),('timer',0x4c6d04),
 ('async',0x49acb0),('display',0x464330),('indev',0x4c6d8c),
 ('theme',0x4546dc),('event',0x4503a4),('style',0x44d32c),
 ('draw_unit',0x4b1b98),('anim',0x48438c),('group',0x4c73d6),
 ('cache',0x44b90c),('font',0x488f4c),('fs',0x4c794c),
 ('misc',0x4c8f0a),('bind',0x4c8efc),('assert',0x4c91a8)]
NAMES={n:'audio_uart_lv_init_'+n+'_'+hex(a)[2:] for n,a in CHILDREN}
NAMES['bind']='audio_uart_lv_init_global_bind_4c8efc'
SHIM='''#include <stdint.h>
uint8_t audio_uart_display_lv_root[0x200];
uint8_t audio_file_lfs_context[4];
void audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,...)
{(void)a;(void)b;(void)c;(void)d;}\n'''
for n,_ in CHILDREN:SHIM+='void '+NAMES[n]+'(){}\n'
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_display_clock_prepare',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    for initialized in (0,1):
        traces=[]
        for is_c in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            for a,d in segs:u.mem_write(a,d)
            flag=syms['audio_uart_display_lv_root'] if is_c else 0x2006f548
            global_ptr=syms['audio_file_lfs_context'] if is_c else 0x20071ac8
            u.mem_write(flag,bytes([initialized]))
            u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
            mapping={((syms[NAMES[n]]&~1) if is_c else a):n for n,a in CHILDREN}
            mapping[(syms['audio_uart_lvgl_log']&~1) if is_c else 0x44d25c]='log'
            calls=[]
            def hook(uc,a,size,_):
                if a not in mapping:return
                n=mapping[a]
                if n=='log':calls.append((n,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R2)))
                elif n=='draw_unit':calls.append((n,uc.reg_read(UC_ARM_REG_R0)))
                elif n=='font':calls.append((n,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
                elif n in ('global','bind'):
                    expected=flag if n=='global' else global_ptr
                    calls.append((n,uc.reg_read(UC_ARM_REG_R0)==expected))
                else:calls.append((n,))
                uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            start=syms['audio_uart_display_clock_prepare'] if is_c else 0x473548
            u.emu_start(start|1,0x600000,count=240)
            traces.append((calls,bytes(u.mem_read(flag,1))))
        assert traces[0]==traces[1],(initialized,traces)
    print('PASS 2 compiled-C/native LV startup call-chain cases')
