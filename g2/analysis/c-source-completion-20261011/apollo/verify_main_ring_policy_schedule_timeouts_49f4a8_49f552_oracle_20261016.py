#!/usr/bin/env python3
"""Compare stock/C ring connect and reconnect timeout scheduling."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/ring_policy_schedule_timeouts_49f4a8_49f552.c'
IMAGE = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
IMAGE_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
BASE = 0x438000
OUT = G2 / 'build/c-firmware/20261016/main-ring-policy-schedule-timeouts-49f4a8-49f552'
HOOKS = {'audio_event_loop_remove_delayed': 0x476ace,
         'audio_event_loop_push_delayed': 0x47697e,
         'audio_log_flags': 0x43d0ce, 'audio_log_extended': 0x43d574,
         'compressed_log_output': 0x43ce9e}
CALLBACKS = {'audio_ble_ring_policy_delayed': 0x49f500,
             'audio_ble_master_success_delayed': 0x4bc418}
TARGETS = {'audio_ble_ring_policy_schedule_connect_timeout_49f4a8': (0x49f4a8, 0x49f500),
           'audio_ble_ring_policy_schedule_reconnect_timeout_49f552': (0x49f552, 0x49f5f8)}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    if hashlib.sha256(IMAGE).hexdigest() != IMAGE_SHA:
        raise RuntimeError('stock payload changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        shim = Path(tmp) / 'shim.c'
        shim.write_text('#include <stdint.h>\nuint8_t audio_ble_ring_policy_pending_2007500b;\n'
                        + ''.join(f'__attribute__((naked)) uint32_t {name}(void){{__asm volatile("bx lr");}}\n'
                                  for name in HOOKS)
                        + ''.join(f'__attribute__((naked)) uint32_t {name}(void){{__asm volatile("bx lr");}}\n'
                                  for name in CALLBACKS))
        elf = Path(tmp) / 'candidate.elf'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                        '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-w', '-nostdlib',
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_ble_ring_policy_schedule_connect_timeout_49f4a8',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as fh:
            parsed = ELFFile(fh)
            segments = [(s['p_vaddr'], s.data()) for s in parsed.iter_segments() if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in parsed.get_section_by_name('.symtab').iter_symbols()}
        def run(compiled, target, pending, flags):
            uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            uc.mem_map(0x400000, 0x400000); uc.mem_write(BASE, IMAGE)
            uc.mem_map(0x100000, 0x200000)
            for address, body in segments: uc.mem_write(address, body)
            uc.mem_map(0x20000000, 0x100000)
            state = symbols['audio_ble_ring_policy_pending_2007500b'] if compiled else 0x2007500b
            uc.mem_write(state, bytes([pending]))
            uc.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
            hooks = {(symbols[name] & ~1) if compiled else address: name
                     for name, address in HOOKS.items()}
            callbacks = {(symbols[name] & ~1) if compiled else address: name
                         for name, address in CALLBACKS.items()}
            trace = []
            def read_string(cpu, ptr):
                return bytes(cpu.mem_read(ptr, 110)).split(b'\0', 1)[0].decode('ascii')
            def observe(cpu, address, insn_size, _):
                name = hooks.get(address)
                if name is None: return
                r0, r1, r2 = (cpu.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                result = 0
                if name == 'audio_event_loop_remove_delayed':
                    trace.append(('remove', callbacks.get(r0 & ~1, '?')))
                elif name == 'audio_event_loop_push_delayed':
                    trace.append(('push', callbacks.get(r0 & ~1, '?'), r1, r2))
                elif name == 'audio_log_flags':
                    trace.append(('flags',)); result = flags
                elif name == 'audio_log_extended':
                    sp = cpu.reg_read(A.UC_ARM_REG_SP)
                    line = int.from_bytes(cpu.mem_read(sp, 4), 'little')
                    fmt = int.from_bytes(cpu.mem_read(sp + 4, 4), 'little')
                    trace.append(('extended', r0, line, read_string(cpu, fmt)))
                else:
                    trace.append(('short', r0, read_string(cpu, r1)))
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            uc.hook_add(UC_HOOK_CODE, observe)
            start = symbols[target] if compiled else TARGETS[target][0]
            uc.emu_start(start | 1, 0x600000, count=1000)
            if (uc.reg_read(A.UC_ARM_REG_PC) & ~1) != 0x600000:
                raise RuntimeError(('no return', compiled))
            return bytes(uc.mem_read(state, 1)), trace
        cases = 0
        for target, pending, flags in itertools.product(TARGETS, (0, 1, 255), (0, 1, 2, 3, 4, 7)):
            native, candidate = run(False, target, pending, flags), run(True, target, pending, flags)
            if native != candidate:
                raise AssertionError(((target, pending, flags), native, candidate))
            cases += 1
        receipt = {'status': 'PASS_NATIVE_MAIN_RING_POLICY_SCHEDULE_TIMEOUTS_49F4A8_49F552',
                   'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
                   'official_payload_sha256': IMAGE_SHA,
                   'native_body_sha256': {name: hashlib.sha256(IMAGE[start-BASE:end-BASE]).hexdigest()
                                          for name, (start, end) in TARGETS.items()},
                   'cases': cases,
                   'limits': ['Event scheduling and logging providers are controlled hooks; real scheduler timing and hardware execution remain open.']}
        path = OUT / 'oracle-receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
        print(receipt['status'], cases, sha(path))

if __name__ == '__main__': main()
