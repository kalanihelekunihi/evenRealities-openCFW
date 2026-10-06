#!/usr/bin/env python3
"""Actual stock lookup/copy and IOM selection prefix versus reconstructed C."""
import argparse
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = 0x438000
FIRMWARE = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
EXPECTED_SHA = '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
OUT, HANDLE, SP, STOP = 0x20001000, 0x20002000, 0x2000f000, 0x8000000
spec = importlib.util.spec_from_file_location('elf_reader', ROOT / 'g2/components/foundation/touch_scb/simulator/verify.py')
elf_reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(elf_reader)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(segments, entry, value, null=False, prior=0, consumer=False, original=False):
    import unicorn as u
    import unicorn.arm_const as a
    cpu = u.Uc(u.UC_ARCH_ARM, u.UC_MODE_THUMB | u.UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M4)
    pages = set()
    for seg in segments:
        for page in range(seg['address'] & ~4095, (seg['address'] + seg['memory_size'] + 4095) & ~4095, 4096):
            if page not in pages:
                cpu.mem_map(page, 4096)
                pages.add(page)
        cpu.mem_write(seg['address'], seg['data'])
    cpu.mem_map(0x20000000, 0x10000)
    cpu.mem_map(STOP, 4096)
    cpu.mem_write(OUT - 8, b'\xcc' * 8 + b'\xa5' * 16 + b'\xcc' * 8)
    cpu.mem_write(HANDLE, struct.pack('<II', 0, value))
    cpu.mem_write(SP - 64, b'\xa5' * 64)
    for reg, val in [(a.UC_ARM_REG_R0, 0 if null else OUT), (a.UC_ARM_REG_R1, value),
                     (a.UC_ARM_REG_SP, SP), (a.UC_ARM_REG_LR, STOP | 1), (a.UC_ARM_REG_PRIMASK, prior)]:
        cpu.reg_write(reg, val)
    saved = {getattr(a, 'UC_ARM_REG_R' + str(i)): 0xabba0000 + i for i in range(4, 12)}
    for reg, val in saved.items():
        cpu.reg_write(reg, val)
    if consumer and original:
        cpu.reg_write(a.UC_ARM_REG_R4, HANDLE)
    trace, writes, calls, reads = {}, [], [], []
    def code(uc, pc, size, _):
        if pc == STOP:
            uc.emu_stop()
            return  # synthetic caller endpoint, no executable stub
        seg = next((s for s in segments if s['flags'] & 1 and s['address'] <= pc and pc + size <= s['address'] + len(s['data'])), None)
        assert seg is not None, hex(pc)
        raw = bytes(uc.mem_read(pc, size))
        assert raw == seg['data'][pc - seg['address']:pc - seg['address'] + size]
        trace[hex(pc)] = raw.hex()
        if original and pc == 0x47ef18:
            calls.append({'callee': 'descriptor_lookup', 'domain': uc.reg_read(a.UC_ARM_REG_R1), 'out': uc.reg_read(a.UC_ARM_REG_R0)})
        if original and pc == 0x439c04:
            calls.append({'callee': 'stock_copy', 'bytes': uc.reg_read(a.UC_ARM_REG_R2)})
    def memory(uc, access, address, size, value, _):
        assert not 0x40000000 <= address < 0x60000000, ('unexpected MMIO', hex(address))
        if access == u.UC_MEM_WRITE:
            writes.append([address, size, value & ((1 << (size * 8)) - 1)])
        elif 0x6becb0 <= address < 0x6beed0:
            reads.append([address, size])
    cpu.hook_add(u.UC_HOOK_CODE, code)
    cpu.hook_add(u.UC_HOOK_MEM_READ | u.UC_HOOK_MEM_WRITE, memory)
    end = 0x47f7be if consumer and original else STOP
    cpu.emu_start(entry | 1, end, count=300)
    assert cpu.reg_read(a.UC_ARM_REG_PC) == end
    assert cpu.reg_read(a.UC_ARM_REG_PRIMASK) == prior
    if consumer and original:
        assert cpu.reg_read(a.UC_ARM_REG_SP) == SP - 40
        # Stock power consumer has not returned. Its descriptor is a local.
        output = SP - 40 + 4
    else:
        output = OUT
        assert cpu.reg_read(a.UC_ARM_REG_SP) == SP
        assert all(cpu.reg_read(reg) == val for reg, val in saved.items())
    assert bytes(cpu.mem_read(OUT - 8, 8)) == b'\xcc' * 8
    assert bytes(cpu.mem_read(OUT + 16, 8)) == b'\xcc' * 8
    selected_writes = [[address - output, size, val] for address, size, val in writes if output <= address < output + 16]
    assert all(off in (0, 4, 8, 12) and size == 4 for off, size, val in selected_writes)
    return {'status': cpu.reg_read(a.UC_ARM_REG_R0), 'output': bytes(cpu.mem_read(output, 16)).hex(),
            'output_writes': selected_writes, 'primask': prior, 'calls': calls, 'table_reads': reads, 'trace': trace}


