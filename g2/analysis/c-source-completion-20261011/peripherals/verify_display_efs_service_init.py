"""Actual compiled ARM C/native EFS startup message arguments."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_efs_service_init.c'
SHIM='''#include <stdint.h>
uint32_t audio_uart_thread_msg_rx_from_ble_48f12c(uint32_t a,uint8_t*b,uint32_t c)
{(void)a;(void)b;(void)c;return 0;}'''
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_efs_service_init_458c48',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    traces=[]
    for is_c in (False,True):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
        for a,d in segs:u.mem_write(a,d)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        lower=(syms['audio_uart_thread_msg_rx_from_ble_48f12c']&~1) if is_c else 0x48f12c
        calls=[]
        def hook(uc,a,size,_):
            if a!=lower:return
            p=uc.reg_read(UC_ARM_REG_R1)
            calls.append((uc.reg_read(UC_ARM_REG_R0),bytes(uc.mem_read(p,1)),uc.reg_read(UC_ARM_REG_R2)))
            uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        start=syms['audio_uart_efs_service_init_458c48'] if is_c else 0x458c48
        u.emu_start(start|1,0x600000,count=40)
        traces.append(calls)
    assert traces[0]==traces[1]==[(0x400,b'\x00',1)],traces
    print('PASS compiled-C/native EFS startup message')
