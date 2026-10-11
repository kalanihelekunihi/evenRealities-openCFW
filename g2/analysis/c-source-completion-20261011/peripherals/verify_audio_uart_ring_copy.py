#!/usr/bin/env python3
"""Compare bounded valid ring copies with authenticated Apollo native bytes."""
from pathlib import Path
import subprocess, tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn import arm_const as A

R = Path(__file__).resolve().parents[4]
S = R/'g2/components/audio/uart_thread_source_candidate'
B = (R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    objs=[]
    for name in ('ring_copy','byte_copy'):
        o=Path(td)/(name+'.o'); objs.append(str(o))
        subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                        '-Wall','-Wextra','-Werror','-c',str(S/(name+'.c')),'-o',str(o)],check=True)
    # The fatal contract is intentionally unreachable in these valid fixtures.
    assert_src=Path(td)/'fatal.c';assert_src.write_text('void offline_assert(void) { for (;;) {} }\n')
    assert_obj=Path(td)/'fatal.o';objs.append(str(assert_obj))
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                    '-c',str(assert_src),'-o',str(assert_obj)],check=True)
    p=Path(td)/'copy.elf'
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x110000',
                    '-o',str(p),*objs],check=True)
    with p.open('rb') as f:
        e=ELFFile(f)
        segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
        syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}

    def run(native, read, cap, offset, count):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        u.mem_map(0x438000,(len(B)+4095)&~4095);u.mem_write(0x438000,B)
        u.mem_map(0x100000,0x30000);u.mem_map(0x20000000,0x100000)
        if not native:
            for addr,data in segs:u.mem_write(addr,data)
        d=0x20040000; src=0x20041000; storage=0x20042000
        u.mem_write(d+8,cap.to_bytes(4,'little'))
        u.mem_write(d+24,storage.to_bytes(4,'little'))
        u.mem_write(src,bytes((i*13+7)&255 for i in range(128)))
        u.mem_write(storage,bytes((i*17+11)&255 for i in range(128)))
        addr=(0x57e2f6 if read else 0x57e268) if native else syms['audio_uart_ring_read_copy' if read else 'audio_uart_ring_write_copy']
        for reg,val in ((A.UC_ARM_REG_R0,d),(A.UC_ARM_REG_R1,src),(A.UC_ARM_REG_R2,count),
                        (A.UC_ARM_REG_R3,offset),(A.UC_ARM_REG_SP,0x200f0000),(A.UC_ARM_REG_LR,0x101ff1)):
            u.reg_write(reg,val)
        u.emu_start(addr|1,0x101ff0,count=1000)
        return (u.reg_read(A.UC_ARM_REG_R0),u.mem_read(src,128),u.mem_read(storage,128))

    n=0
    for read in (False,True):
        for cap in (5,8,17,32):
            for offset in range(cap):
                for count in (1,2,cap-offset,cap):
                    if count>cap:continue
                    original=run(True,read,cap,offset,count)
                    candidate=run(False,read,cap,offset,count)
                    assert original==candidate,(read,cap,offset,count,original[0],candidate[0])
                    n+=1
    print('PASS_AUDIO_UART_RING_COPY',n)
