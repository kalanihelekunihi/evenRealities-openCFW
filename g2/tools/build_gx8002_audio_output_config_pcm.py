# SPDX-License-Identifier: MIT
"""Build PCM configuration and its source-authored diagnostic with authenticated upstream call relocation."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS
FUNCTIONS=(('aout_config_pcm',0xe2c4),)
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='drivers_lib/audio_out/v2.0/hw.o'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
    data=authenticated_blob(sdk/rel,blob);oracle=Elf32(data,rel);stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('PCM configuration stock identity')
    out=ROOT/'build/gx8002-audio-output-config-pcm';out.mkdir(parents=True,exist_ok=True)
    header='include/driver/gx_audio_out/gx_audio_out_v2.h'
    header_blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+header],text=True).strip()
    authenticated_blob(sdk/header,header_blob)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_audio_output_config_pcm.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-I'+str(sdk/'include/driver'),'-fno-jump-tables','-fno-tree-switch-conversion','-Os',*FLAGS[1:],'-c',str(source),'-o',str(out/'bits.o')],check=True)
    script='SECTIONS {\n'+''.join(f' .text.{name} {offset+0x101f6a74:#x} : {{ *(.text*) }}\n' for name,offset in FUNCTIONS)+' .rodata.aout_pcm_clock_diagnostic 0x1020a9b0 : { *(.rodata.aout_pcm_clock_diagnostic) }\n}\nprintf_ = 0x10206c24;\nopen_cfw_gx8002_aout_i2s_config = 0x10204ab0;\nopen_cfw_gx8002_aout_dac_config = 0x102049e8;\nopen_cfw_gx8002_aout_lodac = 0x10204b5c;\n'
    (out/'bits.ld').write_text(script)
    subprocess.run([pre+'ld','-T',str(out/'bits.ld'),str(out/'bits.o'),'-o',str(out/'bits.elf')],check=True)
    elf=Elf32((out/'bits.elf').read_bytes(),'bits.elf');rows=[]
    if any(s['size'] and s['flags']&2 and s['name'] not in ('.text.aout_config_pcm','.rodata.aout_pcm_clock_diagnostic') for s in elf.sections):raise ValueError('Unaccounted allocated section')
    if any(elf.relocations(s['index']) for s in elf.sections) or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Aout unresolved link')
    for name,offset in FUNCTIONS:
        section=next(s for s in oracle.sections if s['name']=='.text.'+name)
        if section['size']!=308:raise ValueError('Upstream wrapper size changed')
        relocations=oracle.relocations(section['index'])
        if [(r['offset'],r['type']) for r in relocations]!=[(50,19),(210,19),(222,19),(226,19),(304,1)]:raise ValueError('PCM configuration relocation changed')
        upstream=oracle.contents(section);baseline=stock[offset:offset+308]
        skip={i for r in relocations for i in range(r['offset'],r['offset']+4)}
        if any(v!=baseline[i] for i,v in enumerate(upstream) if i not in skip):raise ValueError('PCM configuration nonrelocated bytes changed')
        payload=elf.contents(next(s for s in elf.sections if s['name']=='.text.'+name))
        rows.append({'symbol':'open_cfw_gx8002_'+name,'section_name':'.text.'+name,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'package_offset':offset,'stock_envelope_bytes':308,'stock_sha256':sha(stock[offset:offset+308]),'fits':len(payload)<=308})
    diagnostic=elf.contents(next(s for s in elf.sections if s['name']=='.rodata.aout_pcm_clock_diagnostic'))
    if not diagnostic.endswith(b'\0') or diagnostic!=stock[0x13f3c:0x13f3c+len(diagnostic)]:raise ValueError('Source diagnostic differs from stock')
    rows.append({'symbol':'open_cfw_gx8002_aout_pcm_clock_diagnostic','section_name':'.rodata.aout_pcm_clock_diagnostic','compiled_bytes':len(diagnostic),'compiled_sha256':sha(diagnostic),'package_offset':0x13f3c,'stock_envelope_bytes':len(diagnostic),'stock_sha256':sha(diagnostic),'ownership_kind':'generated_source_data','fits':True})
    (out/'bits.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'bits.elf')],text=True))
    return {'functions':rows,'source_sha256':sha(source.read_bytes()),'sdk_commit':SDK_COMMIT,'header':{'path':header,'blob':header_blob},'oracle':{'path':rel,'blob':blob,'sha256':sha(data),'role':'identity_evidence_only'},'source_admitted':False,'hardware_qualified':False,'limits':['Candidate includes independently accounted source text and diagnostic data. Decoded behavior is not yet qualified.']}
if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-audio-output-config-pcm-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print([(f['compiled_bytes'],f['fits']) for f in r['functions']])
