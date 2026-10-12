"""Actual compiled ARM C/native shared connection-state callback."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_connected_state.c'
SHIM='''#include <stdint.h>
uint8_t *audio_ble_profile_connection_context;
void audio_ble_slave_security_state(uint8_t a){(void)a;}'''
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_display_connected',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    for value in (0,1,2,255):
        traces=[]
        for is_c in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            for a,d in segs:u.mem_write(a,d)
            pointer=syms['audio_ble_profile_connection_context'] if is_c else 0x2007432c
            u.mem_write(pointer,struct.pack('<I',0x20002000));u.mem_write(0x20002054,bytes([value]))
            u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
            lower=(syms['audio_ble_slave_security_state']&~1) if is_c else 0x4b82e8
            calls=[]
            def hook(uc,a,size,_):
                if a!=lower:return
                calls.append(uc.reg_read(UC_ARM_REG_R0));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            u.emu_start((syms['audio_uart_display_connected'] if is_c else 0x46f32c)|1,0x600000,count=40)
            traces.append(calls)
        assert traces[0]==traces[1],(value,traces)
    print('PASS 4 compiled-C/native shared connection-state cases')
