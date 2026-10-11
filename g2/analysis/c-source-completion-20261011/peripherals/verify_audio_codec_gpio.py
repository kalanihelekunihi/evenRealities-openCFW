#!/usr/bin/env python3
"""Stock/C oracle for the GX8002 GPIO selector and exact IRQ-save lower."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as A

R = Path(__file__).resolve().parents[4]
D = Path(__file__).resolve().parent
S = R / 'g2/components/audio/codec_gpio_selector_candidate/gpio.c'
O = D / 'codec-gpio-m4.o'
H = R / 'g2/components/audio/codec_gpio_selector_candidate/hal.c'
HO = D / 'codec-hal-m4.o'
E = D / 'codec-gpio-oracle.elf'
subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                '-O2', '-Wall', '-Wextra', '-Werror', '-c', str(S), '-o', str(O)], check=True)
subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                '-O2', '-Wall', '-Wextra', '-Werror', '-c', str(H), '-o', str(HO)], check=True)
subprocess.run(['arm-none-eabi-ld', '-Ttext=0x100000',
                '--defsym=g2_codec_shared_enable_mask=0x2007436c',
                '-o', str(E), str(O), str(HO)], check=True, stderr=subprocess.DEVNULL)
with E.open('rb') as fh:
    elf = ELFFile(fh)
    segments = [(s['p_vaddr'], s.data()) for s in elf.iter_segments() if s['p_type'] == 'PT_LOAD']
    symbols = {s.name: s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
stock = (R / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]

def word(u, addr):
    return int.from_bytes(u.mem_read(addr, 4), 'little')

def putword(u, addr, value):
    u.mem_write(addr, (value & 0xffffffff).to_bytes(4, 'little'))

def machine(original):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000, (len(stock) + 4095) & ~4095)
    u.mem_map(0x100000, 0x20000)
    u.mem_map(0x20000000, 0x100000)
    u.mem_map(0x40010000, 0x1000)
    if original:
        u.mem_write(0x438000, stock)
    else:
        for addr, data in segments:
            u.mem_write(addr, data)
    return u

def invoke(original, channel, value, mask, irq):
    u = machine(original)
    putword(u, 0x2007436c, mask)
    u.reg_write(A.UC_ARM_REG_R0, channel)
    u.reg_write(A.UC_ARM_REG_R1, value)
    u.reg_write(A.UC_ARM_REG_R2, 0x12345678)
    u.reg_write(A.UC_ARM_REG_R3, 0x76543210)
    u.reg_write(A.UC_ARM_REG_SP, 0x200f0000)
    u.reg_write(A.UC_ARM_REG_LR, 0x101181)
    u.reg_write(A.UC_ARM_REG_PRIMASK, irq)
    events = []
    done = [False]
    pin = 0x53a5be if original else symbols['g2_codec_pin_write'] & ~1

    def hook(cpu, pc, _size, _user):
        if pc == 0x101180:
            done[0] = True
            cpu.emu_stop()
            return
        if pc == pin:
            events.append((cpu.reg_read(A.UC_ARM_REG_R0),
                           cpu.reg_read(A.UC_ARM_REG_R1),
                           cpu.reg_read(A.UC_ARM_REG_PRIMASK)))
            cpu.reg_write(A.UC_ARM_REG_R0, 0)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

    u.hook_add(UC_HOOK_CODE, hook)
    u.emu_start((0x509024 if original else symbols['g2_codec_gpio_write']) | 1,
                0, count=400)
    assert done[0], (original, channel, value, mask, irq)
    return (u.reg_read(A.UC_ARM_REG_R0), word(u, 0x2007436c),
            u.reg_read(A.UC_ARM_REG_PRIMASK), events)

cases = 0
for channel in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0x106):
    for value in (0, 1, 2, 0x100, 0x101):
        for mask in (0, 0x100):
            for irq in (0, 1):
                a = invoke(True, channel, value, mask, irq)
                b = invoke(False, channel, value, mask, irq)
                assert a == b, (channel, value, mask, irq, a, b)
                cases += 1
print('PASS_AUDIO_CODEC_GPIO', cases)

# Also compare the standalone MRS/CPSID lower's result and interrupt state.
for irq in (0, 1):
    a = machine(True)
    b = machine(False)
    for u, entry in ((a, 0x473940), (b, symbols['g2_gpio_critical_save'])):
        u.reg_write(A.UC_ARM_REG_PRIMASK, irq)
        u.reg_write(A.UC_ARM_REG_SP, 0x200f0000)
        u.reg_write(A.UC_ARM_REG_LR, 0x101181)
        u.hook_add(UC_HOOK_CODE, lambda cpu, pc, size, user:
                   cpu.emu_stop() if pc == 0x101180 else None)
        u.emu_start(entry | 1, 0, count=20)
    assert (a.reg_read(A.UC_ARM_REG_R0), a.reg_read(A.UC_ARM_REG_PRIMASK)) == (
        b.reg_read(A.UC_ARM_REG_R0), b.reg_read(A.UC_ARM_REG_PRIMASK)) == (irq, 1)
print('PASS_AUDIO_GPIO_CRITICAL', 2)

cases = 0
for pin in (6, 0x81, 0x92):
    for value in (0, 1, 2, 0x100, 0x101):
        for result in (0, 1, 0xffffffff):
            outcomes = []
            for original in (True, False):
                u = machine(original)
                u.reg_write(A.UC_ARM_REG_R0, pin)
                u.reg_write(A.UC_ARM_REG_R1, value)
                u.reg_write(A.UC_ARM_REG_SP, 0x200f0000)
                u.reg_write(A.UC_ARM_REG_LR, 0x101181)
                events = []
                done = [False]
                lower = 0x480fd6 if original else symbols['g2_gpio_hal_write'] & ~1
                def hook(cpu, pc, _size, _user):
                    if pc == 0x101180:
                        done[0] = True
                        cpu.emu_stop()
                    elif pc == lower:
                        events.append((cpu.reg_read(A.UC_ARM_REG_R0),
                                       cpu.reg_read(A.UC_ARM_REG_R1)))
                        cpu.reg_write(A.UC_ARM_REG_R0, result)
                        cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
                u.hook_add(UC_HOOK_CODE, hook)
                entry = 0x53a5be if original else symbols['g2_codec_pin_write']
                u.emu_start(entry | 1, 0, count=80)
                assert done[0]
                outcomes.append((u.reg_read(A.UC_ARM_REG_R0), events))
            assert outcomes[0] == outcomes[1], (pin, value, result, outcomes)
            cases += 1
print('PASS_AUDIO_CODEC_PIN', cases)

cases = 0
for pin in (0, 31, 32, 63, 127, 255, 256):
    for mode in (0, 1, 2, 3, 4, 5, 6, 0x102):
        for irq in (0, 1):
            outcomes = []
            for original in (True, False):
                u = machine(original)
                u.reg_write(A.UC_ARM_REG_R0, pin)
                u.reg_write(A.UC_ARM_REG_R1, mode)
                u.reg_write(A.UC_ARM_REG_SP, 0x200f0000)
                u.reg_write(A.UC_ARM_REG_LR, 0x101181)
                u.reg_write(A.UC_ARM_REG_PRIMASK, irq)
                for addr in (0x40010420, 0x4001043c, 0x40010458,
                             0x40010474, 0x40010490, 0x400104ac):
                    for bank in range(8):
                        putword(u, addr + bank * 4, 0xa5a50000 | bank)
                writes = []
                done = [False]
                def written(cpu, _access, addr, size, value, _user):
                    if 0x40010000 <= addr < 0x40011000:
                        writes.append((addr, size, value & 0xffffffff,
                                       cpu.reg_read(A.UC_ARM_REG_PRIMASK)))
                def stop(cpu, pc, _size, _user):
                    if pc == 0x101180:
                        done[0] = True
                        cpu.emu_stop()
                u.hook_add(UC_HOOK_MEM_WRITE, written)
                u.hook_add(UC_HOOK_CODE, stop)
                entry = 0x480fd6 if original else symbols['g2_gpio_hal_write']
                u.emu_start(entry | 1, 0, count=120)
                assert done[0], (original, pin, mode, irq)
                outcomes.append((u.reg_read(A.UC_ARM_REG_R0),
                                 u.reg_read(A.UC_ARM_REG_PRIMASK), writes))
            assert outcomes[0] == outcomes[1], (pin, mode, irq, outcomes)
            cases += 1
print('PASS_AUDIO_GPIO_HAL', cases)
