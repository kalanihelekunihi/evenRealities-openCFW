#!/usr/bin/env python3
"""Compare stock and C SendDataToBothExt packet, allocation and failure paths."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/sync_send_to_both_ext_464f76.c'
IMAGE = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
IMAGE_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert hashlib.sha256(IMAGE).hexdigest() == IMAGE_SHA
BASE = 0x438000
BODY_SHA = hashlib.sha256(IMAGE[0x464f76-BASE:0x4651aa-BASE]).hexdigest()
OUT = G2 / 'build/c-firmware/20261016/main-sync-send-to-both-ext-464f76'
HOOKS = {'audio_uart_alloc_retry': 0x4646f0,
         'audio_uart_buffer_zero': 0x43c0e4,
         'audio_queue_copy_bytes': 0x439be4,
         'audio_cmsis_queue_put': 0x449abe,
         'g2_log_event_set_task': 0x4495e4,
         'audio_file_heap_free': 0x474d16,
         'audio_log_flags': 0x43d0ce, 'audio_log_extended': 0x43d574,
         'compressed_log_output': 0x43ce9e}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def u32(value): return (value & 0xffffffff).to_bytes(4, 'little')

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        shim = Path(tmp) / 'shim.c'
        shim.write_text('#include <stdint.h>\nvoid *g2_uart_send_queue;\nvoid *g2_uart_thread_event;\n' +
                        ''.join(f'__attribute__((naked)) uint32_t {name}(void){{__asm volatile("bx lr");}}\n'
                                for name in HOOKS))
        elf = Path(tmp) / 'candidate.elf'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                        '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-w', '-nostdlib',
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_sync_send_to_both_ext_464f76',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as fh:
            parsed = ELFFile(fh)
            segments = [(s['p_vaddr'], s.data()) for s in parsed.iter_segments() if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in parsed.get_section_by_name('.symtab').iter_symbols()}
        def run(compiled, stage, app, length, event, flags):
            uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            uc.mem_map(0x400000, 0x400000); uc.mem_write(BASE, IMAGE)
            uc.mem_map(0x100000, 0x200000)
            for address, body in segments: uc.mem_write(address, body)
            uc.mem_map(0x20000000, 0x400000)
            src = 0x20010000; node = 0x20020000; packet = 0x20021000
            uc.mem_write(src, bytes((i * 13 + 9) & 255 for i in range(0x10000)))
            uc.mem_write(node, b'\xa5' * 12)
            uc.mem_write(packet, b'\x5a' * 0x10008)
            queue_cell = symbols['g2_uart_send_queue'] if compiled else 0x200749cc
            event_cell = symbols['g2_uart_thread_event'] if compiled else 0x20074b10
            uc.mem_write(queue_cell, u32(0 if stage == 0 else 0x12345678))
            uc.mem_write(event_cell, u32(0x87654321))
            sp = 0x203ff000
            uc.reg_write(A.UC_ARM_REG_SP, sp); uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
            uc.reg_write(A.UC_ARM_REG_R0, app); uc.reg_write(A.UC_ARM_REG_R1, src)
            uc.reg_write(A.UC_ARM_REG_R2, length); uc.reg_write(A.UC_ARM_REG_R3, 0x89abcdef)
            uc.mem_write(sp, u32(event))
            hooks = {(symbols[name] & ~1) if compiled else address: name
                     for name, address in HOOKS.items()}
            trace = []; alloc_count = [0]
            def observe(cpu, address, size, _):
                name = hooks.get(address)
                if name is None: return
                r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                                  (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                   A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                result = 0
                if name == 'audio_uart_alloc_retry':
                    alloc_count[0] += 1
                    trace.append(('alloc', r0))
                    result = 0 if (alloc_count[0] == 1 and stage == 1) or (alloc_count[0] == 2 and stage == 2) else (node if alloc_count[0] == 1 else packet)
                elif name == 'audio_uart_buffer_zero':
                    trace.append(('zero', r0 == node, r1, r2))
                    cpu.mem_write(r0, bytes([r2 & 255]) * r1)
                elif name == 'audio_queue_copy_bytes':
                    trace.append(('copy', r0 == packet + 8, r1 == src, r2))
                    cpu.mem_write(r0, bytes(cpu.mem_read(r1, r2))); result = r0
                elif name == 'audio_cmsis_queue_put':
                    ptr = int.from_bytes(cpu.mem_read(r1, 4), 'little')
                    trace.append(('queue', r0, ptr == node, bytes(cpu.mem_read(node, 12)),
                                  bytes(cpu.mem_read(packet, 8 + (length & 0xffff))), r2, r3))
                    result = 7 if stage == 3 else 0
                elif name == 'g2_log_event_set_task':
                    trace.append(('event', r0, r1))
                elif name == 'audio_file_heap_free':
                    trace.append(('free', r0))
                elif name == 'audio_log_flags':
                    trace.append(('flags',)); result = flags
                elif name == 'audio_log_extended':
                    trace.append(('extended', r0))
                else:
                    trace.append(('short', r0))
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            uc.hook_add(UC_HOOK_CODE, observe)
            start = symbols['audio_sync_send_to_both_ext_464f76'] if compiled else 0x464f76
            uc.emu_start(start | 1, 0x600000, count=1000)
            if (uc.reg_read(A.UC_ARM_REG_PC) & ~1) != 0x600000:
                raise RuntimeError(('no return', compiled))
            return uc.reg_read(A.UC_ARM_REG_R0), trace
        cases = 0
        for args in itertools.product(range(5), (0x10a, 0xffff1234),
                                      (0, 1, 5, 0x10001, 0xffff),
                                      (4, 0xabcdef04), (0, 1, 2, 4, 7)):
            native = run(False, *args); candidate = run(True, *args)
            if native != candidate: raise AssertionError((args, native, candidate))
            cases += 1
        receipt = {'status': 'PASS_NATIVE_MAIN_SYNC_SEND_TO_BOTH_EXT_464F76',
                   'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
                   'official_payload_sha256': IMAGE_SHA, 'native_body_sha256': BODY_SHA,
                   'cases': cases,
                   'limits': ['Allocation, copy, queue, event, free and logging calls are controlled hooks; final heap and queue behavior remain open.']}
        path = OUT / 'oracle-receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
        print(receipt['status'], cases, sha(path))

if __name__ == '__main__': main()
