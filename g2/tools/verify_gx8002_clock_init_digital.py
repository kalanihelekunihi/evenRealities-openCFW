# SPDX-License-Identifier: MIT
"""Execute initialization's digital voltage call through recovered C and PMU."""
import json
from build_gx8002_digital_voltage_candidate import build, ROOT
from verify_gx8002_digital_voltage_pmu import load_pmu
from verify_gx8002_clock_init_paths import verify as qualify
from verify_gx8002_memcpy_source import decode
from execute_gx8002_digital_voltage import execute
from verify_gx8002_power_initialize import word


def verify():
    candidate = build()
    assert candidate['fits']
    pmu, calls, digest = load_pmu()
    code = decode((ROOT / 'build/gx8002-board/digital-voltage-candidate.disassembly.txt').read_text())
    def digital(voltage):
        assert voltage == 0
        def helper(target, args, memory, events):
            assert target == 0x10025d74 and args[0] == 8
            value = word(memory, args[1])
            assert value == 16
            return pmu(args[0], value)
        result, after, events = execute(code, 0x10024730, [voltage], {}, helper)
        assert result[:2] == ('return', 0) and not after and not events
        return result[1]
    evidence = qualify(digital_runner=digital)
    assert calls == [16] * 190
    return {'evidence': evidence, 'digital_candidate': candidate,
            'decoded_digital_and_pmu_calls': len(calls), 'pmu_elf_sha256': digest,
            'source_admitted': False,
            'limits': ['Both outer initialization variants use the corrected C digital wrapper; stock reserved-bit difference is qualified separately.',
                       'Private helper stack and PMU caller-record marshalling; MMIO trace checked independently, not merged into outer state.',
                       'Physical hardware remains unqualified.']}


if __name__ == '__main__':
    report = verify()
    (ROOT / 'docs/research/gx8002-clock-init-digital.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['decoded_digital_and_pmu_calls'])
