# SPDX-License-Identifier: MIT
"""Cumulative PLL configuration state across initialization retries and resume."""
import json
import subprocess
from verify_gx8002_clock_init_paths import verify as qualify
from verify_gx8002_clock_pll import execute, oracle, OFFSETS
from verify_gx8002_power_initialize import word
from verify_gx8002_memcpy_source import decode
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import ROOT, sha
from execute_gx8002_clock_pll_wait import execute as wait
from verify_gx8002_clock_pll_wait import expected as wait_model
from verify_gx8002_clock_time_us_candidate import execute as timer


def verify(include_other_state=False,copy_runner=None,mode_runner=None,trim_state_runner=None):
    path = ROOT / 'build/gx8002-board/clock-pll-candidate.elf'
    elf = Elf32(path.read_bytes(), str(path))
    report = json.loads((ROOT / 'docs/research/gx8002-clock-pll-source-verification.json').read_text())
    for row in report['functions']:
        section = next(s for s in elf.sections if s['name'] == row['section_name'])
        assert sha(elf.contents(section)) == row['compiled_sha256']
    code = decode(subprocess.check_output([str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-objdump'), '-d', str(path)], text=True))
    dependencies = {}
    for name in ('clock-pll-wait','clock-time-us'):
        dependency = ROOT / f'build/gx8002-board/{name}-candidate.elf'
        image = Elf32(dependency.read_bytes(),name)
        baseline = json.loads((ROOT / f'docs/research/gx8002-{name}-source-verification.json').read_text())
        for row in baseline['functions']:
            section = next(s for s in image.sections if s['name']==row['section_name'])
            assert sha(image.contents(section))==row['compiled_sha256']
        dependencies[name] = decode(subprocess.check_output([str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-d',str(dependency)],text=True))
    calls = []
    def inputs(state):
        return [word(state, 0x200268c8+i*4) for i in range(14)], {off: word(state, 0xa0005000+off) for off in OFFSETS}
    def apply(result, state, events):
        for offset, value in result[1].items():word(state, 0xa0005000+offset, value)
        for kind, address, value in result[0]:
            if kind == 'write':events.extend(('write_byte', address+i, (value >> (8*i)) & 255) for i in range(4))
    def configure(target,args,state,events,wanted):
        assert args[0] == 0x200268c8
        fields, registers = inputs(state)
        expected_config = oracle(True,fields,registers,0)
        invoked=[]
        def config(enable):
            assert enable==1 and not invoked
            result=execute(code,0x10024b04,True,fields,registers,0)
            assert result==expected_config
            apply(result,state,events);invoked.append(True)
            return result[0]
        blocking=target==0x10025060
        locks=([8],[0,8],[0,0,8])[len(calls)%3] if blocking else ([0,8] if wanted==0 else [0])
        ticks=[] if blocking else ([0,40960] if wanted==0 else [0,41984])
        timeout=0 if blocking else args[1]
        def convert(value):return timer(dependencies['clock-time-us'],value&0xffffffff,value>>32)
        result=wait(dependencies['clock-pll-wait'],target,1,timeout,1,locks,ticks,convert,config)
        expected_wait=wait_model(blocking,1,timeout,locks,[] if blocking else ([0,40000] if wanted==0 else [0,41000]))
        expected_trace=expected_wait[2][:1]+expected_config[0]+expected_wait[2][1:]
        assert result[0]=='return' and result[2]==expected_trace and invoked==[True]
        if not blocking:assert result[1]==wanted
        calls.append(fields[5])
        return 0 if blocking else result[1]
    def model(state, events):
        fields, registers = inputs(state)
        apply(oracle(True, fields, registers, 0), state, events)
    if include_other_state:
        from verify_gx8002_clock_init_gate_state import verify as combined
        evidence = combined(pll_state_runner=configure, pll_state_model=model,copy_runner=copy_runner,mode_runner=mode_runner,trim_state_runner=trim_state_runner)
    else:
        evidence = qualify(pll_state_runner=configure, pll_state_model=model,copy_runner=copy_runner,mode_runner=mode_runner,trim_state_runner=trim_state_runner)
    assert len(calls) == 52
    return {'evidence': evidence, 'shared_pll_configurations': len(calls), 'other_state_included': include_other_state,
            'pll_elf_sha256': sha(path.read_bytes()), 'source_admitted': False,
            'limits': ['Decoded configuration writes propagate between retries and into final initialization state.',
                       'Decoded wait/configuration/timer composed; lock samples and tick inputs scripted.',
                       'Other helper state families depend on composition option; physical timing remains unqualified.']}


if __name__ == '__main__':
    report = verify()
    (ROOT / 'docs/research/gx8002-clock-init-pll-state.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['shared_pll_configurations'])
