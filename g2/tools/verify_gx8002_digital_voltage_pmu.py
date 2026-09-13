# SPDX-License-Identifier: MIT
"""Compose digital voltage wrappers with the recovered PMU dispatcher."""
import json
import struct
import subprocess
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import sha
from verify_gx8002_memcpy_source import decode
from compare_gx8002_platform_config import execute, ROOT
from verify_gx8002_digital_voltage import verify as qualify


def load_pmu():
    directory = ROOT / 'build/gx8002-board'
    path = directory / 'config.elf'
    report = json.loads((ROOT / 'docs/research/gx8002-platform-config-candidate.json').read_text())
    source = ROOT / 'components/shared/gx8002/runtime_gx8002_platform_config.c'
    assert sha(source.read_bytes()) == report['source_sha256']
    elf = Elf32(path.read_bytes(), str(path))
    for row in [*report['functions'], report['generated_dispatch_table']]:
        section = next(s for s in elf.sections if s['name'] == row['section'])
        assert sha(elf.contents(section)) == row['compiled_sha256']
        assert not elf.relocations(section['index'])
    table = struct.unpack('<10I', elf.contents(next(s for s in elf.sections if s['name'] == '.rodata.platform_config')))
    code = decode(subprocess.check_output([str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-objdump'), '-d', str(path)], text=True))
    calls = []

    def pmu(operation, value):
        assert operation == 8
        # The helper executor uses its own aligned caller-record address.
        # Marshal the exact complete word produced by the decoded wrapper.
        events = [['read32', 0x20028000, value], ['write', 0xa0000038, value]]
        result = execute(code, 0x10025d74, 0, table, operation, events)
        calls.append(value)
        return result

    return pmu, calls, sha(path.read_bytes())


def verify():
    pmu, calls, digest = load_pmu()
    evidence = qualify(pmu_runner=pmu)
    assert len(calls) == 4120
    return {'evidence': evidence, 'decoded_pmu_calls': len(calls),
            'pmu_elf_sha256': digest, 'source_admitted': False,
            'limits': ['Exact wrapper-produced word marshalled into decoded PMU dispatcher with source-generated jump table.',
                       'Private caller-record address; physical reserved-bit semantics remain unqualified.']}


if __name__ == '__main__':
    report = verify()
    (ROOT / 'docs/research/gx8002-digital-voltage-pmu.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['decoded_pmu_calls'])
