#!/usr/bin/env python3
"""Compare stock and C onboarding event nanopb preparation and dispatch."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/onboarding_event_encode_4a8368.c'
SCHEMA = G2 / 'components/audio/uart_thread_source_candidate/onboarding_event_pb_descriptor_779c94.c'
IMAGE = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
IMAGE_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert hashlib.sha256(IMAGE).hexdigest() == IMAGE_SHA
BASE = 0x438000
BODY_SHA = hashlib.sha256(IMAGE[0x4a8368-BASE:0x4a84d2-BASE]).hexdigest()
OUT = G2 / 'build/c-firmware/20261016/main-onboarding-event-encode-4a8368'
HOOKS = {'audio_pb_ostream_from_buffer': 0x4905f4,
         'audio_uart_checksum_copy': 0x439c04,
         'audio_uart_buffer_zero': 0x43c0e4,
         'audio_pb_encode': 0x490c32,
         'audio_ring_pb_tx_ble_475c1a': 0x475c1a,
         'audio_ring_pb_assert_509b48': 0x509b48,
         'audio_log_flags': 0x43d0ce, 'audio_log_extended': 0x43d574,
         'compressed_log_output': 0x43ce9e}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def u32(value): return (value & 0xffffffff).to_bytes(4, 'little')
def word(cpu, address): return int.from_bytes(cpu.mem_read(address, 4), 'little')
def descriptor_signature(cpu, root):
    def node(address, field_words):
        fields = word(cpu, address)
        return (tuple(word(cpu, fields + 4*i) for i in range(field_words)),
                word(cpu, address + 16), word(cpu, address + 20))
    children = word(cpu, root + 4)
    return (node(root, 9),
            tuple(node(word(cpu, children + 4*i), length)
                  for i, length in enumerate((3, 2, 4))),
            word(cpu, children + 12))

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        shim = Path(tmp) / 'shim.c'
        shim.write_text('#include <stdint.h>\n' + ''.join(
            f'__attribute__((naked)) uint32_t {name}(void){{__asm volatile("bx lr");}}\n'
            for name in HOOKS))
        elf = Path(tmp) / 'candidate.elf'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                        '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-w', '-nostdlib',
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_onboarding_event_encode_4a8368',
                        str(SOURCE), str(SCHEMA), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as fh:
            parsed = ELFFile(fh)
            segments = [(s['p_vaddr'], s.data()) for s in parsed.iter_segments() if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in parsed.get_section_by_name('.symtab').iter_symbols()}
        def run(compiled, payload, encode_ok, sequence, flags, written, errmsg):
            uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            uc.mem_map(0x400000, 0x400000); uc.mem_write(BASE, IMAGE)
            uc.mem_map(0x100000, 0x200000)
            for address, body in segments: uc.mem_write(address, body)
            uc.mem_map(0x20000000, 0x400000)
            input_addr = 0x20010000
            if payload is not None: uc.mem_write(input_addr, payload)
            packet = symbols['audio_onboarding_event_packet_200f612c'] if compiled else 0x200f612c
            state = symbols['audio_onboarding_event_state_200f623c'] if compiled else 0x200f623c
            seq_addr = symbols['audio_onboarding_event_sequence_20074ffb'] if compiled else 0x20074ffb
            descriptor = symbols['audio_onboarding_event_descriptor_779c94'] if compiled else 0x779c94
            uc.mem_write(packet, b'\xa5' * 256); uc.mem_write(state, b'\x5a' * 16)
            uc.mem_write(seq_addr, bytes([sequence]))
            hooks = {(symbols[name] & ~1) if compiled else address: name
                     for name, address in HOOKS.items()}
            trace = []
            def observe(cpu, address, size, _):
                name = hooks.get(address)
                if name is None: return
                r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                                  (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                   A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                result = 0
                if name == 'audio_pb_ostream_from_buffer':
                    trace.append(('ostream', r1 == packet, r2))
                    cpu.mem_write(r0, u32(0x12345679) + u32(r1) + u32(r2) + bytes(8))
                elif name == 'audio_uart_checksum_copy':
                    trace.append(('copy', r2))
                    cpu.mem_write(r0, bytes(cpu.mem_read(r1, r2))); result = r0
                elif name == 'audio_uart_buffer_zero':
                    trace.append(('zero', r0 == state, r1, r2))
                    cpu.mem_write(r0, bytes([r2 & 255]) * r1)
                elif name == 'audio_pb_encode':
                    snapshot = bytes(cpu.mem_read(state, 16))
                    trace.append(('encode', r1 == descriptor, r2 == state, snapshot,
                                  descriptor_signature(cpu, r1)))
                    cpu.mem_write(r0 + 12, u32(written))
                    cpu.mem_write(r0 + 16, u32(errmsg))
                    result = int(encode_ok)
                elif name == 'audio_ring_pb_tx_ble_475c1a':
                    trace.append(('send', r0, r1, r2 == packet, r3))
                elif name == 'audio_ring_pb_assert_509b48':
                    raw = bytes(cpu.mem_read(r0, 20))
                    trace.append(('assert', raw[:8], raw[16:20]))
                elif name == 'audio_log_flags':
                    trace.append(('flags',)); result = flags
                elif name == 'audio_log_extended':
                    trace.append(('extended', r0))
                else:
                    trace.append(('short', r0))
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            uc.hook_add(UC_HOOK_CODE, observe)
            uc.reg_write(A.UC_ARM_REG_R0, 0)
            uc.reg_write(A.UC_ARM_REG_R1, 0 if payload is None else input_addr)
            uc.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
            start = symbols['audio_onboarding_event_encode_4a8368'] if compiled else 0x4a8368
            uc.emu_start(start | 1, 0x600000, count=600)
            if (uc.reg_read(A.UC_ARM_REG_PC) & ~1) != 0x600000:
                raise RuntimeError(('no return', compiled))
            return (uc.reg_read(A.UC_ARM_REG_R0), bytes(uc.mem_read(state, 16)),
                    bytes(uc.mem_read(seq_addr, 1)), trace)
        cases = 0
        for payload in (None, bytes(12), bytes(range(12))):
            for encode_ok in (False, True):
                for sequence in (0, 255):
                    for flags in (0, 1, 2, 4, 7):
                        for errmsg in (0, 0x20010100):
                            args = (payload, encode_ok, sequence, flags, 0x12345, errmsg)
                            native = run(False, *args); candidate = run(True, *args)
                            if native != candidate: raise AssertionError((args, native, candidate))
                            cases += 1
        receipt = {'status': 'PASS_NATIVE_MAIN_ONBOARDING_EVENT_ENCODE_4A8368',
                   'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
                   'descriptor_source': str(SCHEMA.relative_to(ROOT)),
                   'descriptor_source_sha256': sha(SCHEMA),
                   'official_payload_sha256': IMAGE_SHA, 'native_body_sha256': BODY_SHA,
                   'cases': cases,
                   'limits': ['Nanopb stream, copy, encode, BLE send, fault and logging calls are controlled hooks; RAM placement and hardware behavior remain open.']}
        path = OUT / 'oracle-receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
        print(receipt['status'], cases, sha(path))

if __name__ == '__main__': main()
