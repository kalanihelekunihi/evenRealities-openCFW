#!/usr/bin/env python3
"""Compare native and compiled eight-way DM message dispatch at child entry."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_stack_msg_handler_5369d8.c'
TABLE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_stack_interface_78a88c.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-stack-msg-handler-5369d8'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
NAMES = ['audio_ble_dm_dispatch_536820', 'audio_ble_dm_dispatch_536896',
         'audio_ble_dm_dispatch_5368ae', 'audio_ble_dm_stack_reset_536918',
         'audio_ble_dm_stack_hci_handler_53694c',
         'audio_ble_dm_stack_msg_handler_5369d8',
         'audio_ble_dm_dispatch_4d2544', 'audio_ble_dm_dispatch_4d2364']
STOCK = [0x536820, 0x536896, 0x5368ae, 0x536918,
         0x53694c, 0x5369d8, 0x4d2544, 0x4d2364]
SHIM = '#include <stdint.h>\n'
for name in NAMES:
    if name != 'audio_ble_dm_stack_msg_handler_5369d8':
        SHIM += f'__attribute__((noinline)) void {name}(void*p){{(void)p;}}\n'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA:
        raise RuntimeError('Apollo payload changed')
    offset = 0x78a880 - 0x438000
    pointers = [int.from_bytes(blob[offset+i*4:offset+i*4+4], 'little') for i in range(8)]
    if pointers != [addr | 1 for addr in STOCK]:
        raise RuntimeError('native DM dispatch pointer slots changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_dm_stack_msg_handler_5369d8',
                        str(SOURCE), str(TABLE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}

        def run(compiled, event, seed):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x10000)
            msg = bytearray((seed + i * 7) & 0xff for i in range(32))
            msg[2] = event
            cpu.mem_write(0x20001000, bytes(msg))
            targets = {(symbols[name] & ~1) if compiled else stock: index
                       for index, (name, stock) in enumerate(zip(NAMES, STOCK))}
            root = (symbols[NAMES[5]] & ~1) if compiled else STOCK[5]
            first_entry = True
            calls = []
            def hook(uc, addr, size, user):
                nonlocal first_entry
                if addr == root and first_entry:
                    first_entry = False
                    return
                if addr in targets:
                    calls.append((targets[addr], uc.reg_read(A.UC_ARM_REG_R0)))
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, 0x20001000)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x2000ff00)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.emu_start(root | 1, 0x600000, count=1000)
            return calls, bytes(cpu.mem_read(0x20001000, 32))

        cases = 0
        for event in (*range(8), *range(0xf8, 0x100)):
            for seed in (0, 0x55, 0xa5):
                stock = run(False, event, seed)
                candidate = run(True, event, seed)
                if stock != candidate:
                    raise RuntimeError(f'{event=} {seed=}: {stock} != {candidate}')
                cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_STACK_MSG_HANDLER_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'table_source': str(TABLE.relative_to(ROOT)),
               'table_source_sha256': sha(TABLE),
               'payload_sha256': PINNED_SHA, 'cases': cases,
               'comparison_scope': 'Native eight-way dispatch target, forwarded message pointer and preserved message at child entry.',
               'limits': ['Child effects are cut at their entries; event index five self-dispatches and is compared only at the first child call.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
