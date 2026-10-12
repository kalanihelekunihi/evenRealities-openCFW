#!/usr/bin/env python3
"""Stock/source register oracle for native 0x414948 and 0x41b854 wrappers."""
from pathlib import Path
import hashlib
import subprocess
import tempfile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *

ROOT=Path(__file__).resolve().parents[4]
stock=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(stock).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
base=ROOT/'g2/components/bootloader'
with tempfile.TemporaryDirectory() as temp:
    t=Path(temp);objects=[]
    for name,rel in [('lfs','filesystem/native_unmount_abi_wrapper.S'),('uart','initializer_callbacks/native_uart_log_abi_wrapper.S')]:
        obj=t/f'{name}.o'
        subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-c',str(base/rel),'-o',str(obj)],check=True)
        objects.append(obj)
    cuts=t/'cuts.S';cuts.write_text('.syntax unified\n.thumb\n.text\n.global opencfw_boot_lfs_deinit_4144dc\n.thumb_func\nopencfw_boot_lfs_deinit_4144dc:\n bkpt #0\n.global opencfw_boot_uart_log_send\n.thumb_func\nopencfw_boot_uart_log_send:\n bkpt #0\n.section .note.GNU-stack,"",%progbits\n')
    cutobj=t/'cuts.o';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-c',str(cuts),'-o',str(cutobj)],check=True)
    elf=t/'wrappers.elf';raw=t/'wrappers.bin'
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x10000','-e','opencfw_boot_lfs_unmount_internal_abi',*(str(o) for o in objects),str(cutobj),'-o',str(elf)],check=True)
    subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(raw)],check=True)
    symbols={parts[2]:int(parts[0],16)&~1 for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(parts:=line.split())>=3}
    data=raw.read_bytes()
    specs=[('unmount',0x414948,'opencfw_boot_lfs_unmount_internal_abi',0x4144dc,'opencfw_boot_lfs_deinit_4144dc'),
           ('uart',0x41b854,'opencfw_boot_uart_log_send_ambient_abi',0x41f918,'opencfw_boot_uart_log_send')]
    for label,native_entry,source_entry,native_child,source_child in specs:
        observations=[]
        for original in (True,False):
            uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
            uc.mem_map(0x10000,0x1000);uc.mem_map(0x410000,0x25000);uc.mem_map(0x20000000,0x1000)
            uc.mem_write(0x10000,data);uc.mem_write(0x410000,stock)
            entry=native_entry if original else symbols[source_entry]
            child=native_child if original else symbols[source_child]
            calls=[];done=[]
            def hook(machine,pc,size,_):
                if pc==child:
                    calls.append([machine.reg_read(UC_ARM_REG_R0),machine.reg_read(UC_ARM_REG_R1),machine.reg_read(UC_ARM_REG_R2)])
                    machine.reg_write(UC_ARM_REG_R0,0x12345678)
                    machine.reg_write(UC_ARM_REG_PC,machine.reg_read(UC_ARM_REG_LR))
                elif pc==0x20000000:
                    done.append(True);machine.emu_stop()
            uc.hook_add(UC_HOOK_CODE,hook)
            uc.reg_write(UC_ARM_REG_SP,0x20000800);uc.reg_write(UC_ARM_REG_LR,0x20000001)
            uc.reg_write(UC_ARM_REG_R7,0x87654321);uc.reg_write(UC_ARM_REG_R0,0x20000100);uc.reg_write(UC_ARM_REG_R1,0x34)
            uc.emu_start(entry|1,0x20000002,count=50)
            assert done and len(calls)==1,(label,original,done,calls)
            observations.append((calls,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_SP)))
        assert observations[0]==observations[1],(label,observations)
        print('PASS',label,observations[0])
