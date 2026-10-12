"""Compare actual compiled theme slot writes with the authenticated native children."""
from pathlib import Path
import struct, subprocess, tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_SP, UC_ARM_REG_LR

ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_lv_theme_init_children.c'
SHIM='''#include <stdint.h>
uint8_t audio_uart_display_lv_root[0x200];
void audio_uart_lv_theme_default_apply_48bae4(void){}
void audio_uart_lv_theme_basic_apply_48ca3c(void){}
'''
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_theme_default_48ba64',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    for native,entry,slot,cb in ((0x48ba64,'audio_uart_lv_theme_default_48ba64',8,'audio_uart_lv_theme_default_apply_48bae4'),
                                 (0x48ca26,'audio_uart_lv_theme_basic_48ca26',16,'audio_uart_lv_theme_basic_apply_48ca3c')):
        for fill in (0,0x5a):
            for is_c in (False,True):
                u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
                u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
                u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
                for a,d in segs:u.mem_write(a,d)
                root=syms['audio_uart_display_lv_root'] if is_c else 0x2006f548
                u.mem_write(root+0x5c,struct.pack('<I',0x20004000))
                u.mem_write(0x20004000,bytes([fill])*32)
                u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
                u.emu_start((syms[entry] if is_c else native)|1,0x600000,count=20)
                image=bytearray(u.mem_read(0x20004000,32))
                expected=((syms[cb]|1) if is_c else (0x48bae5 if slot==8 else 0x48ca3d))
                assert struct.unpack_from('<I',image,slot)[0]==expected,(entry,is_c,image.hex())
                struct.pack_into('<I',image,slot,0x12345679)
                if not is_c:native_image=bytes(image)
                else:assert bytes(image)==native_image,(entry,fill,image.hex(),native_image.hex())
    print('PASS 4 compiled-C/native LV theme child state cases')
