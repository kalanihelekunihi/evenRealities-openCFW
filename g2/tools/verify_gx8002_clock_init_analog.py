# SPDX-License-Identifier: MIT
"""Qualify initialization's analog voltage call through recovered instructions."""
import json
from build_transparent_image import Elf32
from verify_gx8002_clock_init_paths import verify as qualify
from verify_gx8002_analog_ldo import ADDRESS, ROOT, disassemble, execute
from verify_gx8002_analog_voltage import verify as qualify_leaf
from analyze_gx8002_upstream_objects import sha


def verify():
    evidence_leaf = qualify_leaf()
    report = evidence_leaf['candidate']
    path = ROOT / 'build/gx8002-board/analog-voltage-candidate.elf'
    elf = Elf32(path.read_bytes(), str(path))
    section = next(s for s in elf.sections if s['name'] == '.text')
    assert sha(elf.contents(section)) == report['compiled_sha256']
    code = disassemble(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-objdump', path, '.text')
    calls = []

    def analog(voltage):
        assert voltage == 0
        previous = (0, 0xffffffff, 0xaaaaaaaa, 0x55555555)[len(calls) % 4]
        result, trace = execute(code, voltage, previous)
        assert result == 0
        assert trace == [('read32', ADDRESS, previous), ('write32', ADDRESS, previous & 0xf0)]
        calls.append(trace)
        return result

    evidence = qualify(analog_runner=analog)
    assert len(calls) == 190
    return {'evidence': evidence, 'decoded_analog_calls': len(calls),
            'analog_object_sha256': sha(path.read_bytes()), 'leaf_evidence': evidence_leaf, 'source_admitted': False,
            'limits': ['Analog helper decoded on private MMIO snapshots; full shared hardware state integration remains pending.',
                       'Pure C analog candidate; physical qualification remains pending.',
                       'Digital voltage helper remains modeled at the initialization boundary.']}


if __name__ == '__main__':
    result = verify()
    (ROOT / 'docs/research/gx8002-clock-init-analog.json').write_text(json.dumps(result, indent=2) + '\n')
    print(result['decoded_analog_calls'])
