#!/usr/bin/env python3
"""Compare actual ARM C and stock RTC snapshot for bounded input states."""
from pathlib import Path
import subprocess, tempfile, struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn.arm_const import *

R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ring_rtc_snapshot.c'
with tempfile.TemporaryDirectory() as td:
    t=Path(td);stub=t/'stub.c';stub.write_text('#include <stdint.h>\nvolatile uint32_t audio_uart_ring_rtc_shadow_200742ac;\n')
    elf=t/'c.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_ring_rtc_snapshot_4d3554',str(S),str(stub),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        e=ELFFile(f);segments=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sym={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
    for cache,hardware,out_address in ((0,0x1234,0x20070000),(0x1555,0x1234,0x20070000),(0,0,0x20070000),(0,0x1234,0)):
        pair=[]
        for compiled in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000)
            u.mem_map(0x20000000,0x100000);u.mem_map(0x40008000,0x1000)
            for a,data in segments:u.mem_write(a,data)
            shadow=sym['audio_uart_ring_rtc_shadow_200742ac'] if compiled else 0x200742ac
            u.mem_write(shadow,struct.pack('<I',cache));u.mem_write(0x4000885c,struct.pack('<I',hardware))
            if out_address:u.mem_write(out_address,b'\xaa'*16)
            u.reg_write(UC_ARM_REG_R0,out_address);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
            u.emu_start((sym['audio_uart_ring_rtc_snapshot_4d3554'] if compiled else 0x4d3554)|1,0x600000,count=2000)
            pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(shadow,4)),bytes(u.mem_read(out_address,16)) if out_address else None))
        assert pair[0]==pair[1],(cache,hardware,out_address,pair)
print('PASS_RING_RTC_SNAPSHOT_NATIVE 4')
