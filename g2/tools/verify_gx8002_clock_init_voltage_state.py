# SPDX-License-Identifier: MIT
"""Initialization voltage writes merged into outer decoded memory and event order."""
import json
from verify_gx8002_clock_init_paths import verify as qualify
from verify_gx8002_clock_init_analog import verify as analog_qualification
from verify_gx8002_clock_init_digital import verify as digital_qualification
from verify_gx8002_analog_ldo import disassemble, execute as analog_execute
from execute_gx8002_digital_voltage import execute as digital_execute
from verify_gx8002_digital_voltage_pmu import load_pmu
from verify_gx8002_power_initialize import word
from verify_gx8002_memcpy_source import decode
from analyze_gx8002_upstream_objects import ROOT


def verify(selector_state_runner=None,module_state_runner=None,module_state_model=None,divider_state_runner=None,divider_state_model=None,divider_addresses=(),gate_state_runner=None,gate_state_model=None,pll_state_runner=None,pll_state_model=None,copy_runner=None,mode_runner=None,trim_state_runner=None):
    analog_evidence = analog_qualification()
    digital_evidence = digital_qualification()
    directory = ROOT / 'build/gx8002-board'
    analog = disassemble(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-objdump', directory / 'analog-voltage-candidate.elf', '.text')
    digital = decode((directory / 'digital-voltage-candidate.disassembly.txt').read_text())
    pmu, calls, digest = load_pmu()
    writes = []
    def voltage(target, args, memory, events):
        assert args[0] == 0
        def store(address, value):
            word(memory, address, value)
            events.extend(('write_byte', address+i, (value >> (8*i)) & 255) for i in range(4))
            writes.append((address, value))
        if target == 0x100246f0:
            result, trace = analog_execute(analog, args[0], word(memory, 0xa0005054))
            assert trace[0] == ('read32', 0xa0005054, word(memory, 0xa0005054))
            assert len(trace) == 2 and trace[1][:2] == ('write32', 0xa0005054)
            store(trace[1][1], trace[1][2])
            return result
        assert target == 0x10024730
        def helper(destination, parameters, frame, ignored):
            assert destination == 0x10025d74 and parameters[0] == 8
            value = word(frame, parameters[1])
            result = pmu(parameters[0], value)
            store(0xa0000038, value)  # Accepted decoded dispatcher write.
            return result
        result, after, private_events = digital_execute(digital, target, args[:1], {}, helper)
        assert result[:2] == ('return', 0) and not after and not private_events
        return result[1]
    evidence = qualify(voltage_state_runner=voltage,selector_state_runner=selector_state_runner,module_state_runner=module_state_runner,module_state_model=module_state_model,divider_state_runner=divider_state_runner,divider_state_model=divider_state_model,divider_addresses=divider_addresses,gate_state_runner=gate_state_runner,gate_state_model=gate_state_model,pll_state_runner=pll_state_runner,pll_state_model=pll_state_model,copy_runner=copy_runner,mode_runner=mode_runner,trim_state_runner=trim_state_runner)
    assert len(writes) == 380 and len(calls) == 190
    return {'evidence': evidence, 'analog_evidence': analog_evidence,
            'digital_evidence': digital_evidence, 'shared_voltage_writes': len(writes),
            'pmu_elf_sha256': digest, 'source_admitted': False,
            'limits': ['Voltage MMIO state and ordered writes now shared with initialization; other clock helpers remain modeled in this harness.',
                       'Digital reserved-bit correction used for both outer variants; stock difference qualified separately.',
                       'Helper stack/record marshalling and physical qualification remain limitations.']}


if __name__ == '__main__':
    report = verify()
    (ROOT / 'docs/research/gx8002-clock-init-voltage-state.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['shared_voltage_writes'])
