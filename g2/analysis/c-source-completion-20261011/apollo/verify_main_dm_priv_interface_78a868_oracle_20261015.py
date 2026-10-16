#!/usr/bin/env python3
"""Compare pinned Cordio primary privacy dispatch and bounded C effects."""
import hashlib
import json
import struct
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_priv_interface_78a868.c'
UPSTREAM = ROOT / 'third-party/upstream/cordio/ble-host/sources/stack/dm/dm_priv.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-priv-interface-78a868'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SLOTS = [('audio_ble_dm_priv_reset_4d27c0', 0x4d27c1),
         ('audio_ble_dm_priv_hci_handler_4d26e8', 0x4d26e9),
         ('audio_ble_dm_priv_msg_handler_4d27ae', 0x4d27af)]
ACTIONS = [('resolve_addr', 0x4d254d), ('add_device', 0x4d25f3),
           ('remove_device', 0x4d2617), ('clear_list', 0x4d262d),
           ('set_enable', 0x4d2635), ('set_privacy_mode', 0x4d263f),
           ('generate_addr', 0x4d264d)]
SHIM = '''#include <stddef.h>
#include <stdint.h>
uint8_t audio_ble_dm_priv_cb_storage[26];
uint8_t audio_ble_dm_handler_state[24];
__attribute__((noinline)) void *memcpy(void*x,const void*y,size_t n){(void)y;(void)n;return x;}
__attribute__((noinline)) void *memset(void*x,int c,size_t n){(void)c;(void)n;return x;}
__attribute__((noinline)) uint8_t SecAes(uint8_t*a,uint8_t*b,uint8_t c,uint16_t d,uint8_t e){(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}
__attribute__((noinline)) void SecRand(uint8_t*a,uint8_t b){(void)a;(void)b;}
__attribute__((noinline)) void HciLeAddDeviceToResolvingListCmd(uint8_t a,const uint8_t*b,const uint8_t*c,const uint8_t*d){(void)a;(void)b;(void)c;(void)d;}
__attribute__((noinline)) void HciLeRemoveDeviceFromResolvingList(uint8_t a,const uint8_t*b){(void)a;(void)b;}
__attribute__((noinline)) void HciLeClearResolvingList(void){}
__attribute__((noinline)) void HciLeSetAddrResolutionEnable(uint8_t a){(void)a;}
__attribute__((noinline)) void HciLeSetPrivacyModeCmd(uint8_t a,uint8_t*b,uint8_t c){(void)a;(void)b;(void)c;}
__attribute__((noinline)) void dmDevPassEvtToDevPriv(uint8_t a,uint8_t b,uint8_t c,uint8_t d){(void)a;(void)b;(void)c;(void)d;}
'''
TARGETS = {
    'memcpy': ('memcpy', 0x439be4), 'memset': ('memset', 0x43c0e4),
    'aes': ('SecAes', 0x536426), 'rand': ('SecRand', 0x53634e),
    'add': ('HciLeAddDeviceToResolvingListCmd', 0x52b744),
    'remove': ('HciLeRemoveDeviceFromResolvingList', 0x52b794),
    'clear': ('HciLeClearResolvingList', 0x52b7c2),
    'enable': ('HciLeSetAddrResolutionEnable', 0x52b7f6),
    'mode': ('HciLeSetPrivacyModeCmd', 0x52b818),
    'dev': ('dmDevPassEvtToDevPriv', 0x4b2ea6),
}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA or \
            'void dmPrivHciHandler(hciEvt_t *pEvent)' not in UPSTREAM.read_text():
        raise RuntimeError('Apollo payload or Cordio source changed')
    stock_table = struct.unpack_from('<III', blob, 0x78a868-0x438000)
    stock_actions = struct.unpack_from('<7I', blob, 0x76af6c-0x438000)
    if stock_table != tuple(x for _, x in SLOTS) or \
            stock_actions != tuple(x for _, x in ACTIONS):
        raise RuntimeError('native primary privacy pointers changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_dm_priv_msg_handler_4d27ae',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}
        def read_elf(address, size):
            for base, data in segments:
                if base <= address and address + size <= base + len(data):
                    return data[address-base:address-base+size]
            raise RuntimeError('table not in load segments')
        if struct.unpack('<III', read_elf(symbols['audio_ble_dm_priv_table_a'], 12)) != \
                tuple(symbols[name] for name, _ in SLOTS) or \
                struct.unpack('<7I', read_elf(symbols['audio_ble_dm_priv_actions'], 28)) != \
                tuple(symbols[name] for name, _ in ACTIONS):
            raise RuntimeError('C primary privacy pointers changed')

        def run(compiled, family, kind, status, busy, seed):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x100000)
            state = symbols['audio_ble_dm_priv_cb_storage'] if compiled else 0x20073a58
            dm = symbols['audio_ble_dm_handler_state'] if compiled else 0x20073b78
            cb = bytearray((seed + i * 5) & 0xff for i in range(26))
            cb[3] = 3 if busy else 0
            cb[8] = 1
            cb[9] = 1
            cpu.mem_write(state, bytes(cb))
            dm_data = bytearray((seed + i * 7) & 0xff for i in range(24))
            dm_data[8:12] = (0x20007001).to_bytes(4, 'little')
            dm_data[12] = 4
            dm_data[22] = 0
            cpu.mem_write(dm, bytes(dm_data))
            message = bytearray((seed + i * 3) & 0xff for i in range(48))
            message[0:2] = (0x1234).to_bytes(2, 'little')
            message[2] = kind
            message[3] = status
            cpu.mem_write(0x20001000, bytes(message))
            lookup = {((symbols[name] if compiled else native) & ~1): action
                      for action, (name, native) in TARGETS.items()}
            calls = []
            def hook(uc, addr, size, user):
                if addr == 0x20007000:
                    ptr = uc.reg_read(A.UC_ARM_REG_R0)
                    calls.append(('callback', bytes(uc.mem_read(ptr, 48)).hex()))
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
                    return
                action = lookup.get(addr)
                if action is None:
                    return
                r = [uc.reg_read(getattr(A, f'UC_ARM_REG_R{i}')) for i in range(4)]
                if action == 'memcpy':
                    n = r[2]
                    data = bytes(uc.mem_read(r[1], n))
                    calls.append(('memcpy', data.hex()))
                    uc.mem_write(r[0], data)
                elif action == 'memset':
                    fill, n = (r[1] & 0xff, r[2]) if compiled else (r[2] & 0xff, r[1])
                    calls.append(('memset', fill, n))
                    uc.mem_write(r[0], bytes([fill]) * n)
                elif action == 'aes':
                    event = int.from_bytes(uc.mem_read(uc.reg_read(A.UC_ARM_REG_SP), 4), 'little') & 0xff
                    calls.append(('aes', bytes(uc.mem_read(r[0], 16)).hex(),
                                  bytes(uc.mem_read(r[1], 16)).hex(), r[2] & 0xff,
                                  r[3] & 0xffff, event))
                    uc.reg_write(A.UC_ARM_REG_R0, 1)
                elif action == 'rand':
                    calls.append(('rand', r[1] & 0xff))
                    uc.mem_write(r[0], b'\x12\x34\x56')
                elif action == 'add':
                    calls.append(('add', r[0] & 0xff, bytes(uc.mem_read(r[1], 6)).hex(),
                                  bytes(uc.mem_read(r[2], 16)).hex(), bytes(uc.mem_read(r[3], 16)).hex()))
                elif action == 'remove':
                    calls.append(('remove', r[0] & 0xff, bytes(uc.mem_read(r[1], 6)).hex()))
                elif action == 'clear': calls.append(('clear',))
                elif action == 'enable': calls.append(('enable', r[0] & 0xff))
                elif action == 'mode':
                    calls.append(('mode', r[0] & 0xff, bytes(uc.mem_read(r[1], 6)).hex(), r[2] & 0xff))
                elif action == 'dev': calls.append(('dev', *(x & 0xff for x in r)))
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, 0x20001000)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry_name = {'message': 'audio_ble_dm_priv_msg_handler_4d27ae',
                          'hci': 'audio_ble_dm_priv_hci_handler_4d26e8',
                          'reset': 'audio_ble_dm_priv_reset_4d27c0'}[family]
            entry_native = {'message': 0x4d27ae, 'hci': 0x4d26e8, 'reset': 0x4d27c0}[family]
            entry = symbols[entry_name] if compiled else entry_native
            cpu.emu_start(entry | 1, 0x600000, count=1500)
            return calls, bytes(cpu.mem_read(0x20001000, 48)), \
                bytes(cpu.mem_read(state, 26)), bytes(cpu.mem_read(dm, 24))

        cases = 0
        for family, kinds in [('message', tuple(range(7))),
                              ('hci', tuple(range(0x15, 0x1b))), ('reset', (0,))]:
            for kind in kinds:
                for busy in (False, True):
                    for status in ((0, 1) if family == 'hci' else (0,)):
                        for seed in (0, 0xa5):
                            stock = run(False, family, kind, status, busy, seed)
                            candidate = run(True, family, kind, status, busy, seed)
                            if stock != candidate:
                                raise RuntimeError(f'{family=} {kind=} {status=} {busy=} {seed=}: {stock} != {candidate}')
                            cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_PRIV_INTERFACE_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'upstream_source': str(UPSTREAM.relative_to(ROOT)), 'upstream_sha256': sha(UPSTREAM),
               'payload_sha256': PINNED_SHA, 'native_slots': [hex(x) for x in stock_table],
               'native_actions': [hex(x) for x in stock_actions], 'cases': cases,
               'comparison_scope': 'Three primary privacy interface slots, seven action slots, reset, HCI status routing, command arguments and bounded 26-byte state/message effects.',
               'limits': ['Only valid privacy action indices zero through six are compared; HCI child effects, final placement and hardware behavior remain open.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases, sha(path))

if __name__ == '__main__': main()
