# SPDX-License-Identifier: MIT
"""Decoded initialization selectors with cumulative shared register state."""
import json
import subprocess
from verify_gx8002_clock_init_paths import verify as qualify
from execute_gx8002_clock_source_select import execute
from verify_gx8002_power_initialize import word
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import ROOT, sha
from verify_gx8002_memcpy_source import decode


def verify(include_voltage=False,module_state_runner=None,module_state_model=None,divider_state_runner=None,divider_state_model=None,divider_addresses=(),gate_state_runner=None,gate_state_model=None,pll_state_runner=None,pll_state_model=None,copy_runner=None,mode_runner=None,trim_state_runner=None):
    path = ROOT / 'build/gx8002-board/clock-source-select-candidate.elf'
    elf = Elf32(path.read_bytes(), str(path))
    report = json.loads((ROOT / 'docs/research/gx8002-clock-source-select-source-verification.json').read_text())
    for row in report['functions']:
        section = next(s for s in elf.sections if s['name'] == row['section_name'])
        assert sha(elf.contents(section)) == row['compiled_sha256']
    code = decode(subprocess.check_output([str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-objdump'), '-d', str(path)], text=True))
    calls = []
    def selector(args, memory, events):
        before = dict(memory)
        source, clock = word(memory, args[0]), memory[args[0]+4]
        def helper(target, parameters, state, writes):
            assert target == 0x10024a30 and parameters == [0xa001008c, source, clock, 1]
            result, after, nested = execute(code, target, parameters, state, lambda *a: None)
            assert result[0] == 'return'
            state.clear(); state.update(after); writes.extend(nested)
            return 0
        result, after, writes = execute(code, 0x10024bcc, args[:1], memory, helper)
        assert result[0] == 'return'
        expected = (word(before, 0xa001008c) & ~(1 << source)) | (clock << source)
        assert word(after, 0xa001008c) == expected
        assert all(after[k] == v for k, v in before.items() if not 0xa001008c <= k < 0xa0010090)
        memory.clear(); memory.update(after); events.extend(writes)
        calls.append((source, clock))
        return 0
    if include_voltage:
        from verify_gx8002_clock_init_voltage_state import verify as voltage_qualify
        evidence = voltage_qualify(selector_state_runner=selector,module_state_runner=module_state_runner,module_state_model=module_state_model,divider_state_runner=divider_state_runner,divider_state_model=divider_state_model,divider_addresses=divider_addresses,gate_state_runner=gate_state_runner,gate_state_model=gate_state_model,pll_state_runner=pll_state_runner,pll_state_model=pll_state_model,copy_runner=copy_runner,mode_runner=mode_runner,trim_state_runner=trim_state_runner)
    else:
        evidence = qualify(selector_state_runner=selector,module_state_runner=module_state_runner,module_state_model=module_state_model,divider_state_runner=divider_state_runner,divider_state_model=divider_state_model,divider_addresses=divider_addresses,gate_state_runner=gate_state_runner,gate_state_model=gate_state_model,pll_state_runner=pll_state_runner,pll_state_model=pll_state_model,copy_runner=copy_runner,mode_runner=mode_runner,trim_state_runner=trim_state_runner)
    assert len(calls) == 556
    return {'evidence': evidence, 'shared_selector_calls': len(calls),
            'selector_elf_sha256': sha(path.read_bytes()), 'voltage_state_included': include_voltage, 'source_admitted': False,
            'limits': ['Selector and register leaf execute on cumulative outer state and original source descriptor addresses.',
                       'Other clock dependencies remain modeled in this harness; physical qualification pending.']}


if __name__ == '__main__':
    report = verify()
    (ROOT / 'docs/research/gx8002-clock-init-selector-state.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['shared_selector_calls'])
