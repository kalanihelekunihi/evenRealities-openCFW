# SPDX-License-Identifier: MIT
"""Rebuild GCC software-double dependencies and link exp without binary imports."""
import json,subprocess,shlex
from build_gx8002_backup_exp_probe import build as exp
from build_gx8002_backup_cfft import ROOT,sha,Elf32


def build():
    evidence=exp()
    source=ROOT/'build/upstream-csky-toolchain-build/gcc'
    receipt=json.loads((ROOT/'build/csky-macos/gcc-build-receipt.json').read_text())
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()
    assert revision==receipt['source_revisions']['gcc']
    lib=ROOT/'build/csky-macos/gcc-build/csky-unknown-elf/libgcc'
    names=['pack','unpack','addsub','mul','div','fpcmp_parts','gt','lt','si_to','df_to_si','thenan']
    objects=['_'+n+'_df.o' if n not in ('si_to','df_to_si') else '_si_to_df.o' if n=='si_to' else '_df_to_si.o' for n in names]
    out=ROOT/'build/gx8002-exp-source-closure';out.mkdir(exist_ok=True)
    # Force only fp-bit compilation, not configure regeneration requiring Autoconf 2.69.
    run=subprocess.run(['make','-W',str(source/'libgcc/fp-bit.c'),*objects],cwd=lib,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (out/'rebuild.log').write_text(run.stdout);assert run.returncode==0,run.stdout
    dependencies={};object_rows=[]
    for name in objects:
        assert '-o '+name in run.stdout,'object was not rebuilt: '+name
        dep=(lib/name.replace('.o','.dep')).read_text().replace('\\\n',' ')
        for entry in shlex.split(dep.splitlines()[0].split(':',1)[1]):
            path=(lib/entry).resolve();assert path.is_file()
            dependencies[str(path.relative_to(ROOT))]=sha(path.read_bytes())
        object_rows.append({'name':name,'sha256':sha((lib/name).read_bytes())})
    script=out/'exp.ld';script.write_text('SECTIONS { .text 0x10018000 : { *(.text*) } .rodata : { *(.rodata*) } .data : { *(.data*) } .bss : { *(.bss*) } }\n')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    path=out/'exp.elf'
    subprocess.run([pre+'ld','-T',str(script),str(ROOT/'build/gx8002-backup-exp-probe/exp.o'),*[str(lib/n) for n in objects],'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'source closure')
    unresolved=sorted({s['name'] for s in elf.symbols() if s['name'] and s['section']==0});assert not unresolved,unresolved
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    result={'exp':evidence,'gcc_revision':revision,'runtime_license':'GPL-3.0-or-later WITH GCC-exception-3.1','rebuilt_objects':object_rows,'source_dependencies':dependencies,'elf_sha256':sha(path.read_bytes()),
            'allocated_bytes':sum(s['size'] for s in elf.sections if s['flags']&2),'unresolved_symbols':unresolved,'source_admitted':False,'hardware_qualified':False,
            'limits':['Fully linked source arithmetic experiment at analysis address. No retained firmware helper addresses or archive extraction used.',
                      'GCC fp-bit rounding, NaN, flags and complete exp behavior have not been qualified against stock. Placement and firmware admission pending.']}
    (ROOT/'docs/research/gx8002-exp-source-closure.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=build();print(r['allocated_bytes'],r['unresolved_symbols'])
