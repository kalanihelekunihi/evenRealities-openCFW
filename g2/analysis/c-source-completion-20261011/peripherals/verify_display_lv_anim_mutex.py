"""Actual compiled ARM C/native 0x4d47fa initialized and cold cell effects."""
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
void audio_uart_lv_timer_update_464696(void){}
void stock_enter_critical(void){}
void stock_exit_critical(void){}'''
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_anim_mutex_ensure_4d47fa',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    for initial in (0,1):
        traces=[]
        for is_c in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            for a,d in segs:u.mem_write(a,d)
            cell=0x20002000;u.mem_write(cell,struct.pack('<III',initial,77,88))
            u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
            u.reg_write(UC_ARM_REG_R0,cell)
            mapping={((syms['stock_enter_critical']&~1) if is_c else 0x4420d0):'enter',
                     ((syms['stock_exit_critical']&~1) if is_c else 0x4420e8):'exit'}
            calls=[]
            def hook(uc,a,size,_):
                if a not in mapping:return
                calls.append(mapping[a]);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            start=syms['audio_uart_lv_anim_mutex_ensure_4d47fa'] if is_c else 0x4d47fa
            u.emu_start(start|1,0x600000,count=75)
            traces.append((calls,bytes(u.mem_read(cell,12))))
        assert traces[0]==traces[1],(initial,traces)
    print('PASS 2 compiled-C/native LV animation mutex cases')
