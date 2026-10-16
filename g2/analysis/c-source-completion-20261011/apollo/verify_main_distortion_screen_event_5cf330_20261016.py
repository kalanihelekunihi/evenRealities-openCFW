#!/usr/bin/env python3
"""Compare stock distortion-screen callback with its C body under page-call controls."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SRC = G2 / 'components/audio/uart_thread_source_candidate/distortion_screen_event_5cf330.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261016/main-distortion-screen-event-5cf330'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
ADDRS = [
    0x43de82, 0x43dfa4, 0x43f09a, 0x43f4c0, 0x43f506, 0x43f568,
    0x43ded4, 0x43f6b8, 0x44104c, 0x44120e, 0x44121c, 0x44122a,
    0x441238, 0x441246, 0x441254, 0x44127e, 0x44129e, 0x4412ec,
    0x44130c, 0x44131c, 0x44133a, 0x441378, 0x441386, 0x441394,
    0x4413a2, 0x4413b0, 0x44140e, 0x44142e, 0x44143e, 0x44145a,
    0x44146a, 0x48ba78, 0x48ba92, 0x498668, 0x498680, 0x499416,
    0x49942e, 0x460084, 0x45fffe,
]
RETURNS = {0x43de82, 0x44104c, 0x498668, 0x499416, 0x460084, 0x45fffe}
DATA = {
    'audio_uart_distortion_asset_769f58': 0x769f58,
    'audio_uart_distortion_text_736af4': 0x736af4,
    'audio_uart_distortion_text_736b24': 0x736b24,
    'audio_uart_ring_primary_head_cell': 0x200746dc,
    'audio_uart_distortion_root_2007487c': 0x2007487c,
    'audio_uart_registry_context_20003064': 0x20003064,
}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def build():
    OUT.mkdir(parents=True, exist_ok=True)
    obj, elf = OUT / 'distortion-screen.o', OUT / 'distortion-screen-oracle.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SRC), '-o', str(obj)], check=True)
    names = {f'audio_uart_page_{a:x}': a | 1 for a in ADDRS}
    names.update(DATA)
    defs = [f'--defsym={name}=0x{addr:x}' for name, addr in sorted(names.items())]
    subprocess.run(['arm-none-eabi-ld', '-Ttext=0x100000', *defs,
                    str(obj), '-o', str(elf)], check=True, stderr=subprocess.DEVNULL)
    with elf.open('rb') as f:
        e = ELFFile(f)
        segs = [(s['p_vaddr'], s.data()) for s in e.iter_segments() if s['p_type'] == 'PT_LOAD']
        sym = {s.name: s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    return obj, elf, segs, sym['audio_uart_registry_callback_5cf330']

def execute(stock, segments, source_entry, event, seed):
    image = PAYLOAD.read_bytes()[32:]
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000, (len(image) + 4095) & ~4095)
    u.mem_write(0x438000, image)
    u.mem_map(0x100000, 0x40000)
    if not stock:
        for address, data in segments: u.mem_write(address, data)
    u.mem_map(0x20000000, 0x100000)
    u.mem_write(0x200746dc, (seed * 0x10101).to_bytes(4, 'little'))
    u.mem_write(0x2007487c, (0x78563412 ^ seed).to_bytes(4, 'little'))
    u.mem_write(0x20003068, (0xabcdef01 ^ seed).to_bytes(4, 'little'))
    u.reg_write(A.UC_ARM_REG_R0, event)
    u.reg_write(A.UC_ARM_REG_R1, 0x80001234 | seed)
    u.reg_write(A.UC_ARM_REG_R2, 0x23000000 | seed)
    u.reg_write(A.UC_ARM_REG_R3, 0x20004000 + seed * 4)
    u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
    u.reg_write(A.UC_ARM_REG_LR, 0x101181)
    calls, visited, done = [], set(), [False]
    hooks = set(ADDRS)
    def code(uc, pc, _size, _unused):
        if pc == 0x101180:
            done[0] = True; uc.emu_stop(); return
        if pc in hooks:
            args = tuple(uc.reg_read(r) for r in (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                                   A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            calls.append((pc, args))
            if pc in RETURNS:
                uc.reg_write(A.UC_ARM_REG_R0, (0x20050000 + 0x40 * len(calls) + seed) & 0xffffffff)
            uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
        elif 0x5cf330 <= pc < 0x5cf61c if stock else 0x100000 <= pc < 0x101180:
            visited.add(pc)
    u.hook_add(UC_HOOK_CODE, code)
    u.emu_start((0x5cf330 if stock else source_entry) | 1, 0, count=10000)
    if not done[0]: raise RuntimeError('callback did not return')
    return {'calls': calls,
            'r0': u.reg_read(A.UC_ARM_REG_R0),
            'root': u.mem_read(0x2007487c, 4).hex(),
            'registry_root': u.mem_read(0x20003068, 4).hex()}, visited

def main():
    image = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(image).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError('stock payload changed')
    obj, elf, segments, entry = build()
    visited, total_calls, count = set(), 0, 0
    for event in (0, 1, 2, 3, 4, 5, 0xffffffff):
        for seed in (0, 1, 7, 19):
            a, va = execute(True, segments, entry, event, seed)
            b, _ = execute(False, segments, entry, event, seed)
            if a != b:
                for i, (x, y) in enumerate(zip(a['calls'], b['calls'])):
                    if x != y:
                        raise RuntimeError(f'mismatch event={event} seed={seed} call={i}: {x} vs {y}')
                raise RuntimeError(f'mismatch event={event} seed={seed} calls={len(a["calls"])}:{len(b["calls"])} state={a["r0"],a["root"],a["registry_root"]} vs {b["r0"],b["root"],b["registry_root"]}')
            visited |= va
            total_calls += len(a['calls'])
            count += 1
    receipt = {'status': 'PASS_NATIVE_MAIN_DISTORTION_SCREEN_EVENT_5CF330',
               'cases': count, 'controlled_lower_calls': total_calls,
               'visited_stock_instruction_addresses': len(visited),
               'source': str(SRC.relative_to(ROOT)), 'source_sha256': sha(SRC),
               'official_payload_sha256': PAYLOAD_SHA,
               'object': str(obj.relative_to(ROOT)), 'object_sha256': sha(obj),
               'comparison_elf': str(elf.relative_to(ROOT)), 'comparison_elf_sha256': sha(elf),
               'limits': ['All lower page and string calls are controlled; asset bytes, RAM allocation extent, final link placement and hardware behavior are not proved.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], count, len(visited), sha(path))

if __name__ == '__main__': main()
