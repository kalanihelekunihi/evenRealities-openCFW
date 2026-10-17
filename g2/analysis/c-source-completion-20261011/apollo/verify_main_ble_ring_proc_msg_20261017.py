#!/usr/bin/env python3
"""Compare C ring message, receive, CCCD and token entries with stock."""
import hashlib
import itertools
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2,
                               UC_ARM_REG_R3, UC_ARM_REG_LR, UC_ARM_REG_PC,
                               UC_ARM_REG_SP)

ROOT = Path(__file__).resolve().parents[4]
HERE = ROOT / 'g2/build/c-firmware/20261017/main-ble-ring-proc-msg'
SOURCE = ROOT / 'g2/components/audio/uart_thread_source_candidate/display_ble_ring_proc_msg_4c4910.c'
STOCK = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
STATE, HANDLES, MSG, DATA = 0x20074074, 0x20077000, 0x20077100, 0x20077200
CHILDREN = {
    'role': 0x4b73c4, 'in_use': 0x4b6ec6, 'write_req': 0x4b579c,
    'write_cmd': 0x539dea, 'remove': 0x476ace, 'push': 0x47697e,
    'ring_event': 0x4c543e, 'ring_rx': 0x4c548c,
    'tx_complete': 0x4d0c36, 'flags': 0x43d0ce,
    'extended': 0x43d574, 'compact': 0x43ce9e,
}
ENTRIES = {
    'token': (0x4c46c0, 'audio_ble_ring_cccd_epoch_token'),
    'enable': (0x4c46d0, 'audio_ble_ring_cccd_enable'),
    'receive': (0x4c48ac, 'audio_ble_ring_receive_data_4c48ac'),
    'message': (0x4c4910, 'audio_ble_master_message'),
}
REGS = (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def word(u, address):
    return struct.unpack('<I', u.mem_read(address, 4))[0]


def text_at(u, address):
    return bytes(u.mem_read(address, 200)).split(b'\0', 1)[0].decode(errors='replace')


def compile_candidate():
    HERE.mkdir(parents=True, exist_ok=True)
    bindings = {
        'DmConnRole': 'role', 'DmConnInUse': 'in_use',
        'audio_ble_attc_write_request': 'write_req',
        'audio_ble_attc_write_command_539dea': 'write_cmd',
        'audio_event_loop_remove_delayed': 'remove',
        'audio_event_loop_push_delayed': 'push',
        'Thread_SendEvtToRingTask': 'ring_event',
        'audio_uart_registry_child_4c548c': 'ring_rx',
        'audio_ble_tx_complete_notify': 'tx_complete',
        'audio_log_flags': 'flags', 'audio_log_extended': 'extended',
        'compressed_log_output': 'compact',
    }
    script = HERE / 'oracle.ld'
    definitions = ' '.join(f'{name} = {CHILDREN[kind] | 1:#x};'
                           for name, kind in bindings.items())
    script.write_text(f'audio_ble_ring_handler_state = {STATE:#x}; {definitions} '
                      'SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } '
                      '/DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
    elf = HERE / 'oracle.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                    '-mthumb', '-std=c11', '-O2', '-ffreestanding', '-fno-builtin',
                    '-nostdlib', '-Wl,-T,' + str(script), str(SOURCE), '-o', str(elf)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with elf.open('rb') as stream:
        image = ELFFile(stream)
        symbols = {s.name: s['st_value'] for s in image.get_section_by_name('.symtab').iter_symbols()}
        segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                    if s['p_type'] == 'PT_LOAD']
    return elf, symbols, segments


def run(native, kind, symbols, segments, raw, event, role, flags, active,
        epoch, in_use, handle, status, conn):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.mem_map(0x438000, (len(raw) + 4095) & ~4095)
    u.mem_write(0x438000, raw)
    u.mem_map(0x20000000, 0x80000)
    u.mem_map(0x100000, 0x10000)
    for address, data in segments:
        u.mem_write(address, data)
    u.mem_write(STATE, struct.pack('<BBHIH', active, 9, 0, HANDLES, epoch) + b'\0\0')
    u.mem_write(HANDLES, struct.pack('<HHH', handle, 0x12, 0x13))
    u.mem_write(DATA, b'\x11\x22\x33\x44')
    u.mem_write(MSG, struct.pack('<HBBIHH', conn, event, status, DATA, 4, 0x12))
    u.reg_write(UC_ARM_REG_SP, 0x2007e000)
    u.reg_write(UC_ARM_REG_LR, 0x2007f001)
    original, generated = ENTRIES[kind]
    args = ((conn, event & 1, epoch) if kind == 'token' else
            (((epoch << 16) | (event << 8) | conn,) if kind == 'enable' else
             ((MSG,) if kind == 'receive' else (9, MSG))))
    for register, value in zip(REGS, args):
        u.reg_write(register, value)
    trace = []
    by_address = {value: name for name, value in CHILDREN.items()}
    callback = 0x4c46d0 if native else symbols['audio_ble_ring_cccd_enable'] & ~1

    def normalize(pointer):
        return 'cccd_callback' if (pointer & ~1) == callback else hex(pointer)

    def code_hook(emu, address, size, user_data):
        child = by_address.get(address)
        if child is None:
            return
        args_now = [emu.reg_read(register) for register in REGS]
        if child == 'role':
            trace.append((child, args_now[0]))
            emu.reg_write(UC_ARM_REG_R0, role)
        elif child == 'in_use':
            trace.append((child, args_now[0]))
            emu.reg_write(UC_ARM_REG_R0, in_use)
        elif child == 'flags':
            emu.reg_write(UC_ARM_REG_R0, flags)
        elif child == 'remove':
            trace.append((child, normalize(args_now[0])))
            emu.reg_write(UC_ARM_REG_R0, 0)
        elif child == 'push':
            trace.append((child, normalize(args_now[0]), args_now[1], args_now[2]))
        elif child == 'write_req':
            trace.append((child, args_now[0], args_now[1], args_now[2],
                          bytes(emu.mem_read(args_now[3], args_now[2])).hex()))
        elif child == 'write_cmd':
            trace.append((child, args_now[0], args_now[1], args_now[2],
                          bytes(emu.mem_read(args_now[3], args_now[2])).hex()))
        elif child == 'ring_event':
            trace.append((child, args_now[0]))
        elif child == 'ring_rx':
            trace.append((child, args_now[0], args_now[1]))
        elif child == 'tx_complete':
            trace.append((child,))
        elif child == 'extended':
            sp = emu.reg_read(UC_ARM_REG_SP)
            trace.append((child, args_now[0], word(emu, sp),
                          text_at(emu, word(emu, sp + 4))))
        elif child == 'compact':
            trace.append((child, args_now[0], text_at(emu, args_now[1])))
        emu.reg_write(UC_ARM_REG_PC, emu.reg_read(UC_ARM_REG_LR))

    u.hook_add(UC_HOOK_CODE, code_hook)
    u.emu_start((original if native else symbols[generated]) | 1,
                0x2007f000, count=20000)
    assert u.reg_read(UC_ARM_REG_PC) == 0x2007f000
    return {'trace': trace, 'state': bytes(u.mem_read(STATE, 12)).hex(),
            'handles': bytes(u.mem_read(HANDLES, 6)).hex(),
            'result': u.reg_read(UC_ARM_REG_R0) if kind == 'token' else None}


def main():
    raw = STOCK.read_bytes()[32:]
    assert hashlib.sha256(raw).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
    elf, symbols, segments = compile_candidate()
    count = 0
    for kind in ENTRIES:
        events = ([0, 1, 2] if kind == 'token' else
                  [0, 1, 2] if kind == 'enable' else
                  [0, 1] if kind == 'receive' else
                  [5, 13, 14, 0x27, 0x28, 0xac, 0xff])
        for event, role, flags, active, in_use, handle, status, conn in itertools.product(
                events, [0, 1], [0, 1, 2, 4], [0, 1], [0, 1], [0, 0x10],
                [0, 1], [0, 1, 2]):
            params = (kind, symbols, segments, raw, event, role, flags,
                      active, 7, in_use, handle, status, conn)
            original = run(True, *params)
            candidate = run(False, *params)
            assert original == candidate, (params[0], event, role, flags,
                                           active, in_use, handle, status, conn,
                                           original, candidate)
            count += 1
    record = {'status': 'PASS_MAIN_BLE_RING_PROC_MSG_BOUNDED_STOCK_MATCH',
              'cases': count, 'source_sha256': sha(SOURCE),
              'oracle_elf_sha256': sha(elf),
              'stock_payload_sha256': hashlib.sha256(raw).hexdigest(),
              'stock_entries': {key: hex(value[0]) for key, value in ENTRIES.items()},
              'controlled_children': CHILDREN,
              'limits': ['ATT, event-loop, ring-task, logging and DM children are controlled.',
                         'No physical BLE link, final placement or device behavior is proven.'],
              'source_complete': False, 'flashable': False, 'hardware_proof': False}
    output = HERE / 'oracle.json'
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], count, sha(output))


if __name__ == '__main__':
    main()
