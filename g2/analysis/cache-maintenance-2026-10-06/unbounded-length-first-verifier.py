#!/usr/bin/env python3
"""Stock/source/model cache register ordering; physical cache effects unmodeled."""
import argparse
import hashlib
import importlib.util
import json
import struct
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
BASE, H, SP, STOP = 0x438000, 0x20001000, 0x2000f000, 0x8000000
CCR, SELECT, SIZE = 0xe000ed14, 0xe000ed84, 0xe000ed80
spec = importlib.util.spec_from_file_location('elf_reader', ROOT / 'g2/components/foundation/touch_scb/simulator/verify.py')
elf_reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(elf_reader)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def positive(value):
    return value != 0 and value < 0x80000000


def model(c):
    events = [['read', CCR, c['ccr']]]
    if not c['ccr'] & 0x10000:
        return events + [['dsb'], ['isb']]
    if c['null']:
        operation = 0xe000ef6c if c['clean'] else (0xe000ef74 if c['flag'] & 255 else 0xe000ef60)
        events += [['write', SELECT, 0], ['dsb'], ['read', SIZE, c['size']]]
        for set_number in range(((c['size'] >> 13) & 0x7fff), -1, -1):
            for way in range(((c['size'] >> 3) & 0x3ff), -1, -1):
                events.append(['write', operation, ((set_number << 5) & 0x3fe0) | ((way << 30) & 0xffffffff)])
        return events + [['dsb'], ['isb']]
    events += [['read', H + 4, c['length']], ['read', H, c['address']]]
    if not positive(c['length']):
        return events
    operation = 0xe000ef68 if c['clean'] else (0xe000ef70 if c['flag'] & 255 else 0xe000ef5c)
    events.append(['dsb'])
    remaining, address = (c['length'] + (c['address'] & 31)) & 0xffffffff, c['address']
    while True:
        events.append(['write', operation, address])
        address, remaining = (address + 32) & 0xffffffff, (remaining - 32) & 0xffffffff
        if not positive(remaining):
            break
        assert len(events) < 10000
    return events + [['dsb'], ['isb']]


def run(segments, entry, c):
    import unicorn as u
    import unicorn.arm_const as a
    cpu = u.Uc(u.UC_ARCH_ARM, u.UC_MODE_THUMB | u.UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M4)
    pages = set()
    for seg in segments:
        for p in range(seg['address'] & ~4095, (seg['address'] + seg['memory_size'] + 4095) & ~4095, 4096):
            if p not in pages:
                cpu.mem_map(p, 4096); pages.add(p)
        cpu.mem_write(seg['address'], seg['data'])
    for start, count in [(0x20000000, 0x10000), (0xe000e000, 8192), (STOP, 4096)]:
        cpu.mem_map(start, count)
    cpu.mem_write(H - 8, b'\xcc' * 8 + struct.pack('<II', c['address'], c['length']) + b'\xcc' * 8)
    for address, value in [(CCR, c['ccr']), (SIZE, c['size']), (SELECT, 0xdeadbeef)]:
        cpu.mem_write(address, struct.pack('<I', value))
    for reg, value in [(a.UC_ARM_REG_R0, 0 if c['null'] else H), (a.UC_ARM_REG_R1, c['flag']),
                       (a.UC_ARM_REG_SP, SP), (a.UC_ARM_REG_LR, STOP | 1), (a.UC_ARM_REG_PRIMASK, c['prior'])]:
        cpu.reg_write(reg, value)
    saved = {getattr(a, 'UC_ARM_REG_R' + str(i)): 0xabba0000 + i for i in range(4, 12)}
    for reg, value in saved.items():
        cpu.reg_write(reg, value)
    events, trace = [], {}
    def code(uc, pc, size, _):
        if pc == STOP:
            uc.emu_stop(); return
        seg = next((s for s in segments if s['flags'] & 1 and s['address'] <= pc and pc + size <= s['address'] + len(s['data'])), None)
        assert seg is not None, hex(pc)
        raw = bytes(uc.mem_read(pc, size))
        assert raw == seg['data'][pc - seg['address']:pc - seg['address'] + size]
        trace[hex(pc)] = raw.hex()
        if raw == bytes.fromhex('bff34f8f'):
            events.append(['dsb'])
        if raw == bytes.fromhex('bff36f8f'):
            events.append(['isb'])
    def memory(uc, access, address, size, value, _):
        if 0xe000e000 <= address < 0xe0010000 or H <= address < H + 8:
            assert size == 4
            value = struct.unpack('<I', uc.mem_read(address, 4))[0] if access == u.UC_MEM_READ else value & 0xffffffff
            events.append(['read' if access == u.UC_MEM_READ else 'write', address, value])
            if H <= address < H + 8:
                assert access == u.UC_MEM_READ
    cpu.hook_add(u.UC_HOOK_CODE, code)
    cpu.hook_add(u.UC_HOOK_MEM_READ | u.UC_HOOK_MEM_WRITE, memory)
    cpu.emu_start(entry | 1, STOP, count=30000)
    assert cpu.reg_read(a.UC_ARM_REG_PC) == STOP
    assert cpu.reg_read(a.UC_ARM_REG_SP) == SP
    assert cpu.reg_read(a.UC_ARM_REG_PRIMASK) == c['prior']
    assert all(cpu.reg_read(reg) == value for reg, value in saved.items())
    assert bytes(cpu.mem_read(H - 8, 24)) == b'\xcc' * 8 + struct.pack('<II', c['address'], c['length']) + b'\xcc' * 8
    return {'status': cpu.reg_read(a.UC_ARM_REG_R0), 'events': events, 'trace': trace}


