#!/usr/bin/env python3
"""Compare the stock target setter with the existing C provider and address adapter."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/ble_master_set_target_hand_4a2068.c'
PROVIDER = G2 / 'components/audio/uart_thread_source_candidate/display_ble_master_connect_children.c'
IMAGE = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
IMAGE_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
BASE = 0x438000
OUT = G2 / 'build/c-firmware/20261016/main-ble-master-set-target-hand-4a2068'
HOOKS = {'audio_queue_copy_bytes': 0x439be4,
         'audio_uart_buffer_zero': 0x43c0e4,
         'audio_log_level': 0x43d0ce,
         'audio_log_extended': 0x43d574,
         'compressed_log_output': 0x43ce9e}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    if hashlib.sha256(IMAGE).hexdigest() != IMAGE_SHA:
        raise RuntimeError('stock payload changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        shim = Path(tmp) / 'shim.c'
        shim.write_text('#include <stdint.h>\n'
                        'uint8_t audio_ble_master_target_address[6];\n'
                        'char audio_ble_master_target_name[15];\n'
                        'uint8_t audio_ble_master_auth_mode;\n'
                        'uint8_t audio_ble_master_connect_state;\n'
                        '__attribute__((naked)) void audio_ble_master_connect_event(void){__asm volatile("bx lr");}\n'
                        '__attribute__((naked)) void audio_ble_master_cancel_retry(void){__asm volatile("bx lr");}\n'
                        '__attribute__((naked)) void audio_event_loop_push_delayed(void){__asm volatile("bx lr");}\n'
                        + ''.join(f'__attribute__((naked)) uint32_t {name}(void){{__asm volatile("bx lr");}}\n'
                                  for name in HOOKS))
        elf = Path(tmp) / 'candidate.elf'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                        '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-w', '-nostdlib',
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_ble_master_set_target_hand_4a2068',
                        str(SOURCE), str(PROVIDER), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as fh:
            parsed = ELFFile(fh)
            segments = [(s['p_vaddr'], s.data()) for s in parsed.iter_segments() if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in parsed.get_section_by_name('.symtab').iter_symbols()}
        def run(compiled, use_address, use_name, name_length, flags):
            uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            uc.mem_map(0x400000, 0x400000); uc.mem_write(BASE, IMAGE)
            uc.mem_map(0x100000, 0x200000)
            for address, body in segments: uc.mem_write(address, body)
            uc.mem_map(0x20000000, 0x100000)
            target_address = symbols['audio_ble_master_target_address'] if compiled else 0x200003c0
            target_name = symbols['audio_ble_master_target_name'] if compiled else 0x200003c8
            uc.mem_write(target_address, b'\x11\x22\x33\x44\x55\x66')
            uc.mem_write(target_name, b'OLD TARGET NAME')
            uc.mem_write(0x20021000, b'\x91\x92\x93\x94\x95\x96')
            uc.mem_write(0x20022000, b'NEW TARGET NAME')
            uc.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
            uc.reg_write(A.UC_ARM_REG_R0, 0x20021000 if use_address else 0)
            uc.reg_write(A.UC_ARM_REG_R1, 0x20022000 if use_name else 0)
            uc.reg_write(A.UC_ARM_REG_R2, name_length)
            hooks = {(symbols[name] & ~1) if compiled else address: name
                     for name, address in HOOKS.items()}
            trace = []
            def read_string(cpu, ptr):
                return bytes(cpu.mem_read(ptr, 160)).split(b'\0', 1)[0].decode('ascii')
            def observe(cpu, address, insn_size, _):
                name = hooks.get(address)
                if name is None: return
                r0, r1, r2 = (cpu.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                result = 0
                if name == 'audio_queue_copy_bytes':
                    trace.append(('copy', r0 == target_address, r0 == target_name,
                                  r1 in (0x20021000, 0x20022000), r2))
                    cpu.mem_write(r0, bytes(cpu.mem_read(r1, r2))); result = r0
                elif name == 'audio_uart_buffer_zero':
                    trace.append(('zero', r0 == target_name, r1, r2))
                    cpu.mem_write(r0, bytes([r2 & 255]) * r1)
                elif name == 'audio_log_level':
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
            start = symbols['audio_ble_master_set_target_hand_4a2068'] if compiled else 0x4a2068
            uc.emu_start(start | 1, 0x600000, count=1500)
            if (uc.reg_read(A.UC_ARM_REG_PC) & ~1) != 0x600000:
                raise RuntimeError(('no return', compiled))
            return (bytes(uc.mem_read(target_address, 6)),
                    bytes(uc.mem_read(target_name, 15)), trace)
        cases = 0
        for address, name, length, flags in itertools.product(
                (False, True), (False, True), (0, 1, 3, 15), (0, 1, 2, 4, 7)):
            args = (address, name, length, flags)
            native, candidate = run(False, *args), run(True, *args)
            if native != candidate:
                raise AssertionError((args, native, candidate))
            cases += 1
        receipt = {'status': 'PASS_NATIVE_MAIN_BLE_MASTER_SET_TARGET_HAND_4A2068',
                   'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
                   'provider': str(PROVIDER.relative_to(ROOT)), 'provider_sha256': sha(PROVIDER),
                   'official_payload_sha256': IMAGE_SHA,
                   'native_body_sha256': hashlib.sha256(IMAGE[0x4a2068-BASE:0x4a2164-BASE]).hexdigest(),
                   'cases': cases,
                   'limits': ['Copy, zero and log providers are controlled hooks; native/C target storage effects and logging branch identities are compared. Final RAM placement remains open.']}
        path = OUT / 'oracle-receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
        print(receipt['status'], cases, sha(path))

if __name__ == '__main__': main()
