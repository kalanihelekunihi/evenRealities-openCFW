"""Actual compiled-C/native 0x480c7c status, revision and ambient R2 cases."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_identifier_caps.c'
SHIM='''#include <stdint.h>
uint32_t audio_ble_hci_radio_read_word_4d3f3c(uint8_t a,uint32_t b,uint32_t c,uint32_t *d)
{(void)a;(void)b;(void)c;(void)d;return 0;}'''
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_radio_identifier_caps_480c7c',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    for status in (0,1,6):
        for revision in (0,0x21,0x22,0x23,0x24,0x33):
            for value in (0,1,254,255,256):
                traces=[]
                for is_c in (False,True):
                    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
                    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
                    u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
                    u.mem_map(0x40020000,0x10000);u.mem_write(0x4002000c,struct.pack('<I',revision))
                    for a,d in segs:u.mem_write(a,d)
                    out=0x20001000;u.mem_write(out,b'\xa5'*64)
                    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
                    u.reg_write(UC_ARM_REG_R0,out);u.reg_write(UC_ARM_REG_R2,out)
                    read=(syms['audio_ble_hci_radio_read_word_4d3f3c']&~1) if is_c else 0x4d3f3c
                    calls=[]
                    def hook(uc,a,size,_):
                        if a!=read:return
                        calls.append((uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)))
                        uc.mem_write(uc.reg_read(UC_ARM_REG_R3),struct.pack('<I',value))
                        uc.reg_write(UC_ARM_REG_R0,status)
                        uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
                    u.hook_add(UC_HOOK_CODE,hook)
                    start=syms['audio_ble_hci_radio_identifier_caps_480c7c'] if is_c else 0x480c7c
                    u.emu_start(start|1,0x600000,count=500)
                    traces.append((bytes(u.mem_read(out+12,4)),calls))
                assert traces[0]==traces[1],(status,hex(revision),value,traces)
    print('PASS 90 compiled-C/native identifier capability cases')
