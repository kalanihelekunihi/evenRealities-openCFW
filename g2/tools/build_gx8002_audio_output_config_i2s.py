# SPDX-License-Identifier: MIT
"""Build public DAC wrapper with authenticated upstream call relocation."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS
FUNCTIONS=(('aout_config_i2s',0xe1f0),)
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='drivers_lib/audio_out/v2.0/hw.o'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
    data=authenticated_blob(sdk/rel,blob);oracle=Elf32(data,rel);stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Aout bits stock identity')
    out=ROOT/'build/gx8002-audio-output-config-i2s';out.mkdir(parents=True,exist_ok=True)
    header='include/driver/gx_audio_out/gx_audio_out_v2.h'
    header_blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+header],text=True).strip()
    authenticated_blob(sdk/header,header_blob)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_audio_output_config_i2s.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-I'+str(sdk/'include/driver'),'-Os',*FLAGS[1:],'-c',str(source),'-o',str(out/'bits.o')],check=True)
    script='SECTIONS {\n'+''.join(f' .text.{name} {offset+0x101f6a74:#x} : {{ *(.text.open_cfw_gx8002_{name}) }}\n' for name,offset in FUNCTIONS)+'}\nopen_cfw_gx8002_aout_i2s_config = 0x10204ab0;\nopen_cfw_gx8002_aout_set_lodac = 0x10204b5c;\n'
    (out/'bits.ld').write_text(script)
    subprocess.run([pre+'ld','-T',str(out/'bits.ld'),str(out/'bits.o'),'-o',str(out/'bits.elf')],check=True)
    elf=Elf32((out/'bits.elf').read_bytes(),'bits.elf');rows=[]
    if any(elf.relocations(s['index']) for s in elf.sections) or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Aout unresolved link')
    for name,offset in FUNCTIONS:
        section=next(s for s in oracle.sections if s['name']=='.text.'+name)
        if section['size']!=44:raise ValueError('Upstream wrapper size changed')
        relocations=oracle.relocations(section['index'])
        if [(r['offset'],r['type']) for r in relocations]!=[(26,19),(30,19)]:raise ValueError('DAC wrapper relocation changed')
        upstream=oracle.contents(section);baseline=stock[offset:offset+44]
        if upstream[:26]!=baseline[:26] or upstream[34:]!=baseline[34:]:raise ValueError('DAC wrapper nonrelocated bytes changed')
        payload=elf.contents(next(s for s in elf.sections if s['name']=='.text.'+name))
        rows.append({'symbol':'open_cfw_gx8002_'+name,'section_name':'.text.'+name,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'package_offset':offset,'stock_envelope_bytes':44,'stock_sha256':sha(stock[offset:offset+44]),'fits':len(payload)<=44})
    (out/'bits.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'bits.elf')],text=True))
    return {'functions':rows,'source_sha256':sha(source.read_bytes()),'sdk_commit':SDK_COMMIT,'header':{'path':header,'blob':header_blob},'oracle':{'path':rel,'blob':blob,'sha256':sha(data),'role':'identity_evidence_only'},'source_admitted':False,'hardware_qualified':False}
if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-audio-output-config-i2s-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print([(f['compiled_bytes'],f['fits']) for f in r['functions']])
