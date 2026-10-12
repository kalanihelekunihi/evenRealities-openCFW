"""Actual compiled ARM C/native LV event initialization order and bytes."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
DIR=ROOT/'components/audio/uart_thread_source_candidate'
SHIM='''#include <stdint.h>
#include <stddef.h>
uint8_t audio_uart_display_lv_root[0x200];
void audio_uart_lv_transition_timer_callback_450758(void*a){(void)a;}
void *audio_uart_lv_timer_create_464466(void(*a)(void*),uint32_t b,void*c)
{(void)a;(void)b;(void)c;return 0;}
void audio_uart_lv_transition_schedule_4509da(void){}
void *memset(void*p,int c,size_t n){(void)c;(void)n;return p;}
void audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,...)
{(void)a;(void)b;(void)c;(void)d;}'''
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_init_event_4503a4',
                    str(DIR/'display_lv_event_init.c'),str(DIR/'display_lv_global_init.c'),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    traces=[]
    for is_c in (False,True):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
        for a,d in segs:u.mem_write(a,d)
        root=syms['audio_uart_display_lv_root'] if is_c else 0x2006f548
        callback=syms['audio_uart_lv_transition_timer_callback_450758'] if is_c else 0x450759
        u.mem_write(root,b'\xa5'*0x200)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        create=(syms['audio_uart_lv_timer_create_464466']&~1) if is_c else 0x464466
        schedule=(syms['audio_uart_lv_transition_schedule_4509da']&~1) if is_c else 0x4509da
        calls=[]
        def hook(uc,a,size,_):
            if a==create:
                calls.append(('create',(uc.reg_read(UC_ARM_REG_R0)&~1)==(callback&~1),
                              uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)))
                uc.reg_write(UC_ARM_REG_R0,0x20003000)
            elif a==schedule:calls.append(('schedule',))
            else:return
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        start=syms['audio_uart_lv_init_event_4503a4'] if is_c else 0x4503a4
        u.emu_start(start|1,0x600000,count=120)
        traces.append((calls,bytes(u.mem_read(root+0xa4,0x20))))
    assert traces[0]==traces[1],traces
    print('PASS compiled-C/native LV event initializer')