def cases():
    for domain in list(range(36)) + [255, 256, 257, 0xffffffff]:
        for null in (False, True):
            for prior in (0, 1):
                yield {'kind': 'direct', 'value': domain, 'null': null, 'prior': prior}
    # Stock caller always supplies a nonnull local; module selection wraps to byte.
    for module in list(range(36)) + [252, 253, 254, 255, 256, 257, 0xffffffff]:
        for prior in (0, 1):
            yield {'kind': 'consumer', 'value': module, 'null': False, 'prior': prior}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--elf', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert sha(FIRMWARE) == EXPECTED_SHA
    raw = FIRMWARE.read_bytes()[32:]
    assert struct.unpack_from('<I', raw, 0x47f944 - BASE)[0] == 0x6becb0
    table = raw[0x6becb0 - BASE:0x6beed0 - BASE]
    stock = [dict(address=p, memory_size=n, data=raw[p - BASE:p - BASE + n], flags=flags)
             for p, n, flags in [(0x47e000, 8192, 5), (0x439000, 4096, 5), (0x55c000, 4096, 5), (0x6be000, 4096, 4)]]
    _, segments, symbols = elf_reader.elf_info(args.elf)
    all_trace, results = {}, []
    for case in cases():
        consumer = case['kind'] == 'consumer'
        value, null, prior = case['value'], case['null'], case['prior']
        domain = ((value + 3) & 255) if consumer else value
        status = 6 if null or domain >= 34 else 0
        expected = 'a5' * 16 if status else table[domain * 16:domain * 16 + 16].hex()
        original = run(stock, 0x55ca72 if consumer else 0x47ef18, value, null, prior, consumer, True)
        source = run(segments, symbols['opencfw_iom_domain_descriptor' if consumer else 'opencfw_power_domain_descriptor'] & ~1, value, null, prior)
        for result in (original, source):
            assert result['status'] == status, (case, result)
            assert result['output'] == expected, (case, result)
            assert result['output_writes'] == ([] if status else [[i, 4, struct.unpack_from('<I', bytes.fromhex(expected), i)[0]] for i in (0, 4, 8, 12)])
        assert len(original['calls']) == (1 if status else 2)
        assert original['calls'][0]['domain'] == domain
        for address, bytes_hex in original['trace'].items():
            assert address not in all_trace or all_trace[address] == bytes_hex
            all_trace[address] = bytes_hex
        results.append({'inputs': case, 'domain': domain, 'original': original, 'source': source})
    used = {int(pc, 0) + i for pc, bytes_hex in all_trace.items() for i in range(len(bytes.fromhex(bytes_hex)))}
    report = {'status': 'PASS', 'cases': len(results), 'results': results, 'original_trace': all_trace,
              'unique_original_trace_bytes': len(used), 'firmware_sha256': sha(FIRMWARE), 'elf_sha256': sha(args.elf),
              'descriptor_table': {'address': '0x6becb0', 'size': 544, 'sha256': hashlib.sha256(table).hexdigest()},
              'source_manifest': {str(p.relative_to(ROOT)): sha(p) for p in Path(__file__).parent.iterdir() if p.suffix in ('.c', '.h', '.py')},
              'limits': 'Descriptor selection/copy only. Full stock lookup returns; IOM consumer stops at 47f7be after lookup, with live stack frame. Source IOM helper implements only uint8(module+3) selection. No executable callee stubs, no MMIO, no power transition/delay/timeout/callback or asynchronous ownership claim; valid mapped RAM states, original copy IT instructions observed.'}
    with args.output.open('x') as f:
        json.dump(report, f, indent=2)
        f.write('\n')
    print('PASS', len(results), len(used))


if __name__ == '__main__':
    main()
