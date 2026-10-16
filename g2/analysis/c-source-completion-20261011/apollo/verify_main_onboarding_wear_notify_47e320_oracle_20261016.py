#!/usr/bin/env python3
"""Compare stock and C onboarding wear-notification gating and event payload."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/onboarding_wear_notify_47e320.c'
IMAGE = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
IMAGE_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert hashlib.sha256(IMAGE).hexdigest() == IMAGE_SHA
BASE = 0x438000
BODY_SHA = hashlib.sha256(IMAGE[0x47e320-BASE:0x47e3e6-BASE]).hexdigest()
OUT = G2 / 'build/c-firmware/20261016/main-onboarding-wear-notify-47e320'
HOOKS = {'audio_ota_transfer_active': 0x4487ac,
         'audio_log_wake_allowed': 0x443484,
         'audio_quicklist_refresh_enabled_4434d0': 0x4434d0,
         'audio_onboarding_event_encode_4a8368': 0x4a8368,
         'audio_log_flags': 0x43d0ce, 'audio_log_extended': 0x43d574,
         'compressed_log_output': 0x43ce9e}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        shim = Path(tmp) / 'shim.c'
        shim.write_text('#include <stdint.h>\n' + ''.join(f'__attribute__((naked)) uint32_t {name}(void){{__asm volatile("bx lr");}}\n'
                                for name in HOOKS))
        elf = Path(tmp) / 'candidate.elf'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                        '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-w', '-nostdlib',
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_wear_child_47e320',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as fh:
            parsed = ELFFile(fh)
            segments = [(s['p_vaddr'], s.data()) for s in parsed.iter_segments() if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in parsed.get_section_by_name('.symtab').iter_symbols()}
        def run(compiled, status, ota, wake, enabled, encode_result, flags):
            uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            uc.mem_map(0x400000, 0x400000); uc.mem_write(BASE, IMAGE)
            uc.mem_map(0x100000, 0x200000)
            for address, body in segments: uc.mem_write(address, body)
            uc.mem_map(0x20000000, 0x100000)
            uc.reg_write(A.UC_ARM_REG_SP, 0x200ff000); uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
            uc.reg_write(A.UC_ARM_REG_R0, status)
            hooks = {(symbols[name] & ~1) if compiled else address: name
                     for name, address in HOOKS.items()}
            trace = []
            def observe(cpu, address, size, _):
                name = hooks.get(address)
                if name is None: return
                r0 = cpu.reg_read(A.UC_ARM_REG_R0)
                if name == 'audio_ota_transfer_active':
                    trace.append(('ota',)); result = ota
                elif name == 'audio_log_wake_allowed':
                    trace.append(('wake',)); result = wake
                elif name == 'audio_quicklist_refresh_enabled_4434d0':
                    trace.append(('enabled', r0)); result = enabled
                elif name == 'audio_onboarding_event_encode_4a8368':
                    ptr = cpu.reg_read(A.UC_ARM_REG_R1)
                    event = tuple(int.from_bytes(cpu.mem_read(ptr + 4*i, 4), 'little') for i in range(3))
                    trace.append(('encode', r0, event)); result = encode_result
                elif name == 'audio_log_flags':
                    trace.append(('flags',)); result = flags
                elif name == 'audio_log_extended':
                    trace.append(('extended', r0)); result = 0
                else:
                    trace.append(('short', r0)); result = 0
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            uc.hook_add(UC_HOOK_CODE, observe)
            start = symbols['audio_wear_child_47e320'] if compiled else 0x47e320
            uc.emu_start(start | 1, 0x600000, count=250)
            if (uc.reg_read(A.UC_ARM_REG_PC) & ~1) != 0x600000:
                raise RuntimeError(('no return', compiled))
            return trace
        cases = 0
        for status in (0, 1, 255):
            for ota in (0, 1, 2):
                for wake in (0, 1):
                    for enabled in (0, 1):
                        for encode_result in (0, 43):
                            for flags in (0, 1, 2, 4, 7):
                                args = (status, ota, wake, enabled, encode_result, flags)
                                native = run(False, *args); candidate = run(True, *args)
                                if native != candidate: raise AssertionError((args, native, candidate))
                                cases += 1
        receipt = {'status': 'PASS_NATIVE_MAIN_ONBOARDING_WEAR_NOTIFY_47E320',
                   'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
                   'official_payload_sha256': IMAGE_SHA, 'native_body_sha256': BODY_SHA,
                   'cases': cases,
                   'limits': ['OTA, wake, display membership, encoder and logging calls are controlled hooks; encoder implementation and device behavior remain open.']}
        path = OUT / 'oracle-receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
        print(receipt['status'], cases, sha(path))

if __name__ == '__main__': main()
