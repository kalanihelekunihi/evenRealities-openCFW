"""Actual compiled ARM C/native 0x4d3f3c dispatch and forwarded ABI."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_read_word.c'
SHIM='''#include <stdint.h>
uint32_t audio_ble_hci_radio_read_region_4d3dda(uint8_t a,uint32_t b,uint32_t c,uint32_t*d)
{(void)a;(void)b;(void)c;(void)d;return 9;}'''
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_radio_read_word_4d3f3c',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    for region in range(256):
        traces=[]
        for is_c in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            for a,d in segs:u.mem_write(a,d)
            u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
            for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),
                           (region,0x244,1,0x20001000)):u.reg_write(r,v)
            child=(syms['audio_ble_hci_radio_read_region_4d3dda']&~1) if is_c else 0x4d3dda
            calls=[]
            def hook(uc,a,size,_):
                if a!=child:return
                calls.append(tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)))
                uc.reg_write(UC_ARM_REG_R0,9)
                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            start=syms['audio_ble_hci_radio_read_word_4d3f3c'] if is_c else 0x4d3f3c
            u.emu_start(start|1,0x600000,count=100)
            traces.append((u.reg_read(UC_ARM_REG_R0),calls))
        assert traces[0]==traces[1],(region,traces)
    print('PASS 256 compiled-C/native read-selector branches and forwarded registers')
