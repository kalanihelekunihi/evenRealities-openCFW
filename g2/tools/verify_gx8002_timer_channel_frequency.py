# SPDX-License-Identifier: MIT
"""Timer setup composed with decoded module-23 low-frequency clock paths."""
import json,struct,subprocess
from verify_gx8002_timer_channel_initialize import verify as qualify,execute,expected,ROOT,sha,Elf32,decode
from verify_gx8002_clock_low_frame import execute as frequency

def verify():
    evidence=qualify();path=ROOT/'build/gx8002-clock-frequency-table-probe/placement.elf'
    report_path=ROOT/'docs/research/gx8002-clock-frequency-source-verification.json'
    report=json.loads(report_path.read_text());elf=Elf32(path.read_bytes(),'frequency');sections={s['name']:s for s in elf.sections}
    for row in report['functions']:
        sec=sections[row['section_name']];assert sha(elf.contents(sec))==row['compiled_sha256'] and not elf.relocations(sec['index'])
    table=struct.unpack('<19I',elf.contents(sections['.rodata.open_cfw_gx8002_clock_frequency']))
    records=elf.contents(sections['.data.gx_clock_param_table'])
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    timer=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-board/timer-channel-initialize-candidate.elf')],text=True))
    cases=0
    for source in (0,1<<18):
      for seed in (0,1,0xffffffff):
        calls=[]
        def provider(module):
            assert module==23
            hz,trace=frequency(code,table,module,0,0,source,lookup_records=records)
            assert hz==(1024000 if source else 12288000) and trace==[('lookup',22)]
            calls.append(trace);return hz
        actual=execute(timer,0x100257b8,0,seed,provider)
        assert actual==expected(1024000 if source else 12288000) and len(calls)==1
        cases+=1
    return {'evidence':evidence,'frequency_elf_sha256':sha(path.read_bytes()),'frequency_report_sha256':sha(report_path.read_bytes()),'composed_cases':cases,'source_admitted':False,'limits':['Actual decoded frequency provider and lookup with placement-table records; low-frequency source choices only. Clock registers modeled. Other frequency selections and outer timer initialization remain separate qualifications. No physical timer qualification.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-timer-channel-frequency.json').write_text(json.dumps(r,indent=2)+'\n');print(r['composed_cases'])
