#!/usr/bin/env python3
"""Bounded native/source ambient return ABI for UART RX drain adapter."""
from pathlib import Path
import hashlib
import subprocess
import tempfile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as a

root=Path(__file__).resolve().parents[4]
stock=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(stock).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
with tempfile.TemporaryDirectory() as directory:
    work=Path(directory)
    source=root/'g2/components/bootloader/initializer_callbacks/uart_rx_drain32_abi.S'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-c',str(source),'-o',str(work/'drain.o')],check=True)
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x10000','-e','opencfw_boot_uart_rx_drain32_abi','--defsym=opencfw_boot_uart_rx_fifo=0x11001',str(work/'drain.o'),'-o',str(work/'drain.elf')],check=True,stderr=subprocess.DEVNULL)
    subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(work/'drain.elf'),str(work/'drain.bin')],check=True)
    code=(work/'drain.bin').read_bytes()
    def run(original,child_status):
        cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        cpu.mem_map(0x10000,0x2000);cpu.mem_map(0x410000,0x25000);cpu.mem_map(0x20000000,0x4000)
        cpu.mem_write(0x10000,code);cpu.mem_write(0x410000,stock)
        cpu.reg_write(a.UC_ARM_REG_SP,0x20003000);cpu.reg_write(a.UC_ARM_REG_LR,0x20002001)
        cpu.reg_write(a.UC_ARM_REG_R0,0x20000100);cpu.reg_write(a.UC_ARM_REG_R7,0xdead1234)
        events=[];done=[]
        def hook(machine,pc,size,unused):
            if pc==(0x4232c8 if original else 0x11000):
                events.append(tuple(machine.reg_read(r) for r in (a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3)))
                machine.reg_write(a.UC_ARM_REG_R0,child_status)
                machine.reg_write(a.UC_ARM_REG_PC,machine.reg_read(a.UC_ARM_REG_LR))
            elif pc==0x20002000:done.append(True);machine.emu_stop()
        cpu.hook_add(UC_HOOK_CODE,hook)
        cpu.emu_start((0x423342 if original else 0x10000)|1,0x20002002,count=100)
        assert done
        return events,cpu.reg_read(a.UC_ARM_REG_R0),cpu.reg_read(a.UC_ARM_REG_R1),cpu.reg_read(a.UC_ARM_REG_SP)
    for status in (0,4,0x8000000,0xffffffff):
        native=run(True,status);selected=run(False,status)
        assert native==selected,(status,native,selected)
        assert native[0]==[(0x20000100,0,32,0)]
    print('PASS native/source UART RX drain ABI four child statuses')
