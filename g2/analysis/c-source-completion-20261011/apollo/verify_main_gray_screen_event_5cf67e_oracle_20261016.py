#!/usr/bin/env python3
"""Compare stock/C gray screen call sequence and state writes."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/gray_screen_event_5cf67e.c'
IMAGE = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
IMAGE_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
BODY_START, BODY_END = 0x5cf67e, 0x5cf788
BODY_SHA = '98a6172b4fd466267ec70b0d9b1373c16d93c27f5a6940f3a172b90f7406f24c'
STEPS = bytes((1, 2, 4, 8, 8, 4, 2, 1))
OUT = G2 / 'build/c-firmware/20261016/main-gray-screen-event-5cf67e'
CALLS = {
    'audio_uart_page_43de82': (0x43de82, 1),
    'audio_uart_page_43dfa4': (0x43dfa4, 2),
    'audio_uart_page_43f506': (0x43f506, 2),
    'audio_uart_page_43f568': (0x43f568, 2),
    'audio_uart_page_43f4c0': (0x43f4c0, 3),
    'audio_uart_page_43f09a': (0x43f09a, 3),
    'audio_uart_page_44104c': (0x44104c, 1),
    'audio_uart_page_44127e': (0x44127e, 3),
    'audio_uart_page_44129e': (0x44129e, 3),
    'audio_uart_page_4412ec': (0x4412ec, 3),
    'audio_uart_page_44131c': (0x44131c, 3),
    'audio_uart_page_44146a': (0x44146a, 3),
    'audio_uart_page_441068': (0x441068, 3),
}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def u32(value): return (value & 0xffffffff).to_bytes(4, 'little')

def main():
    if IMAGE[0x78df8c - 0x438000:0x78df94 - 0x438000] != STEPS or \
            hashlib.sha256(IMAGE).hexdigest() != IMAGE_SHA or hashlib.sha256(
            IMAGE[BODY_START - 0x438000:BODY_END - 0x438000]).hexdigest() != BODY_SHA:
        raise RuntimeError('stock payload or body changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        shim = Path(tmp) / 'shim.c'
        shim.write_text('#include <stdint.h>\nuint32_t audio_uart_registry_context_20003080[2];\n' +
                        '\n'.join(f'__attribute__((naked)) uint32_t {name}(void)'
                                  '{__asm volatile("bx lr");}' for name in CALLS))
        elf = Path(tmp) / 'candidate.elf'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                        '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-w',
                        '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_uart_registry_callback_5cf67e',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as fh:
            parsed = ELFFile(fh)
            segments = [(s['p_vaddr'], s.data()) for s in parsed.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       parsed.get_section_by_name('.symtab').iter_symbols()}

        def run(compiled, event, parent):
            uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            uc.mem_map(0x400000, 0x400000); uc.mem_write(0x438000, IMAGE)
            uc.mem_map(0x100000, 0x200000)
            for address, data in segments: uc.mem_write(address, data)
            uc.mem_map(0x20000000, 0x100000)
            root_cell = symbols['audio_uart_gray_screen_root_20074880'] if compiled else 0x20074880
            context = symbols['audio_uart_registry_context_20003080'] if compiled else 0x20003080
            uc.mem_write(root_cell, u32(0xaaaaaaaa)); uc.mem_write(context + 4, u32(0xbbbbbbbb))
            for register, value in ((A.UC_ARM_REG_R0, event), (A.UC_ARM_REG_R1, 0x12345678),
                                    (A.UC_ARM_REG_R2, parent ^ 0x12345678), (A.UC_ARM_REG_R3, parent),
                                    (A.UC_ARM_REG_SP, 0x200ff000), (A.UC_ARM_REG_LR, 0x600001)):
                uc.reg_write(register, value)
            hooks = {(symbols[name] & ~1 if compiled else address): (name, arity)
                     for name, (address, arity) in CALLS.items()}
            trace = []; count = 0
            def observe(cpu, address, size, _):
                nonlocal count
                target = hooks.get(address)
                if target is None: return
                name, arity = target
                regs = [cpu.reg_read(x) for x in (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                                   A.UC_ARM_REG_R2)]
                trace.append((name, *regs[:arity]))
                result = 0
                if name == 'audio_uart_page_43de82':
                    result = 0x20040000 + 0x100 * count; count += 1
                elif name == 'audio_uart_page_44104c': result = regs[0] ^ 0x0055aa55
                elif name == 'audio_uart_page_441068': result = 0x00abcdef
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            uc.hook_add(UC_HOOK_CODE, observe)
            start = symbols['audio_uart_registry_callback_5cf67e'] if compiled else BODY_START
            uc.emu_start(start | 1, 0x600000, count=5000)
            return (trace, int.from_bytes(uc.mem_read(root_cell, 4), 'little'),
                    int.from_bytes(uc.mem_read(context + 4, 4), 'little'),
                    uc.reg_read(A.UC_ARM_REG_R0), uc.reg_read(A.UC_ARM_REG_R1))

        cases = 0
        for event in (0, 1, 2, 3, 4, 5, 0xffffffff):
            for parent in (0, 0x12345678, 0x87654321, 0xffffffff):
                native, candidate = run(False, event, parent), run(True, event, parent)
                if native != candidate:
                    raise AssertionError((event, parent, native, candidate))
                cases += 1
    receipt = {'status': 'PASS_NATIVE_MAIN_GRAY_SCREEN_EVENT_5CF67E',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'official_payload_sha256': IMAGE_SHA, 'native_body_sha256': BODY_SHA,
               'native_gray_steps_sha256': hashlib.sha256(STEPS).hexdigest(),
               'cases': cases,
               'limits': ['UI calls and two RAM cells controlled; final placement and device display behavior remain open.']}
    path = OUT / 'oracle-receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases, sha(path))

if __name__ == '__main__': main()
