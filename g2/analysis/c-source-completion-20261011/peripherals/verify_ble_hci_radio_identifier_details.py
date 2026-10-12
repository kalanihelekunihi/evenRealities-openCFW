"""Actual ARM compiled-C/native 0x480874 register readout and delay effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_identifier_details.c'
SHIM='''#include <stdint.h>
void audio_ble_hci_boot_delay_491102(uint32_t n){(void)n;}'''
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_radio_identifier_details_480874',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    for mode in range(16):
        traces=[]
        for is_c in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            u.mem_map(0x40020000,0x10000);u.mem_map(0xe00f0000,0x10000)
            for a,d in segs:u.mem_write(a,d)
            for i in range(6):u.mem_write(0x40020000+i*4,struct.pack('<I',0x11223344+i if i!=5 else mode))
            for i,a in enumerate((0xe00fefe0,0xe00fefe4,0xe00fefe8,0xe00fefec,
                                   0xe00feffc,0xe00feff8,0xe00feff4,0xe00feff0)):
                u.mem_write(a,struct.pack('<I',0x12345670+i*19))
            out=0x20001000;u.mem_write(out,b'\xa5'*64)
            u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
            u.reg_write(UC_ARM_REG_R0,out)
            delay=(syms['audio_ble_hci_boot_delay_491102']&~1) if is_c else 0x491102
            calls=[]
            def hook(uc,a,size,_):
                if a!=delay:return
                calls.append(uc.reg_read(UC_ARM_REG_R0))
                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            start=syms['audio_ble_hci_radio_identifier_details_480874'] if is_c else 0x480874
            u.emu_start(start|1,0x600000,count=600)
            traces.append((bytes(u.mem_read(out,64)),calls))
        assert traces[0]==traces[1],(mode,traces)
    print('PASS 16 compiled-C/native identifier detail readouts and delay sequences')