def cases():
    default = {'ccr': 0x10000, 'size': 0, 'address': 0x20008000, 'length': 1, 'flag': 0, 'null': False, 'prior': 0}
    for clean in (False, True):
        for flag in (0, 1, 2, 255, 256, 257):
            for prior in (0, 1):
                for null in (False, True):
                    for ccr in (0, 0x8000, 0x20000):
                        yield dict(default, clean=clean, flag=flag, prior=prior, null=null, ccr=ccr)
                for sets, ways in [(0, 0), (1, 1), (2, 3), (3, 0), (127, 3), (512, 0), (0, 7)]:
                    yield dict(default, clean=clean, flag=flag, prior=prior, null=True, size=(sets << 13) | (ways << 3) | 2)
        for flag in (0, 1, 256):
            for align in (0, 1, 15, 16, 30, 31):
                for length in (0, 1, 2, 31, 32, 33, 63, 64, 65, 3200, 0x80000000, 0xffffffff):
                    yield dict(default, clean=clean, flag=flag, address=0x20008000 + align, length=length)
            for align in (0, 1, 15, 31):
                yield dict(default, clean=clean, flag=flag, address=0xfffffff0 + align if align < 16 else 0xffffffff, length=64)
                # Signed addition wraps negative; do-while still emits the first address.
                if align:
                    yield dict(default, clean=clean, flag=flag, address=0x20008000 + align, length=0x7fffffff)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--elf', type=Path, required=True); ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    firmware = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
    assert sha(firmware) == '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
    raw = firmware.read_bytes()[32:]
    stock = [dict(address=0x475000, memory_size=4096, data=raw[0x475000 - BASE:0x476000 - BASE], flags=5)]
    _, segments, syms = elf_reader.elf_info(args.elf)
    results, trace = [], {}
    for c in cases():
        original = run(stock, 0x47510e if c['clean'] else 0x475014, c)
        source = run(segments, syms['opencfw_cache_clean' if c['clean'] else 'opencfw_cache_invalidate'] & ~1, c)
        observed = original.pop('trace'); source.pop('trace')
        assert original == source == {'status': 0, 'events': model(c)}, (c, original, source, model(c))
        for pc, value in observed.items():
            assert pc not in trace or trace[pc] == value
            trace[pc] = value
        results.append({'inputs': c, 'result': original})
    used = {int(pc, 0) + i for pc, value in trace.items() for i in range(len(bytes.fromhex(value)))}
    result = {'status': 'PASS', 'cases': len(results), 'results': results, 'original_trace': trace,
              'unique_original_trace_bytes': len(used), 'firmware_sha256': sha(firmware), 'elf_sha256': sha(args.elf),
              'source_manifest': {str(p.relative_to(ROOT)): sha(p) for p in Path(__file__).parent.iterdir() if p.suffix in ('.c', '.h', '.py')},
              'limits': 'Both original functions return with ABI preserved; source/model/stock ordered register/descriptor reads, maintenance writes and DSB/ISB agree. No executable callee stubs; raw SCB register fixtures only. No actual cache-line effect, DMA coherence, physical ownership or complete bus/caller proof. Synthetic CCSIDR geometry includes truncation probes; no live-device geometry asserted. Optimized tick blocker remains separate.'}
    with args.output.open('x') as f: json.dump(result, f, indent=2); f.write('\n')
    print('PASS', len(results), len(used))


if __name__ == '__main__': main()
