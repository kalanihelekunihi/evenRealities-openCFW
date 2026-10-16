#!/usr/bin/env python3
"""Compare stock/C scene-pending reset and delayed-event cancellation."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/ble_master_reset_scene_pending_4a2658.c'
IMAGE = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
IMAGE_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
BASE = 0x438000
OUT = G2 / 'build/c-firmware/20261016/main-ble-master-reset-scene-pending-4a2658'
HOOKS = {'audio_event_loop_remove_delayed': 0x476ace,
         'audio_log_flags': 0x43d0ce, 'audio_log_extended': 0x43d574,
         'compressed_log_output': 0x43ce9e}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    if hashlib.sha256(IMAGE).hexdigest() != IMAGE_SHA:
        raise RuntimeError('stock payload changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        shim = Path(tmp) / 'shim.c'
        shim.write_text('#include <stdint.h>\nuint8_t audio_ble_master_connect_state;\n'
                        '__attribute__((naked)) void audio_ble_master_connect_event(void){__asm volatile("bx lr");}\n'
                        + ''.join(f'__attribute__((naked)) uint32_t {name}(void){{__asm volatile("bx lr");}}\n'
                                  for name in HOOKS))
        elf = Path(tmp) / 'candidate.elf'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                        '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-w', '-nostdlib',
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_ble_master_reset_scene_pending_4a2658',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as fh:
            parsed = ELFFile(fh)
            segments = [(s['p_vaddr'], s.data()) for s in parsed.iter_segments() if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in parsed.get_section_by_name('.symtab').iter_symbols()}
        def run(compiled, state, flags):
            uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            uc.mem_map(0x400000, 0x400000); uc.mem_write(BASE, IMAGE)
            uc.mem_map(0x100000, 0x200000)
            for address, body in segments: uc.mem_write(address, body)
            uc.mem_map(0x20000000, 0x100000)
            state_addr = symbols['audio_ble_master_connect_state'] if compiled else 0x20074f87
            callback = (symbols['audio_ble_master_connect_event'] & ~1) if compiled else 0x4a1b60
            uc.mem_write(state_addr, bytes([state]))
            uc.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
            hooks = {(symbols[name] & ~1) if compiled else address: name
                     for name, address in HOOKS.items()}
            trace = []
            def read_string(cpu, ptr):
                return bytes(cpu.mem_read(ptr, 100)).split(b'\0', 1)[0].decode('ascii')
            def observe(cpu, address, insn_size, _):
                name = hooks.get(address)
                if name is None: return
                r0 = cpu.reg_read(A.UC_ARM_REG_R0)
                result = 0
                if name == 'audio_event_loop_remove_delayed':
                    trace.append(('remove', (r0 & ~1) == callback))
                elif name == 'audio_log_flags':
                    trace.append(('flags',)); result = flags
                elif name == 'audio_log_extended':
                    sp = cpu.reg_read(A.UC_ARM_REG_SP)
                    line = int.from_bytes(cpu.mem_read(sp, 4), 'little')
                    fmt = int.from_bytes(cpu.mem_read(sp + 4, 4), 'little')
                    trace.append(('extended', r0, line, read_string(cpu, fmt)))
                else:
                    fmt = cpu.reg_read(A.UC_ARM_REG_R1)
                    trace.append(('short', r0, read_string(cpu, fmt)))
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            uc.hook_add(UC_HOOK_CODE, observe)
            start = symbols['audio_ble_master_reset_scene_pending_4a2658'] if compiled else 0x4a2658
            uc.emu_start(start | 1, 0x600000, count=1000)
            if (uc.reg_read(A.UC_ARM_REG_PC) & ~1) != 0x600000:
                raise RuntimeError(('no return', compiled))
            return bytes(uc.mem_read(state_addr, 1)), trace
        cases = 0
        for state, flags in itertools.product(range(4), (0, 1, 2, 3, 4, 7)):
            native, candidate = run(False, state, flags), run(True, state, flags)
            if native != candidate:
                raise AssertionError(((state, flags), native, candidate))
            cases += 1
        receipt = {'status': 'PASS_NATIVE_MAIN_BLE_MASTER_RESET_SCENE_PENDING_4A2658',
                   'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
                   'official_payload_sha256': IMAGE_SHA,
                   'native_body_sha256': hashlib.sha256(IMAGE[0x4a2658-BASE:0x4a26b2-BASE]).hexdigest(),
                   'cases': cases,
                   'limits': ['Delayed-event removal and logging are controlled hooks; final event queue/RAM placement remains open.']}
        path = OUT / 'oracle-receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
        print(receipt['status'], cases, sha(path))

if __name__ == '__main__': main()
