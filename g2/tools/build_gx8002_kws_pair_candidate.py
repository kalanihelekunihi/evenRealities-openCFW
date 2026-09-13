# SPDX-License-Identifier: MIT
"""Place compiler-generated KWS functions and their shared pool in one section."""
import json,re,subprocess
from build_gx8002_kws_run_candidate import build as runner,ROOT,sha
from build_gx8002_audio_completion_forward_candidate import build as callback
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import IMAGE,IMAGE_SHA

def build():
    run=runner();forward=callback();out=ROOT/'build/gx8002-board';sdk=ROOT/'build/upstream-nationalchip-lvp-kws';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    texts=[]
    for name,report,config in (('audio_completion_forward',forward,'audio-completion-config'),('kws_run',run,'kws-run-config')):
        assembly=out/(name+'-pair.s');source=ROOT/f'components/shared/gx8002/runtime_gx8002_{name}.c'
        subprocess.run([pre+'gcc',*report['flags'],'-mconstpool','-I'+str(out/config),'-I'+str(sdk/'include'),'-S',str(source),'-o',str(assembly)],check=True)
        texts.append(assembly.read_text())
    a,b=texts
    marker='\t.align\t2\n.LCP0:\n\t.long\topen_cfw_gx8002_audio_completion_callback\n'
    assert a.count(marker)==1 and a.count('\tlrw\ta3, [.LCP0]')==1
    assert b.count('.LCP0:')==1 and b.count('\t.long\topen_cfw_gx8002_audio_completion_forward')==1
    a=a[a.index('\t.global'):a.index(marker)]
    b=b[b.index('\t.global'):b.index('\t.ident')].replace('.L','.LK')
    combined='.section .text.kws_pair,"ax",@progbits\n.align 2\n'+a+'\n.size open_cfw_gx8002_audio_completion_forward, .-open_cfw_gx8002_audio_completion_forward\n.org 20\n'+b+'\n.org 212\n.LCP0:\n.long open_cfw_gx8002_audio_completion_callback\n'
    asm=out/'kws-pair.s';asm.write_text(combined)
    bindings=run['bindings'].copy();del bindings['open_cfw_gx8002_audio_completion_forward'];bindings['open_cfw_gx8002_audio_completion_callback']=0x20027b50
    script=out/'kws-pair.ld';script.write_text('SECTIONS { .text 0x100260d0 : { *(.text.kws_pair) } }\n'+''.join(f'{k} = {v:#x};\n' for k,v in bindings.items()))
    obj=out/'kws-pair.o';path=out/'kws-pair.elf';subprocess.run([pre+'as','-mcpu=ck804ef',str(asm),'-o',str(obj)],check=True);subprocess.run([pre+'ld','-T',str(script),str(obj),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'KWS pair');sections=[s for s in elf.sections if s['size'] and s['flags']&2];assert len(sections)==1;section=sections[0];data=elf.contents(section)
    assert section['address']==0x100260d0 and len(data)==216 and not elf.relocations(section['index'])
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    for name,address in (('open_cfw_gx8002_audio_completion_forward',0x100260d0),('open_cfw_gx8002_kws_run',0x100260e4)):
        assert next(s['value'] for s in elf.symbols() if s['name']==name)==address
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA and data[:20]==stock[0x180e4:0x180f8]
    assert data[212:]==(0x20027b50).to_bytes(4,'little')
    (out/'kws-pair.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'runner':run,'callback':forward,'compiler_assembly_sha256':[sha(t.encode()) for t in texts],'combined_assembly_sha256':sha(combined.encode()),'compiled_bytes':len(data),'compiled_sha256':sha(data),'bindings':bindings,'source_admitted':False,'limits':['Guarded compiler-assembly section/pool transformation; no extracted firmware instructions/data. Fixed org boundaries and linked symbols/size checked. Full runner behavior, combined call chain and ownership admission pending.']}
    (ROOT/'docs/research/gx8002-kws-pair-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(build()['compiled_bytes'])
