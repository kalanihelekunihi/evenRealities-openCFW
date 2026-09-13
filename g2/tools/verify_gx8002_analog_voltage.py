# SPDX-License-Identifier: MIT
"""Compare pure C analog voltage leaf against stock and independent MMIO policy."""
import json
import random
from build_gx8002_analog_voltage_candidate import build, ROOT, IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_ldo import ADDRESS, disassemble, execute


def verify():
    candidate = build()
    assert candidate['fits']
    directory = ROOT / 'build/gx8002-analog-ldo-source'
    oldpath = directory / 'runtime_gx8002_analog_ldo.o'
    oldreport = json.loads((directory / 'verification.json').read_text())
    elf = Elf32(oldpath.read_bytes(), str(oldpath))
    payload = elf.contents(next(s for s in elf.sections if s['name'] == oldreport['section_name']))
    stock = IMAGE.read_bytes()
    assert sha(stock) == IMAGE_SHA and payload == stock[0x16704:0x16724]
    objdump = ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-objdump'
    old = disassemble(objdump, oldpath, oldreport['section_name'])
    new = disassemble(objdump, ROOT / 'build/gx8002-board/analog-voltage-candidate.elf', '.text')
    rng = random.Random(0x16704)
    inputs = list(range(256)) + [0xffffffff, 0xfffffffe, 0x100, 0x80000000, 0x7fffffff]
    previous = [0, 0xffffffff, 0xaaaaaaaa, 0x55555555] + [rng.getrandbits(32) for _ in range(128)]
    cases = 0
    for voltage in inputs:
        for value in previous:
            expected = (0xffffffff, []) if voltage == 0xffffffff else (0, [('read32', ADDRESS, value), ('write32', ADDRESS, (voltage | (value & 0xf0)) & 0xff)])
            assert execute(old, voltage, value) == execute(new, voltage, value) == expected
            cases += 1
    return {'candidate': candidate, 'cases': cases, 'source_admitted': False,
            'limits': ['Restricted decoded leaf interpreter; no whole-device or physical qualification.',
                       'All low-byte input patterns plus upper-bit and sentinel boundaries; not an exhaustive 32-bit proof.']}


if __name__ == '__main__':
    report = verify()
    (ROOT / 'docs/research/gx8002-analog-voltage-verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['cases'])
