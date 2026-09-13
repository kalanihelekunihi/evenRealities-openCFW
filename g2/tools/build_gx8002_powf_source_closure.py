# SPDX-License-Identifier: MIT
"""Build complete pinned Newlib power/sqrt source with recovered dependencies."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32
from build_gx8002_scalbnf_probe import build as scale_build
from verify_gx8002_analog_source import FLAGS

def build():
    scale=scale_build(corrected=True)
    upstream=ROOT/'build/upstream-newlib-math';receipt=json.loads((upstream/'receipt.json').read_text())
    assert receipt['commit']=='4aa696c8d6294897411cf78cae87f7f4680e9687'
    for row in receipt['files']:assert sha((upstream/row['path'].split('/')[-1]).read_bytes())==row['sha256']
    out=ROOT/'build/gx8002-powf-source-closure';out.mkdir(exist_ok=True)
    header=ROOT/'components/shared/gx8002/newlib_math_compat.h';(out/'fdlibm.h').write_bytes(header.read_bytes())
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');objects=[];commands=[]
    for name in ('ef_pow.c','ef_sqrt.c'):
        source=out/name;source.write_bytes((upstream/name).read_bytes());obj=out/(name+'.o')
        cmd=[pre+'gcc',*FLAGS,'-fwrapv','-ffp-contract=off','-c',str(source),'-o',str(obj)]
        subprocess.run(cmd,check=True);objects.append(str(obj));commands.append(cmd)
    objects += [str(ROOT/'build/gx8002-scalbnf-corrected'/f'source{i}.o') for i in (0,1)]
    ld=out/'power.ld';ld.write_text('SECTIONS { .text 0x10018000 : { *(.text*) } .rodata : { *(.rodata*) } }\n')
    path=out/'power.elf';subprocess.run([pre+'ld','-T',str(ld),*objects,'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'power');assert not any(s['name'] and s['section']==0 for s in elf.symbols());assert not any(elf.relocations(s['index']) for s in elf.sections)
    (out/'power.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result={'upstream':receipt,'header_sha256':sha(header.read_bytes()),'commands':commands,'scale':scale,'elf_sha256':sha(path.read_bytes()),'sections':[(s['name'],s['size']) for s in elf.sections if s['flags']&2 and s['size']],'source_admitted':False,'limits':['Analysis-only complete source closure. Pinned power and square-root algorithm bodies copied intact with license notices. Header selects IEEE binary32; fwrapv defines signed integer wrap. Behavioral, exception and physical placement qualification pending.']}
    (ROOT/'docs/research/gx8002-powf-source-closure.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(build()['sections'])
