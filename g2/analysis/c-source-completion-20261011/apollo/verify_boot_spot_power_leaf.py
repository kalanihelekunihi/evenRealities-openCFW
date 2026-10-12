#!/usr/bin/env python3
"""Bounded stock/source Spot power flag and R0 semantics at 0x42a19c."""
from pathlib import Path
import hashlib
import itertools
import subprocess
import tempfile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as a

root=Path(__file__).resolve().parents[4]
stock=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(stock).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
with tempfile.TemporaryDirectory() as directory:
    work=Path(directory)
    source=root/'g2/components/bootloader/initializer_callbacks/spot_internal_power_domain.c'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-c',str(source),'-o',str(work/'spot.o')],check=True)
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x10000','-e','opencfw_boot_spot_internal_power_domain',str(work/'spot.o'),'-o',str(work/'spot.elf')],check=True)
    subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(work/'spot.elf'),str(work/'spot.bin')],check=True)
    code=(work/'spot.bin').read_bytes()
    cases=0
    for state,mode,initial in itertools.product((0,1,2,3,0x102,0xdeadbeef),(0,1,2,0x101),(0,0x55)):
        outputs=[]
        for original,entry in ((True,0x42a19c),(False,0x10000)):
            cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
            cpu.mem_map(0x10000,0x1000);cpu.mem_map(0x410000,0x25000);cpu.mem_map(0x20000000,0x30000)
            cpu.mem_write(0x10000,code);cpu.mem_write(0x410000,stock)
            cpu.mem_write(0x200271b0,bytes([initial]))
            cpu.reg_write(a.UC_ARM_REG_SP,0x2002f000);cpu.reg_write(a.UC_ARM_REG_LR,0x20002001)
            cpu.reg_write(a.UC_ARM_REG_R0,state);cpu.reg_write(a.UC_ARM_REG_R1,mode)
            done=[]
            def hook(machine,pc,size,unused):
                if pc==0x20002000:done.append(True);machine.emu_stop()
            cpu.hook_add(UC_HOOK_CODE,hook)
            cpu.emu_start(entry|1,0x20002002,count=100)
            assert done
            outputs.append((cpu.reg_read(a.UC_ARM_REG_R0),cpu.mem_read(0x200271b0,1)[0]))
        assert outputs[0]==outputs[1],(state,mode,initial,outputs)
        cases+=1
    print('PASS native/source Spot power leaf',cases,'cases')
