#!/usr/bin/env python3
"""Controlled stock/C transaction send and cleanup comparisons, logging disabled."""
from pathlib import Path
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'g2/components/audio/transaction_send_source_candidate/send.c'
STOCK = (ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as directory:
    directory = Path(directory)
    obj, path = directory / 'send.o', directory / 'send.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-O2', '-Wall', '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    definitions = {'g2_audio_transaction_transport': 0x2007397c,
                   'audio_transaction_init': 0x101011,
                   'audio_transaction_construct': 0x101021,
                   'audio_transaction_cleanup': 0x101031,
                   'audio_transaction_exchange': 0x101041,
                   'audio_transaction_extract': 0x101051,
                   'audio_log_flags': 0x101061,
                   'audio_log_extended': 0x101071,
                   'audio_log_simple': 0x101081}
    subprocess.run(['arm-none-eabi-ld', '-Ttext=0x100000',
                    *[f'--defsym={name}=0x{value:x}' for name, value in definitions.items()],
                    '-o', str(path), str(obj)], check=True, stderr=subprocess.DEVNULL)
    with path.open('rb') as stream:
        elf = ELFFile(stream)
        segments = [(item['p_vaddr'], item.data()) for item in elf.iter_segments() if item['p_type'] == 'PT_LOAD']
        symbols = {item.name: item['st_value'] for item in elf.get_section_by_name('.symtab').iter_symbols()}

    def run(native, transaction, failed_stage, code, family, length, flags):
        unit = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        unit.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        unit.mem_map(0x438000, (len(STOCK)+4095)&~4095)
        unit.mem_map(0x100000, 0x20000)
        unit.mem_map(0x20000000, 0x100000)
        unit.mem_write(0x438000, STOCK)
        if not native:
            for address, data in segments:
                unit.mem_write(address, data)
        stack = 0x200f0000
        for offset, value in ((0, flags), (4, transaction), (8, 77)):
            unit.mem_write(stack+offset, (value&0xffffffff).to_bytes(4, 'little'))
        for reg, value in ((A.UC_ARM_REG_R0, code), (A.UC_ARM_REG_R1, family),
                           (A.UC_ARM_REG_R2, 0x20008000), (A.UC_ARM_REG_R3, length),
                           (A.UC_ARM_REG_SP, stack), (A.UC_ARM_REG_LR, 0x101181)):
            unit.reg_write(reg, value)
        targets = ({0x57ba88:'init', 0x57c0d6:'construct', 0x57baec:'cleanup',
                    0x57c442:'exchange', 0x57bd06:'extract', 0x43d0ce:'flags'} if native else
                   {0x101010:'init', 0x101020:'construct', 0x101030:'cleanup',
                    0x101040:'exchange', 0x101050:'extract', 0x101060:'flags'})
        calls = []
        done = [False]
        def hook(machine, pc, _size, _user):
            if pc == 0x101180:
                done[0] = True
                machine.emu_stop()
                return
            kind = targets.get(pc)
            if kind is None:
                return
            r = tuple(machine.reg_read(getattr(A, f'UC_ARM_REG_R{i}')) for i in range(4))
            sp = machine.reg_read(A.UC_ARM_REG_SP)
            if kind == 'construct':
                fifth = int.from_bytes(machine.mem_read(sp,4),'little')
                calls.append((kind, *r, fifth))
            elif kind == 'exchange':
                calls.append((kind, r[0], r[1], r[3]))
                machine.mem_write(r[2], (0x1234).to_bytes(2,'little'))
            elif kind == 'extract':
                calls.append((kind, r[0], r[1], r[2]))
                if r[2]:
                    machine.mem_write(r[2]+4, bytes((0x34,0x12,0,0x56)))
            else:
                calls.append((kind,))
            result = (7 if kind == failed_stage else 0)
            machine.reg_write(A.UC_ARM_REG_R0, result)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))
        unit.hook_add(UC_HOOK_CODE, hook)
        unit.emu_start((0x57c512 if native else symbols['audio_send_transaction'])|1,0,count=450)
        assert done[0], (native, transaction, failed_stage)
        return unit.reg_read(A.UC_ARM_REG_R0), calls

    total=0
    for transaction in (0,0x20007000):
        for stage in ('none','construct','exchange','extract'):
            for code,family,length,flags in ((12,0x100,0,0),(0x12345,0x23456,0x33333,0x101)):
                original=run(True,transaction,stage,code,family,length,flags)
                candidate=run(False,transaction,stage,code,family,length,flags)
                assert original==candidate,(transaction,stage,code,original,candidate)
                total+=1
    print('PASS_AUDIO_TRANSACTION_SEND',total)
