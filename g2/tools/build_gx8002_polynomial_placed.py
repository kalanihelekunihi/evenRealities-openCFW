# SPDX-License-Identifier: MIT
"""Build the complete reconstructed descending Horner evaluator on macOS."""
import json, subprocess
from build_gx8002_backup_cfft import ROOT, sha, Elf32
from verify_gx8002_analog_source import FLAGS
from analyze_gx8002_double_wrapper_references import analyze


def build():
    out = ROOT/'build/gx8002-polynomial-placed'; out.mkdir(exist_ok=True)
    source = ROOT/'components/shared/gx8002/runtime_gx8002_polynomial.c'
    pre = str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    obj = out/'polynomial.o'
    command = [pre+'gcc', *FLAGS, '-Os', '-ffp-contract=off', '-c', str(source), '-o', str(obj)]
    subprocess.run(command, check=True)
    delta = 0x10003000-0x3b940
    ld = out/'polynomial.ld'
    ld.write_text(('__muldf3 = 0x%x; __adddf3 = 0x%x;\nSECTIONS { .polynomial 0x%x : { *(.text.open_cfw_gx8002_polynomial) } }\nASSERT(SIZEOF(.polynomial)<=104,"polynomial overflow")\n') % (0x4a790+delta,0x4a724+delta,0x49828+delta))
    path = out/'polynomial.elf'
    subprocess.run([pre+'ld','-T',str(ld),str(obj),'-o',str(path)],check=True)
    elf = Elf32(path.read_bytes(),'polynomial')
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    sections = [s for s in elf.sections if s['flags']&2 and s['size']]
    assert len(sections)==1 and sections[0]['name']=='.polynomial'
    sec = sections[0]
    assert sec['address']==0x49828+delta
    assert next(s['value'] for s in elf.symbols() if s['name']=='open_cfw_gx8002_polynomial')==sec['address']
    (out/'polynomial.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result = {'source_sha256':sha(source.read_bytes()),'elf_sha256':sha(path.read_bytes()),'command':command,'sections':[{'name':sec['name'],'package_offset':0x49828,'bytes':sec['size'],'sha256':sha(elf.contents(sec))}],'references':analyze(0x49828,0x49890,require_entry_only=False),'source_admitted':False,'limits':['Whole function fits; numerical, ABI, reference classification, dependency identity and integration checks remain pending. Coefficient arrays remain caller-owned.']}
    (ROOT/'docs/research/gx8002-polynomial-placed.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__': print(build())
