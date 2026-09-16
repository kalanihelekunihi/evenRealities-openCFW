# SPDX-License-Identifier: MIT
"""Place complete pinned log/exp source and constants inside stock envelopes."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32
from build_gx8002_log_exp_probe import build as probe
from verify_gx8002_analog_source import FLAGS

def build():
    evidence=probe();out=ROOT/'build/gx8002-log-exp-placed';out.mkdir(exist_ok=True)
    source=ROOT/'build/gx8002-log-exp-probe';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    obj=out/'exp.o';command=[pre+'gcc',*[('-Os' if f=='-O2' else f) for f in FLAGS],'-fwrapv','-ffp-contract=off','-c',str(source/'ef_exp.c'),'-o',str(obj)];subprocess.run(command,check=True)
    delta=0x10003000-0x3b940
    ld=out/'math.ld';ld.write_text('SECTIONS { .log 0x%x : { *(.text.__ieee754_logf) } .exp 0x%x : { *(.text.__ieee754_expf) } .exp_constants : { *(.rodata*) } }\nASSERT(SIZEOF(.log)<=600,"log overflow")\nASSERT(SIZEOF(.exp)+SIZEOF(.exp_constants)<=524,"exp overflow")\n'%(0x490a8+delta,0x49300+delta))
    path=out/'math.elf';subprocess.run([pre+'ld','-T',str(ld),str(source/'ef_log.c.o'),str(obj),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'math');assert not any(s['name'] and s['section']==0 for s in elf.symbols());assert not any(elf.relocations(s['index']) for s in elf.sections)
    allocated=[s for s in elf.sections if s['flags']&2 and s['size']];assert {s['name'] for s in allocated}=={'.log','.exp','.exp_constants'}
    for name,offset in (('__ieee754_logf',0x490a8),('__ieee754_expf',0x49300)):
        assert next(s['value'] for s in elf.symbols() if s['name']==name)==offset+delta
    rows=[{'name':s['name'],'package_offset':s['address']-delta,'bytes':s['size'],'sha256':sha(elf.contents(s))} for s in allocated]
    (out/'math.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result={'probe':evidence,'exp_command':command,'elf_sha256':sha(path.read_bytes()),'sections':rows,'source_admitted':False,'limits':['Whole source functions and source constants fit original regions. Numerical/ABI/reference qualification and integration pending; no binary fragments reused.']}
    (ROOT/'docs/research/gx8002-log-exp-placed.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=build();print(r['elf_sha256'],r['sections'])
