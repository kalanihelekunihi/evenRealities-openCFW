#!/usr/bin/env python3
"""Compare native device-privacy event forwarding to C with logging disabled."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_dev_priv_forward_4b2ea6.c'
UPSTREAM = ROOT / 'third-party/upstream/cordio/ble-host/sources/stack/dm/dm_dev.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-dev-priv-forward-4b2ea6'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = 'unsigned char audio_ble_dm_config[64];\n'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA or \
            'void dmDevPassEvtToDevPriv(uint8_t event' not in UPSTREAM.read_text():
        raise RuntimeError('Apollo payload or Cordio source changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,dmDevPassEvtToDevPriv', str(SOURCE), str(shim),
                        '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}
        def run(compiled, event, param, adv, connectable):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x100000)
            config = symbols['audio_ble_dm_config'] if compiled else 0x20000694
            cpu.mem_write(config + 4, (0x20005000).to_bytes(4, 'little'))
            cpu.mem_write(0x20005008, (0x20007001).to_bytes(4, 'little'))
            calls = []
            def hook(uc, addr, size, user):
                if addr == 0x4c9c50 and not compiled:
                    uc.reg_write(A.UC_ARM_REG_R0, 0)
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
                elif addr == 0x20007000:
                    ptr = uc.reg_read(A.UC_ARM_REG_R0)
                    data = bytes(uc.mem_read(ptr, 6))
                    calls.append((data[:3].hex(), data[4:6].hex()))
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            for reg, value in zip((A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                   A.UC_ARM_REG_R2, A.UC_ARM_REG_R3),
                                  (event, param, adv, connectable)):
                cpu.reg_write(reg, value)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = symbols['dmDevPassEvtToDevPriv'] if compiled else 0x4b2ea6
            cpu.emu_start(entry | 1, 0x600000, count=1500)
            return calls
        cases = 0
        for event in (0x0c, 0x0d, 0x7f):
            for param in (0, 1, 0xff):
                for adv in (0, 5):
                    for connectable in (0, 1):
                        stock = run(False, event, param, adv, connectable)
                        candidate = run(True, event, param, adv, connectable)
                        if stock != candidate:
                            raise RuntimeError(f'{event=} {param=} {adv=} {connectable=}: {stock} != {candidate}')
                        cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_DEV_PRIV_FORWARD_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'upstream_source': str(UPSTREAM.relative_to(ROOT)), 'upstream_sha256': sha(UPSTREAM),
               'payload_sha256': PINNED_SHA, 'cases': cases,
               'comparison_scope': 'Logging-disabled native DM device-privacy event forwarding, callback slot and five initialized event bytes.',
               'limits': ['Native logging branches and uninitialized event status byte are excluded; final placement and hardware behavior remain open.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases, sha(path))

if __name__ == '__main__': main()
