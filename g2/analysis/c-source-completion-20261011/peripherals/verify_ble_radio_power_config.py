"""Actual compiled ARM C/native 0x4c2b68 pin cells and ordered calls."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_radio_power_config.c'
SHIM='''#include <stdint.h>
uint32_t g2_codec_pin_function(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}'''
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_radio_power_config_4c2b68',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    for group in range(9):
        for setting in (0,1,2,3,255):
            traces=[]
            for is_c in (False,True):
                u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
                u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
                u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
                for a,d in segs:u.mem_write(a,d)
                for a in list(range(0x2000006c,0x20000114,4))+list(range(0x20074204,0x2007421c,4)):
                    u.mem_write(a,struct.pack('<I',a^0x87654321))
                u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
                u.reg_write(UC_ARM_REG_R0,group);u.reg_write(UC_ARM_REG_R1,setting)
                pin=(syms['g2_codec_pin_function']&~1) if is_c else 0x480f0c
                calls=[]
                def hook(uc,a,size,_):
                    if a!=pin:return
                    calls.append((uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
                    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
                u.hook_add(UC_HOOK_CODE,hook)
                start=syms['audio_ble_radio_power_config_4c2b68'] if is_c else 0x4c2b68
                u.emu_start(start|1,0x600000,count=250)
                traces.append(calls)
            assert traces[0]==traces[1],(group,setting,traces)
    print('PASS 45 compiled-C/native radio pin-function call sequences')
