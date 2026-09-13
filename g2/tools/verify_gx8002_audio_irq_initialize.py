# SPDX-License-Identifier: MIT
"""Decoded initializer publication into source-owned IRQ state."""
import json,subprocess
from build_gx8002_audio_irq_candidate import build,ROOT,sha,Elf32
from execute_gx8002_audio_initialize import execute,STATE
from verify_gx8002_memcpy_source import decode

def verify():
    evidence=build();path=ROOT/'build/gx8002-source-candidate/audio-initialize/gain.elf';elf=Elf32(path.read_bytes(),'init');report=json.loads((ROOT/'docs/research/gx8002-audio-initialize-source-verification.json').read_text());row=report['functions'][0];section=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(section))==row['compiled_sha256']
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-d',str(path)],text=True));cases=0
    for present in range(32):
        # SDK config argument order: record,config,update,energy,FFT.
        callbacks=tuple(0x10220000+4*i if present&(1<<i) else 0 for i in range(5))
        result,trace,memory=execute(code,section['address'],callbacks,0xa5a5a5a5,7,7,0)
        expected=[7,7,callbacks[1],callbacks[0],callbacks[2],callbacks[3],callbacks[4]] if callbacks[1] else [0]*7
        assert [memory[STATE+4*i] for i in range(7)]==expected
        assert result==(0 if callbacks[1] else 0xffffffff)
        assert [e for e in trace if e[0]=='irq']==([('irq',2,0x10025e48,0)] if callbacks[1] else [])
        assert [e for e in trace if e[0]=='memset']==[('memset',STATE,0,28)]
        cases+=1
    return {'candidate':evidence,'initializer_elf_sha256':sha(path.read_bytes()),'cases':cases,'source_admitted':False,'limits':['Actual decoded source initializer clears/publishes all seven state words and installs recovered IRQ address across all callback-presence combinations. Initializer helper bodies modeled; IRQ execution not nested within initialization.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-irq-initialize.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
