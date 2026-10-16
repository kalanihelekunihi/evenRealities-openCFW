#!/usr/bin/env python3
"""Compare compiled Cordio privacy event constructor with Apollo native."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_dev_pass_priv_4b2ea6.c'
UPSTREAM = ROOT / 'third-party/upstream/cordio/ble-host/sources/stack/dm/dm_dev.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-dev-pass-priv-4b2ea6'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = '''#include <stdint.h>
uint8_t audio_ble_dm_config[0x80];
__attribute__((noinline)) uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void){return 0;}
__attribute__((noinline)) int32_t audio_ble_hci_vendor_compare_44b610(const void*a,const void*b,uint32_t n){(void)a;(void)b;(void)n;return 0;}
__attribute__((noinline)) uint32_t audio_log_flags(void){return 0;}
__attribute__((noinline)) void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
__attribute__((noinline)) void audio_ble_hci_wsf_trace(const char*a,const char*b,...){(void)a;(void)b;}
'''

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA:
        raise RuntimeError('Apollo payload changed')
    upstream = UPSTREAM.read_text()
    start = upstream.index('void dmDevPassEvtToDevPriv(')
    end = upstream.index('\n}', start)
    body = upstream[start:end]
    for term in ('evt.hdr.event = event', 'evt.hdr.param = param',
                 'evt.privCtrl.advHandle = advHandle',
                 'evt.privCtrl.connectable = connectable'):
        if term not in body:
            raise RuntimeError('Cordio privacy constructor source changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_dm_dev_pass_priv_4b2ea6',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}

        def run(compiled, event, param, adv, connectable, vendor, flags):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x200000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x100000)
            config = symbols['audio_ble_dm_config'] if compiled else 0x20000694
            cpu.mem_write(config + 4, (0x20004000).to_bytes(4, 'little'))
            cpu.mem_write(0x20004008, (0x2000a001).to_bytes(4, 'little'))
            cpu.mem_write(0x200fe000, bytes((0xa5,) * 0x1000))
            calls = []
            observed_status = []
            def string(addr):
                return bytes(cpu.mem_read(addr, 200)).split(b'\0', 1)[0].decode('ascii', 'replace')
            addresses = {
                (symbols['audio_ble_hci_vendor_log_enabled_4c9c50'] & ~1) if compiled else 0x4c9c50: 'vendor',
                (symbols['audio_ble_hci_vendor_compare_44b610'] & ~1) if compiled else 0x44b610: 'compare',
                (symbols['audio_log_flags'] & ~1) if compiled else 0x43d0ce: 'flags',
                (symbols['audio_log_extended'] & ~1) if compiled else 0x43d574: 'extended',
                (symbols['audio_ble_hci_wsf_trace'] & ~1) if compiled else 0x52a63c: 'wsf',
                0x2000a000: 'privacy_callback',
            }
            def hook(uc, address, size, user):
                kind = addresses.get(address)
                if kind is None:
                    return
                sp = uc.reg_read(A.UC_ARM_REG_SP)
                if kind == 'vendor':
                    uc.reg_write(A.UC_ARM_REG_R0, vendor)
                elif kind == 'compare':
                    left = string(uc.reg_read(A.UC_ARM_REG_R0))
                    right = string(uc.reg_read(A.UC_ARM_REG_R1))
                    length = uc.reg_read(A.UC_ARM_REG_R2)
                    uc.reg_write(A.UC_ARM_REG_R0, 0 if left[:length] == right[:length] else 1)
                elif kind == 'flags':
                    uc.reg_write(A.UC_ARM_REG_R0, flags)
                elif kind == 'wsf':
                    fmt = string(uc.reg_read(A.UC_ARM_REG_R1))
                    calls.append(('wsf', string(uc.reg_read(A.UC_ARM_REG_R0)), fmt,
                                  uc.reg_read(A.UC_ARM_REG_R2) & 0xff,
                                  uc.reg_read(A.UC_ARM_REG_R3) & 0xff,
                                  int.from_bytes(uc.mem_read(sp, 4), 'little') & 0xff))
                elif kind == 'extended':
                    fmt = string(int.from_bytes(uc.mem_read(sp + 4, 4), 'little'))
                    calls.append(('extended', uc.reg_read(A.UC_ARM_REG_R0) & 0xff,
                                  string(uc.reg_read(A.UC_ARM_REG_R1)),
                                  string(uc.reg_read(A.UC_ARM_REG_R2)),
                                  string(uc.reg_read(A.UC_ARM_REG_R3)),
                                  int.from_bytes(uc.mem_read(sp, 4), 'little'),
                                  fmt,
                                  *(int.from_bytes(uc.mem_read(sp + x, 4), 'little') & 0xff
                                    for x in (8, 12, 16))))
                else:
                    raw = bytes(uc.mem_read(uc.reg_read(A.UC_ARM_REG_R0), 6))
                    observed_status.append(raw[3])
                    calls.append(('privacy_callback', raw[:3] + raw[4:]))
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, event)
            cpu.reg_write(A.UC_ARM_REG_R1, param)
            cpu.reg_write(A.UC_ARM_REG_R2, adv)
            cpu.reg_write(A.UC_ARM_REG_R3, connectable)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = symbols['audio_ble_dm_dev_pass_priv_4b2ea6'] if compiled else 0x4b2ea6
            cpu.emu_start(entry | 1, 0x600000, count=15000)
            return calls, observed_status, bytes(cpu.mem_read(config + 4, 4))

        cases = 0
        stock_statuses = set()
        candidate_statuses = set()
        for event in (0, 0x0d, 0xff):
            for param in (0, 0x28, 0xff):
                for adv in (0, 1, 0xff):
                    for connectable in (0, 1):
                        for vendor, flags in ((0, 0), (1, 0), (1, 2)):
                            stock = run(False, event, param, adv, connectable, vendor, flags)
                            candidate = run(True, event, param, adv, connectable, vendor, flags)
                            stock_statuses.update(stock[1])
                            candidate_statuses.update(candidate[1])
                            if stock[0] != candidate[0] or stock[2] != candidate[2]:
                                raise RuntimeError(f'{event=} {param=} {adv=} {connectable=} {vendor=} {flags=}: {stock} != {candidate}')
                            cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_DEV_PASS_PRIV_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'upstream_source': str(UPSTREAM.relative_to(ROOT)),
               'upstream_sha256': sha(UPSTREAM), 'payload_sha256': PINNED_SHA,
               'cases': cases, 'observed_stock_unwritten_status_values': sorted(stock_statuses),
               'observed_compiled_unwritten_status_values': sorted(candidate_statuses),
               'comparison_scope': 'Native logger calls, five assigned record bytes, callback dispatch and DM configuration preservation.',
               'limits': ['WSF hdr.status is unwritten by stock and upstream constructor; its value is excluded from equality and remains an explicit runtime gate.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
