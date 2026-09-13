# SPDX-License-Identifier: MIT
"""Compare recovered digital voltage C with defined stock fields and stack leak."""
import json, random, subprocess
from build_gx8002_digital_voltage_candidate import build, ROOT, IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from execute_gx8002_digital_voltage import execute
from verify_gx8002_power_initialize import word


def verify(pmu_runner=None):
    candidate = build()
    assert sha(IMAGE.read_bytes()) == IMAGE_SHA
    path = ROOT / 'build/gx8002-board/padmux-get-stock.elf'
    elf = Elf32(path.read_bytes(), str(path))
    assert sha(elf.contents(next(s for s in elf.sections if s['name'] == '.data'))) == IMAGE_SHA
    objdump = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    stock = decode(subprocess.check_output([objdump, '-D', '--start-address=0x16744', '--stop-address=0x16770', str(path)], text=True))
    source = decode((ROOT / 'build/gx8002-board/digital-voltage-candidate.disassembly.txt').read_text())
    rng = random.Random(0x16744)
    inputs = list(range(256)) + [0xffffffff, 0xfffffffe, 0x80000000, 0x7fffffff] + [rng.getrandbits(32) for _ in range(256)]
    cases = changes = 0
    for voltage in inputs:
        for seed in (0, 0xff, 0xa5, 0x5a):
            commands = []
            for code, entry in ((stock, 0x16744), (source, 0x10024730)):
                calls = []
                def helper(target, args, memory, events):
                    assert target == 0x10025d74 and args[0] == 8
                    assert args[1] == 0x2006fff8
                    value = word(memory, args[1])
                    if pmu_runner:
                        assert pmu_runner(args[0], value) == 0
                    calls.append(value)
                    return 0xffffffff  # The wrapper must ignore PMU status.
                result, after, writes = execute(code, entry, [voltage], {}, helper, seed)
                assert result[:2] == ('return', 0xffffffff if voltage == 0xffffffff else 0) and not after and not writes
                commands.append(calls)
            if voltage == 0xffffffff:
                assert commands == [[], []]
            else:
                defined = 16 | (voltage & 15)
                assert commands == [[(seed * 0x01010101 & 0xffffffe0) | defined], [defined]]
                changes += commands[0] != commands[1]
            cases += 1
    return {'candidate': candidate, 'cases': cases, 'reserved_bit_changes': changes,
            'source_admitted': False, 'hardware_qualified': False,
            'limits': ['Decoded wrapper qualification only; PMU dispatcher remains a modeled boundary.',
                       'Reserved bits intentionally zeroed; hardware behavior remains unqualified.']}


if __name__ == '__main__':
    report = verify()
    (ROOT / 'docs/research/gx8002-digital-voltage-verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['cases'], report['reserved_bit_changes'])
