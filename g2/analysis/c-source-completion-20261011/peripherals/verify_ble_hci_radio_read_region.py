"""Actual compiled ARM C/native 0x4d3dda region limits and copy arguments."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_read_region.c'
SHIM='''#include <stdint.h>
uint32_t platform_copy_words(uint32_t a,uint32_t*b,uint32_t c)
{(void)a;(void)b;(void)c;return 0;}'''
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_radio_read_region_4d3dda',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    cases=[(region,mode,ready,offset,words) for region in range(7)
           for mode in (0,8,16,24) for ready in (0,1)
           for offset,words in ((0,1),(0x3f,1),(0x1ff,1),(0x200,1),(0x243,1),(0x5ff,1))]
    for region,mode,ready,offset,words in cases:
        traces=[]
        for is_c in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            u.mem_map(0x40020000,0x10000)
            u.mem_write(0x400201bc,struct.pack('<I',mode))
            u.mem_write(0x40021008,struct.pack('<I',ready<<27))
            for a,d in segs:u.mem_write(a,d)
            u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
            for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),
                           (region,offset,words,0x20001000)):u.reg_write(r,v)
            child=(syms['platform_copy_words']&~1) if is_c else 0x48086a
            calls=[]
            def hook(uc,a,size,_):
                if a!=child:return
                calls.append(tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)))
                uc.reg_write(UC_ARM_REG_R0,0)
                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            start=syms['audio_ble_hci_radio_read_region_4d3dda'] if is_c else 0x4d3dda
            u.emu_start(start|1,0x600000,count=250)
            traces.append((u.reg_read(UC_ARM_REG_R0),calls))
        assert traces[0]==traces[1],(region,mode,ready,offset,words,traces)
    print('PASS',len(cases),'compiled-C/native radio region read decisions and copy arguments')
