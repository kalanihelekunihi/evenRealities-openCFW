# SPDX-License-Identifier: MIT
"""Build recovered audio input IRQ; SDK binary is provenance oracle only."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS

def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');deps=[]
    for rel in ('drivers_lib/audio_in/v2.0/audio_in.o','include/driver/gx_audio_in/gx_audio_in_v2.h','include/utility/types.h'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();data=authenticated_blob(sdk/rel,blob);deps.append({'path':rel,'blob':blob,'sha256':sha(data)})
        if rel.endswith('.o'):
            oracle=Elf32(data,'SDK audio');symbol=next(s for s in oracle.symbols() if s['name']=='_AudioInISR');irq=oracle.sections[symbol['section']];assert irq['name']=='.sram_text';oracle_hash=sha(oracle.contents(irq));oracle_size=irq['size']
    source=ROOT/'components/shared/gx8002/runtime_gx8002_audio_irq.c';obj=out/'audio-irq.o';flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-I'+str(sdk/'include/driver'),'-I'+str(sdk/'include/utility'),'-c',str(source),'-o',str(obj)],check=True)
    state_source=ROOT/'components/shared/gx8002/runtime_gx8002_audio_irq_state.c';state_obj=out/'audio-irq-state.o'
    subprocess.run([pre+'gcc',*flags,'-I'+str(sdk/'include/driver'),'-I'+str(sdk/'include/utility'),'-c',str(state_source),'-o',str(state_obj)],check=True)
    script=out/'audio-irq.ld';script.write_text('SECTIONS { .text 0x10025e48 : { *(.text.open_cfw_gx8002_audio_irq) *(.text.pending) } .state 0x20027330 (NOLOAD) : { *(.bss.audio_irq_runtime) } }\nmemset = 0x102099cc;\n')
    path=out/'audio-irq.elf';subprocess.run([pre+'ld','-T',str(script),str(obj),str(state_obj),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'IRQ');sections=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(sections)==2;state=next(s for s in sections if s['name']=='.state');assert (state['address'],state['size'],state['type'],state['flags'])==(0x20027330,28,8,3);text=next(s for s in sections if s['name']=='.text');body=elf.contents(text)
    assert text['address']==0x10025e48 and len(body)<=648 and not elf.relocations(text['index']) and not any(s['name'] and s['section']==0 for s in elf.symbols())
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    relocations=oracle.relocations(irq['index']);assert [(r['offset'],r['type'],r['addend']) for r in relocations]==[(176,19,0),(366,19,0),(644,1,0)]
    assert all(oracle.symbols()[r['symbol']]['name']=='memset' for r in relocations[:2])
    pointer_symbol=oracle.symbols()[relocations[2]['symbol']];assert oracle.sections[pointer_symbol['section']]['name']=='.bss'
    excluded={i for r in relocations for i in range(r['offset'],r['offset']+4)};upstream=oracle.contents(irq);original=stock[0x17e5c:0x180e4]
    assert len(upstream)==len(original)==648 and all(a==b for i,(a,b) in enumerate(zip(upstream,original)) if i not in excluded)
    assert int.from_bytes(original[644:648],'little')==0x20027330
    (out/'audio-irq.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    r={'sdk_commit':SDK_COMMIT,'dependencies':deps,'upstream_symbol':'_AudioInISR','upstream_section_bytes':oracle_size,'upstream_section_sha256':oracle_hash,'source_sha256':sha(source.read_bytes()),'state_source_sha256':sha(state_source.read_bytes()),'flags':flags,'elf_sha256':sha(path.read_bytes()),'compiled_bytes':len(body),'compiled_sha256':sha(body),'stock_offset':0x17e5c,'stock_bytes':648,'stock_sha256':sha(stock[0x17e5c:0x180e4]),'upstream_nonrelocated_equal_bytes':636,'upstream_relocations':relocations,'source_admitted':False,'limits':['C IRQ plus compiler helper linked in original slot. SDK object authenticated for provenance only and never linked or copied. MMIO ordering, callback mutations, ABI and startup state still require decoded qualification.']}
    (ROOT/'docs/research/gx8002-audio-irq-candidate.json').write_text(json.dumps(r,indent=2)+'\n');return r
if __name__=='__main__':print(build()['compiled_bytes'])
