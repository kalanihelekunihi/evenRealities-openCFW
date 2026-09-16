# SPDX-License-Identifier: MIT
"""Link complete source argument reduction and binary64 dependencies for analysis."""
import json,re,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32
from build_gx8002_reduction_probe import build as probe


def build():
    reports=[probe(),probe(helpers=True)]
    out=ROOT/'build/gx8002-reduction-source-closure';out.mkdir(exist_ok=True)
    base=ROOT/'build/gx8002-exp-placed-cluster'
    prior=json.loads((ROOT/'docs/research/gx8002-exp-placed-cluster.json').read_text())
    assert sha((base/'exp.elf').read_bytes())==prior['elf_sha256']
    before=Elf32((base/'exp.elf').read_bytes(),'arithmetic')
    script=(base/'exp.ld').read_text();inputs=list(dict.fromkeys(re.findall(r'(/[^\s()]+\.o)\(',script)))
    source=ROOT/'build/upstream-csky-toolchain-build/gcc/libgcc/fp-bit.c'
    lib=ROOT/'build/csky-macos/gcc-build/csky-unknown-elf/libgcc'
    command=['make','-W',str(source),'_eq_df.o','_ge_df.o']
    log=subprocess.check_output(command,cwd=lib,text=True);(out/'comparison-build.log').write_text(log)
    additions=[];objects=[]
    for report in reports:
        directory=ROOT/'build'/('gx8002-reduction-helpers-probe' if report['helpers'] else 'gx8002-reduction-probe')
        for row in report['objects']:
            obj=directory/(row['source']['path'].split('/')[-1]+'.o')
            assert sha(obj.read_bytes())==row['object_sha256'];additions.append(obj)
    for name in ('_eq_df.o','_ge_df.o'):
        obj=out/name;obj.write_bytes((lib/name).read_bytes());additions.append(obj)
    script+='SECTIONS { .reduction 0x10018000 : {\n'
    for obj in additions:
        inputs.append(str(obj));script+=str(obj)+'(.text .text.* .rodata .rodata.*)\n'
        objects.append({'path':str(obj),'sha256':sha(obj.read_bytes())})
    script+='} }\n'
    ld=out/'reduction.ld';ld.write_text(script);path=out/'reduction.elf';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'ld','-T',str(ld),*inputs,'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'reduction')
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    allocated=[s for s in elf.sections if s['flags']&2 and s['size']]
    for old in before.sections:
        if old['flags']&2 and old['size']:
            new=next(s for s in allocated if s['name']==old['name']);assert new['address']==old['address'] and elf.contents(new)==before.contents(old)
    assert {s['name'] for s in allocated}-{s['name'] for s in before.sections}=={'.reduction'}
    section=next(s for s in allocated if s['name']=='.reduction')
    (out/'reduction.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result={'probes':reports,'comparison_source_sha256':sha(source.read_bytes()),'comparison_build_command':command,'comparison_build_log_sha256':sha(log.encode()),'objects':objects,'arithmetic_elf_sha256':prior['elf_sha256'],'elf_sha256':sha(path.read_bytes()),'new_section_bytes':section['size'],'source_admitted':False,'limits':['Whole source link at analysis addresses outside stock image. Prior arithmetic byte-authenticated. Numerical/ABI tests, stock mapping, placement and hardware pending.']}
    (ROOT/'docs/research/gx8002-reduction-source-closure.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=build();print(r['elf_sha256'],r['new_section_bytes'])
