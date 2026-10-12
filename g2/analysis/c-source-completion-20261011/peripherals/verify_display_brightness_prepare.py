"""Actual compiled ARM C/native 0x46f50c/52c flash-power transitions."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_brightness_prepare.c'
SHIM='''#include <stdint.h>
void *audio_uart_font_flash_device;
uint8_t audio_uart_font_flash_sleep;
int32_t audio_uart_font_flash_power(void*a,uint8_t b,uint8_t c)
{(void)a;(void)b;(void)c;return 0;}'''
FUNCS={'close':(0x46f50c,'audio_uart_brightness_close_prepare_46f50c'),
       'open':(0x46f52c,'audio_uart_brightness_open_prepare_46f52c')}
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_brightness_close_prepare_46f50c',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    for name,(native,csym) in FUNCS.items():
        for asleep in (0,1,2):
            traces=[]
            for is_c in (False,True):
                u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
                u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
                u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
                for a,d in segs:u.mem_write(a,d)
                cell=syms['audio_uart_font_flash_sleep'] if is_c else 0x20074fb9
                device=syms['audio_uart_font_flash_device'] if is_c else 0x20074544
                u.mem_write(cell,bytes([asleep]));u.mem_write(device,struct.pack('<I',0x20003000))
                u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
                lower=(syms['audio_uart_font_flash_power']&~1) if is_c else 0x4c26e0
                calls=[]
                def hook(uc,a,size,_):
                    if a!=lower:return
                    calls.append(tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)))
                    uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
                u.hook_add(UC_HOOK_CODE,hook)
                u.emu_start((syms[csym] if is_c else native)|1,0x600000,count=90)
                traces.append((calls,bytes(u.mem_read(cell,1))))
            assert traces[0]==traces[1],(name,asleep,traces)
    print('PASS 6 compiled-C/native brightness flash-power transitions')
