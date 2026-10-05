#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare reused MSPI interrupt source against original instructions offline."""
import argparse
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

if not __debug__:
    raise RuntimeError('optimized Python is rejected for simulator evidence')
ROOT = Path(__file__).resolve().parents[5]
PARSER = ROOT / 'g2/components/foundation/touch_scb/simulator/verify.py'
spec = importlib.util.spec_from_file_location('foundation_elf', PARSER)
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)
MSPI = 0x40060000
HANDLE = 0x20001000
OUTPUT = 0x20002000
STOP = 0x08000000
BASE = 0x438000
FUNCTIONS = {
    'enable': (0x4c2328, 52, 'ff601938062e67c168148c01471475c081038eb87938f8344c93afbf89f673e4'),
    'disable': (0x4c235c, 54, '046eba05f4da245735e178e179220a0c666e75c2c377bf05f08fab8815900a40'),
    'status': (0x4c2392, 76, 'af49be2bc2098b45d294afc6ca8cc5f9f48eee343a0245cea95a9d832973c1c5'),
    'clear': (0x4c23de, 48, '4b01a25a8075cf158eb59da277f8730e36c751ee01c67bae86bc172ec877bd48'),
}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def execute(segments, entry, operation, prefix, module, mask, enable, status,
            enabled_only=False, null_handle=False, null_output=False):
    import unicorn
    import capstone
    from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2,
                                   UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC)
    cpu = unicorn.Uc(unicorn.UC_ARCH_ARM, unicorn.UC_MODE_THUMB | unicorn.UC_MODE_MCLASS)
    pages = set()
    for segment in segments:
        for address in range(segment['address'] & ~4095,
                             (segment['address'] + segment['memory_size'] + 4095) & ~4095, 4096):
            if address not in pages:
                cpu.mem_map(address, 4096)
                pages.add(address)
        cpu.mem_write(segment['address'], segment['data'])
    for address in range(0x20000000, 0x20010000, 4096):
        if address not in pages:
            cpu.mem_map(address, 4096)
    cpu.mem_map(MSPI, 3 * 4096)
    cpu.mem_map(STOP, 4096)
    for i in range(3):
        cpu.mem_write(MSPI + i * 4096 + 0x200, struct.pack('<3I', enable, status, 0xdecafbad))
    cpu.mem_write(HANDLE, struct.pack('<2I', prefix, module))
    guard = b'\xa5' * 24
    cpu.mem_write(OUTPUT - 8, guard)
    initial_handle = bytes(cpu.mem_read(HANDLE, 8))
    accesses, trace = [], []
    disassembler = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB | capstone.CS_MODE_MCLASS)

    def instruction(uc, address, size, _):
        matches = [s for s in segments if s['flags'] & 1 and
                   s['address'] <= address < address + size <= s['address'] + len(s['data'])]
        assert len(matches) == 1, hex(address)
        segment = matches[0]
        raw = bytes(uc.mem_read(address, size))
        offset = address - segment['address']
        assert raw == segment['data'][offset:offset + size]
        decoded = list(disassembler.disasm(raw, address))
        assert len(decoded) == 1 and decoded[0].size == size
        trace.append({'pc': address, 'bytes': raw.hex()})

    def memory(uc, access, address, size, value, _):
        if MSPI <= address < MSPI + 3 * 4096:
            assert size == 4 and (address - MSPI) % 4096 in [0x200, 0x204, 0x208]
            assert (address - MSPI) // 4096 == module
            write = access == unicorn.UC_MEM_WRITE
            accesses.append({'kind': 'write' if write else 'read',
                             'offset': address - MSPI - module * 4096,
                             'value': value if write else struct.unpack('<I', uc.mem_read(address, 4))[0]})
            if write and (address - MSPI) % 4096 == 0x208:
                # Synthetic W1C stimulus only; no timing/posted-write hardware model.
                old = struct.unpack('<I', uc.mem_read(MSPI + module * 4096 + 0x204, 4))[0]
                uc.mem_write(MSPI + module * 4096 + 0x204, struct.pack('<I', old & ~value))

    cpu.hook_add(unicorn.UC_HOOK_CODE, instruction)
    cpu.hook_add(unicorn.UC_HOOK_MEM_READ | unicorn.UC_HOOK_MEM_WRITE, memory)
    cpu.reg_write(UC_ARM_REG_SP, 0x2000f000)
    cpu.reg_write(UC_ARM_REG_LR, STOP | 1)
    cpu.reg_write(UC_ARM_REG_R0, 0 if null_handle else HANDLE)
    cpu.reg_write(UC_ARM_REG_R1, (0 if null_output else OUTPUT) if operation == 'status' else mask)
    cpu.reg_write(UC_ARM_REG_R2, int(enabled_only))
    cpu.emu_start(entry | 1, STOP, count=1000)
    assert cpu.reg_read(UC_ARM_REG_PC) == STOP
    assert bytes(cpu.mem_read(HANDLE, 8)) == initial_handle
    return {'return': cpu.reg_read(UC_ARM_REG_R0), 'accesses': accesses, 'trace': trace,
            'output_guard': bytes(cpu.mem_read(OUTPUT - 8, len(guard))).hex(),
            'registers': [list(struct.unpack('<3I', cpu.mem_read(MSPI + i * 4096 + 0x200, 12)))
                          for i in range(3)]}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--elf', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    blob = (ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
    assert sha(blob) == '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
    image = blob[32:]
    elf, segments, symbols = loader.elf_info(args.elf)
    originals = {}
    for operation, (address, size, expected_hash) in FUNCTIONS.items():
        body = image[address - BASE:address - BASE + size]
        assert sha(body) == expected_hash
        originals[operation] = [dict(address=address, data=body, memory_size=size, flags=5)]
        # The four leaves load the same two literal words outside their bodies.
        for literal in [0x4c26dc, 0x4c2adc]:
            word = image[literal - BASE:literal - BASE + 4]
            assert struct.unpack('<I', word)[0] in [MSPI, 0x1bebebe]
            originals[operation].append(dict(address=literal, data=word, memory_size=4, flags=4))
        assert 'ambiq_sim_' + operation in symbols
    cases, original_bytes = [], {}
    # All physical module addresses, zero/all-bit/complement masks and both
    # status interpretations. Prefix high bits are deliberately ignored.
    valid = [(module, mask, enable, status, only, prefix)
             for module, mask, enable, status, prefix in [
                 (0, 0, 0x12345678, 0x87654321, 0x1bebebe),
                 (1, 0xffffffff, 0, 0xffffffff, 0xffbebebe),
                 (2, 0x55555555, 0xaaaaaaaa, 0x80000001, 0x3bebebe),
                 (1, 0x100, 0x101, 0x100, 0x1bebebe),
                 (1, 0x1a80, 0x2080, 0x1a80, 0x1bebebe),
                 (2, 0, 0, 0, 0x1bebebe)]
             for only in [False, True]]
    invalid = [(0, 0xffffffff, 0x12345678, 0xffffffff, False, prefix, null)
               for prefix, null in [(0x1bebebe, True), (0xbebebe, False),
                                     (0x1bebebf, False), (0, False), (0xfebebebe, False)]]
    for operation, (entry, _, _) in FUNCTIONS.items():
        for module, mask, enable, status, only, prefix, null in [(*v, False) for v in valid] + invalid:
            parameters = dict(operation=operation, prefix=prefix, module=module, mask=mask,
                              enable=enable, status=status, enabled_only=only, null_handle=null,
                              null_output=(operation == 'status' and (null or prefix & 0x1ffffff != 0x1bebebe)))
            stock = execute(originals[operation], entry, **parameters)
            source = execute(segments, symbols['ambiq_sim_' + operation], **parameters)
            for key in ['return', 'accesses', 'output_guard', 'registers']:
                assert stock[key] == source[key], (operation, parameters, key)
            is_valid = not null and prefix & 0x1ffffff == 0x1bebebe
            assert stock['return'] == (0 if is_valid else 2)
            expected_accesses = []
            expected_guard = bytearray(b'\xa5' * 24)
            if is_valid:
                if operation in ['enable', 'disable']:
                    value = enable | mask if operation == 'enable' else enable & ~mask
                    expected_accesses = [('read', 0x200, enable), ('write', 0x200, value)]
                elif operation == 'status':
                    expected_accesses = [('read', 0x204, status)]
                    if only:
                        expected_accesses.append(('read', 0x200, enable))
                    expected_guard[8:12] = struct.pack('<I', status & enable if only else status)
                else:
                    expected_accesses = [('write', 0x208, mask), ('read', 0x204, status & ~mask)]
            assert [(a['kind'], a['offset'], a['value']) for a in stock['accesses']] == expected_accesses
            assert stock['output_guard'] == expected_guard.hex()
            for t in stock['trace']:
                original_bytes[t['pc']] = t['bytes']
            cases.append(dict(parameters=parameters, original=stock, source_linked=source))
    component = Path(__file__).resolve().parents[1]
    report = {'status': 'PASS', 'firmware_sha256': sha(blob), 'image_base': BASE,
              'linked_elf_sha256': sha(elf), 'script_sha256': sha(Path(__file__).read_bytes()),
              'elf_parser_sha256': sha(PARSER.read_bytes()), 'elf': str(args.elf),
              'source_manifest': {str(p.relative_to(ROOT)): sha(p.read_bytes())
                                  for p in sorted(component.rglob('*')) if p.suffix in ['.c', '.h', '.ld']},
              'functions': {k: {'address': a, 'bytes': n, 'sha256': h} for k, (a, n, h) in FUNCTIONS.items()},
              'cases': cases, 'case_count': len(cases),
              'original_unique_instruction_bytes': sum(len(bytes.fromhex(v)) for v in original_bytes.values()),
              'limits': 'Source subset, minimal prefix/interrupt register compatibility types. Synthetic W1C and powered mapped modules; no clock, NVIC, DMA, posted bus write or hardware IRQ timing proof. No original callee stubs. Not a full HAL or bootable firmware.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        stream.write(json.dumps(report, indent=2) + '\n')
    print('PASS', len(cases), 'original/source MSPI cases;', report['original_unique_instruction_bytes'], 'original bytes')

if __name__ == '__main__':
    main()
