#!/usr/bin/env python3
"""Compare stock and C dominant-hand setting branches and record effects."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/setting_dominant_hand_467540.c'
IMAGE = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
IMAGE_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert hashlib.sha256(IMAGE).hexdigest() == IMAGE_SHA
BASE = 0x438000
BODY_SHA = hashlib.sha256(IMAGE[0x467540-BASE:0x467c18-BASE]).hexdigest()
OUT = G2 / 'build/c-firmware/20261016/main-setting-dominant-hand-467540'
HOOKS = {'audio_setting_unit_record_get_466010': 0x466010,
         'g2_lfs_memcmp': 0x4751c8, 'audio_queue_copy_bytes': 0x439be4,
         'audio_uart_device_role_get': 0x45a568,
         'audio_ring_connect_policy_on_hand_49f15a': 0x49f15a,
         'audio_ring_address_is_unset_4a26e8': 0x4a26e8,
         'audio_ble_master_set_target_hand_4a2068': 0x4a2068,
         'audio_uart_ring_unpair_publish_hand_4661a6': 0x4661a6,
         'audio_uart_ring_unpair_commit_hand_466016': 0x466016,
         'audio_ble_master_hand_changed_4a2948': 0x4a2948,
         'audio_ble_status_reply': 0x47d870,
         'audio_log_flags': 0x43d0ce, 'audio_log_extended': 0x43d574,
         'compressed_log_output': 0x43ce9e}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

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
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_setting_dispatch_type11_467540',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as fh:
            parsed = ELFFile(fh)
            segments = [(s['p_vaddr'], s.data()) for s in parsed.iter_segments() if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in parsed.get_section_by_name('.symtab').iter_symbols()}
        def run(compiled, size, changed, outcome, role, flags, desired, unset):
            uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            uc.mem_map(0x400000, 0x400000); uc.mem_write(BASE, IMAGE)
            uc.mem_map(0x100000, 0x200000)
            for address, body in segments: uc.mem_write(address, body)
            uc.mem_map(0x20000000, 0x100000)
            record = 0x20020000; data = 0x20021000
            before = bytearray((i * 3 + 0x42) & 255 for i in range(0x30))
            before[11] = 1
            uc.mem_write(record, bytes(before))
            payload = bytearray(16)
            payload[0] = desired
            payload[4:6] = ((size or 0) & 0xffff).to_bytes(2, 'little')
            payload[6:12] = bytes((0x91 + i) & 255 for i in range(6))
            uc.mem_write(data, bytes(payload))
            uc.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
            uc.reg_write(A.UC_ARM_REG_R0, 0 if size is None else data)
            hooks = {(symbols[name] & ~1) if compiled else address: name
                     for name, address in HOOKS.items()}
            trace = []
            def observe(cpu, address, insn_size, _):
                name = hooks.get(address)
                if name is None: return
                r0, r1, r2 = (cpu.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                result = 0
                if name == 'audio_setting_unit_record_get_466010':
                    trace.append(('record',)); result = record
                elif name == 'g2_lfs_memcmp':
                    trace.append(('memcmp', r0 == record + 12, r1 == data + 6, r2))
                    result = 1 if changed else 0
                elif name == 'audio_queue_copy_bytes':
                    trace.append(('copy', r0 == record + 12, r1 == data + 6, r2))
                    cpu.mem_write(r0, bytes(cpu.mem_read(r1, r2))); result = r0
                elif name == 'audio_uart_device_role_get':
                    trace.append(('role',)); result = role
                elif name == 'audio_ring_connect_policy_on_hand_49f15a':
                    trace.append(('policy', r0, r1)); result = outcome
                elif name == 'audio_ring_address_is_unset_4a26e8':
                    trace.append(('unset', r0 == record + 12)); result = unset
                elif name == 'audio_ble_master_set_target_hand_4a2068':
                    trace.append(('target', r0 == record + 12, r1, r2))
                elif name == 'audio_uart_ring_unpair_publish_hand_4661a6':
                    trace.append(('publish',))
                elif name == 'audio_uart_ring_unpair_commit_hand_466016':
                    trace.append(('commit',))
                elif name == 'audio_ble_master_hand_changed_4a2948':
                    trace.append(('changed', r0, r1, r2))
                elif name == 'audio_ble_status_reply':
                    trace.append(('reply', r0))
                elif name == 'audio_log_flags':
                    trace.append(('flags',)); result = flags
                elif name == 'audio_log_extended':
                    trace.append(('extended', r0))
                else:
                    trace.append(('short', r0))
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            uc.hook_add(UC_HOOK_CODE, observe)
            start = symbols['audio_setting_dispatch_type11_467540'] if compiled else 0x467540
            uc.emu_start(start | 1, 0x600000, count=5000)
            if (uc.reg_read(A.UC_ARM_REG_PC) & ~1) != 0x600000:
                raise RuntimeError(('no return', compiled))
            return bytes(uc.mem_read(record, 0x30)), trace
        cases = 0
        params = [(None, 0), (0, 0), (6, 0), (6, 1), (3, 0), (-1, 0)]
        for (size, changed), outcome, role, flags, desired, unset in itertools.product(
                params, (0, 1, 2, 3), (0, 1), (0, 1, 2, 4, 7), (0, 2), (0, 1)):
            args = (size, changed, outcome, role, flags, desired, unset)
            native = run(False, *args); candidate = run(True, *args)
            if native != candidate: raise AssertionError((args, native, candidate))
            cases += 1
        receipt = {'status': 'PASS_NATIVE_MAIN_SETTING_DOMINANT_HAND_467540',
                   'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
                   'official_payload_sha256': IMAGE_SHA, 'native_body_sha256': BODY_SHA,
                   'cases': cases,
                   'limits': ['Record, compare/copy, policy, target, reconnect, reply and logging children are controlled hooks; these exposed children need independent C bodies.']}
        path = OUT / 'oracle-receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
        print(receipt['status'], cases, sha(path))

if __name__ == '__main__': main()
