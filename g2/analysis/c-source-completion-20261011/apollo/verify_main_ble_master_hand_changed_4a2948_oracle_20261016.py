#!/usr/bin/env python3
"""Compare stock and C dominant-hand master connection branch effects."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/ble_master_hand_changed_4a2948.c'
IMAGE = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
IMAGE_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
BASE = 0x438000
OUT = G2 / 'build/c-firmware/20261016/main-ble-master-hand-changed-4a2948'
HOOKS = {
    'audio_uart_ring_active': 0x4a2914,
    'audio_ble_peer_ring_status_47d8f0': 0x47d8f0,
    'audio_ble_ring_link_state_name': 0x49f828,
    'audio_setting_unit_record_get_466010': 0x466010,
    'audio_queue_copy_bytes': 0x439be4,
    'audio_ring_address_is_unset_4a26e8': 0x4a26e8,
    'audio_ble_master_link_matches_target': 0x4a2864,
    'audio_ble_master_set_target_hand_4a2068': 0x4a2068,
    'audio_ble_master_auth_mode_set': 0x4a2168,
    'audio_ble_master_reset_retry_count': 0x4a2300,
    'audio_ble_master_clear_failure_notify': 0x4a15c0,
    'audio_ble_master_begin_failure_notify_4a1546': 0x4a1546,
    'audio_ble_master_reset_scene_pending_4a2658': 0x4a2658,
    'audio_ble_master_schedule_connect': 0x4a2618,
    'audio_ble_master_disconnect_delayed': 0x4a01fc,
    'audio_ble_ring_policy_schedule_connect_timeout_49f4a8': 0x49f4a8,
    'audio_ble_ring_policy_schedule_reconnect_timeout_49f552': 0x49f552,
    'audio_ble_ring_policy_cancel_connect_timeout_49f5f8': 0x49f5f8,
    'audio_ble_ring_policy_notify_success_49f646': 0x49f646,
    'audio_ble_set_ring_link_state': 0x49f870,
    'audio_event_loop_remove_delayed': 0x476ace,
    'audio_event_loop_push_delayed': 0x47697e,
    'audio_log_flags': 0x43d0ce,
    'audio_log_extended': 0x43d574,
    'compressed_log_output': 0x43ce9e,
}
CALLBACKS = {'audio_ble_master_connect_event': 0x4a1b60,
             'audio_ble_master_start_try_connect_ring': 0x4a23ac}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    if hashlib.sha256(IMAGE).hexdigest() != IMAGE_SHA:
        raise RuntimeError('stock payload changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        shim = Path(tmp) / 'shim.c'
        shim.write_text('#include <stdint.h>\n'
                        'uint8_t audio_ble_ring_link_state;\n'
                        'uint8_t audio_ble_master_open_connection;\n'
                        'uint8_t *audio_ble_master_context;\n'
                        + ''.join(f'__attribute__((naked)) uint32_t {name}(void){{__asm volatile("bx lr");}}\n'
                                  for name in HOOKS)
                        + ''.join(f'__attribute__((naked)) void {name}(void){{__asm volatile("bx lr");}}\n'
                                  for name in CALLBACKS))
        elf = Path(tmp) / 'candidate.elf'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                        '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-w', '-nostdlib',
                        '-Wl,-Ttext=0x100000', '-Wl,-e,audio_ble_master_hand_changed_4a2948',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as fh:
            parsed = ELFFile(fh)
            segments = [(s['p_vaddr'], s.data()) for s in parsed.iter_segments() if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in parsed.get_section_by_name('.symtab').iter_symbols()}
        def run(compiled, scenario, desired, delay, silent, flags):
            owner, state, opening, context, unset, match = scenario
            uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            uc.mem_map(0x400000, 0x400000); uc.mem_write(BASE, IMAGE)
            uc.mem_map(0x100000, 0x200000)
            for address, body in segments: uc.mem_write(address, body)
            uc.mem_map(0x20000000, 0x100000)
            state_addr = symbols['audio_ble_ring_link_state'] if compiled else 0x20074f85
            opening_addr = symbols['audio_ble_master_open_connection'] if compiled else 0x20074f86
            context_addr = symbols['audio_ble_master_context'] if compiled else 0x200742fc
            uc.mem_write(state_addr, bytes([state]))
            uc.mem_write(opening_addr, bytes([opening]))
            uc.mem_write(context_addr, (0 if context == 0 else 0x20024000).to_bytes(4, 'little'))
            uc.mem_write(0x20024000 + 0x55, bytes([1 if context == 2 else 0]))
            uc.mem_write(0x20020000 + 12, b'\x91\x92\x93\x94\x95\x96')
            uc.mem_write(0x20023000, b'OPENING\0')
            uc.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
            for reg, val in zip((A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                 A.UC_ARM_REG_R2, A.UC_ARM_REG_R3),
                                (desired, delay, silent, 0x1457)):
                uc.reg_write(reg, val)
            hooks = {(symbols[name] & ~1) if compiled else address: name
                     for name, address in HOOKS.items()}
            callback_addr = {(symbols[name] & ~1) if compiled else address: name
                             for name, address in CALLBACKS.items()}
            trace = []
            def read_string(cpu, ptr):
                return bytes(cpu.mem_read(ptr, 160)).split(b'\0', 1)[0].decode('ascii')
            def observe(cpu, address, insn_size, _):
                name = hooks.get(address)
                if name is None: return
                r0, r1, r2 = (cpu.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                result = 0
                if name == 'audio_uart_ring_active':
                    trace.append(('owner',)); result = owner
                elif name == 'audio_ble_peer_ring_status_47d8f0':
                    trace.append(('peer',)); result = 1
                elif name == 'audio_ble_ring_link_state_name':
                    trace.append(('state-name', r0)); result = 0x20023000
                elif name == 'audio_setting_unit_record_get_466010':
                    trace.append(('record',)); result = 0x20020000
                elif name == 'audio_queue_copy_bytes':
                    trace.append(('copy', r2, r1 == 0x2002000c,
                                  bytes(cpu.mem_read(r1, r2))))
                    cpu.mem_write(r0, bytes(cpu.mem_read(r1, r2))); result = r0
                elif name == 'audio_ring_address_is_unset_4a26e8':
                    trace.append(('unset', bytes(cpu.mem_read(r0, 6))))
                    result = unset
                elif name == 'audio_ble_master_link_matches_target':
                    trace.append(('matches', bytes(cpu.mem_read(r0, 6))))
                    result = match
                elif name == 'audio_ble_master_set_target_hand_4a2068':
                    trace.append(('target', bytes(cpu.mem_read(r0, 6)),
                                  bytes(cpu.mem_read(r1, r2)), r2))
                elif name == 'audio_ble_master_auth_mode_set':
                    trace.append(('auth', r0))
                elif name == 'audio_ble_master_schedule_connect':
                    trace.append(('schedule', r0, r1))
                elif name == 'audio_ble_master_disconnect_delayed':
                    trace.append(('cancel-connection', r0))
                elif name == 'audio_ble_set_ring_link_state':
                    trace.append(('link-state', r0, read_string(cpu, r1)))
                    cpu.mem_write(state_addr, bytes([r0 & 255]))
                elif name in ('audio_event_loop_remove_delayed', 'audio_event_loop_push_delayed'):
                    trace.append((name, callback_addr.get(r0 & ~1, '?'), r1, r2)
                                 if name == 'audio_event_loop_push_delayed'
                                 else (name, callback_addr.get(r0 & ~1, '?')))
                elif name == 'audio_log_flags':
                    trace.append(('flags',)); result = flags
                elif name == 'audio_log_extended':
                    sp = cpu.reg_read(A.UC_ARM_REG_SP)
                    line = int.from_bytes(cpu.mem_read(sp, 4), 'little')
                    fmt = int.from_bytes(cpu.mem_read(sp + 4, 4), 'little')
                    trace.append(('extended', r0, line, read_string(cpu, fmt)))
                elif name == 'compressed_log_output':
                    trace.append(('short', r0, read_string(cpu, r1)))
                else:
                    trace.append((name,))
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            uc.hook_add(UC_HOOK_CODE, observe)
            start = symbols['audio_ble_master_hand_changed_4a2948'] if compiled else 0x4a2948
            uc.emu_start(start | 1, 0x600000, count=3000)
            if (uc.reg_read(A.UC_ARM_REG_PC) & ~1) != 0x600000:
                raise RuntimeError(('no return', compiled))
            return bytes(uc.mem_read(state_addr, 1)), trace
        scenarios = [(1, 0, 0, 0, 1, 0), (1, 0, 0, 0, 0, 1),
                     (1, 0, 0, 0, 0, 0), (0, 1, 4, 0, 0, 0),
                     (0, 0, 0, 0, 0, 0), (0, 0, 0, 1, 0, 0),
                     (0, 0, 0, 2, 0, 0)]
        cases = 0
        for scenario, desired, delay, silent, flags in itertools.product(
                scenarios, (0, 1), (0, 4000), (0, 1), (0, 1, 2, 4, 7)):
            args = (scenario, desired, delay, silent, flags)
            native, candidate = run(False, *args), run(True, *args)
            if native != candidate:
                raise AssertionError((args, native, candidate))
            cases += 1
        receipt = {'status': 'PASS_NATIVE_MAIN_BLE_MASTER_HAND_CHANGED_4A2948',
                   'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
                   'official_payload_sha256': IMAGE_SHA,
                   'native_body_sha256': hashlib.sha256(IMAGE[0x4a2948-BASE:0x4a2c6a-BASE]).hexdigest(),
                   'cases': cases,
                   'limits': ['Owner, peer status, record, copy, policy, scheduler, state and logging children are controlled hooks; their independent bodies and final hardware/RAM integration remain open. Logging compares branch identity, format and severity, not every variadic argument.']}
        path = OUT / 'oracle-receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
        print(receipt['status'], cases, sha(path))

if __name__ == '__main__': main()
