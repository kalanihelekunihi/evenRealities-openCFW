"""Actual compiled ARM C/native LV mutex and timer startup children."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_lv_init_mutex_children.c'
SHIM='''#include <stdint.h>
uint8_t audio_uart_display_lv_root[0x200];
void audio_uart_lv_mutex_ensure(uint32_t*a){(void)a;}
void audio_uart_lv_anim_mutex_ensure_4d47fa(uint32_t*a){(void)a;}
void audio_uart_lv_timer_update_464696(void){}'''
FUNCS={'async':(0x4d465c,'audio_uart_lv_async_init_4d465c'),
       'anim':(0x4d46de,'audio_uart_lv_anim_init_4d46de'),
       'display':(0x4645d8,'audio_uart_lv_display_init_4645d8')}
LOWERS={'async':(0x4d47cc,'audio_uart_lv_mutex_ensure'),
        'anim':(0x4d47fa,'audio_uart_lv_anim_mutex_ensure_4d47fa'),
        'display':(0x464696,'audio_uart_lv_timer_update_464696')}
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_async_init_4d465c',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    for group,(native,csym) in FUNCS.items():
        for value in ((0,1,257) if group=='display' else (0,)):
            traces=[]
            for is_c in (False,True):
                u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
                u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
                u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
                for a,d in segs:u.mem_write(a,d)
                root=syms['audio_uart_display_lv_root'] if is_c else 0x2006f548
                u.mem_write(root,b'\xa5'*0x200)
                u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
                u.reg_write(UC_ARM_REG_R0,value if group=='display' else 0x20002000)
                mapping={((syms[sym]&~1) if is_c else a):n for n,(a,sym) in LOWERS.items()}
                calls=[]
                def hook(uc,a,size,_):
                    if a not in mapping:return
                    n=mapping[a];calls.append((n,uc.reg_read(UC_ARM_REG_R0) if n!='display' else None))
                    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
                u.hook_add(UC_HOOK_CODE,hook)
                u.emu_start((syms[csym] if is_c else native)|1,0x600000,count=80)
                traces.append((calls,bytes(u.mem_read(root+0x80,1)),
                               u.reg_read(UC_ARM_REG_R0) if group!='display' else None))
            assert traces[0]==traces[1],(group,value,traces)
    print('PASS 5 compiled-C/native LV mutex/timer init cases')
