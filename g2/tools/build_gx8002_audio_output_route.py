# SPDX-License-Identifier: MIT
"""Build typed mutable playback route and its source-defined name."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS

def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='drivers_lib/audio_out/v2.0/hw.o';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();data=authenticated_blob(sdk/rel,blob);oracle=Elf32(data,rel);stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Route stock identity')
    section=next(s for s in oracle.sections if s['name']=='.data');upstream=oracle.contents(section)
    if upstream[:52]!=bytes(52) or [(r['offset'],r['type'],r['addend']) for r in oracle.relocations(section['index']) if r['offset']<52]!=[(0,1,118)]:raise ValueError('SDK route layout')
    names=oracle.contents(next(s for s in oracle.sections if s['name']=='.rodata.str1.1'))
    if names[118:131]!=b'0 route play\0':raise ValueError('SDK route name')
    out=ROOT/'build/gx8002-audio-output-route';out.mkdir(parents=True,exist_ok=True);source=ROOT/'components/shared/gx8002/runtime_gx8002_audio_output_route.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(source),'-o',str(out/'bits.o')],check=True)
    (out/'bits.ld').write_text('SECTIONS { .data.aout_route 0x20026b94 : { *(.data.open_cfw_gx8002_aout_route) } .rodata.aout_route_name 0x1020aa26 : { *(.rodata.open_cfw_gx8002_aout_route_name) } }\n')
    subprocess.run([pre+'ld','-T',str(out/'bits.ld'),str(out/'bits.o'),'-o',str(out/'bits.elf')],check=True);elf=Elf32((out/'bits.elf').read_bytes(),'bits.elf');rows=[]
    allowed={'.data.aout_route','.rodata.aout_route_name'}
    if any(s['size'] and s['flags']&2 and s['name'] not in allowed for s in elf.sections):raise ValueError('Route unaccounted section')
    if any(elf.relocations(s['index']) for s in elf.sections) or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Route unresolved link')
    for name,section,offset,size,writable in (('aout_route','.data.aout_route',0x18ba8,52,True),('aout_route_name','.rodata.aout_route_name',0x13fb2,13,False)):
        sec=next(s for s in elf.sections if s['name']==section);payload=elf.contents(sec)
        if len(payload)!=size or payload!=stock[offset:offset+size] or bool(sec['flags']&1)!=writable or sec['flags']&4:raise ValueError('Route source identity/flags')
        rows.append({'symbol':'open_cfw_gx8002_'+name,'section_name':section,'compiled_bytes':size,'compiled_sha256':sha(payload),'package_offset':offset,'stock_envelope_bytes':size,'stock_sha256':sha(payload),'ownership_kind':'generated_source_data','fits':True})
    return {'functions':rows,'source_sha256':sha(source.read_bytes()),'sdk_commit':SDK_COMMIT,'oracle':{'path':rel,'blob':blob,'sha256':sha(data)},'source_admitted':False,'hardware_qualified':False,'limits':['Typed source route/name match SDK initialization and stock linked contents. Reserved fields remain explicitly unresolved. Full boot copy and driver lifecycle composition remain unqualified.']}
if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-audio-output-route-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print([(f['compiled_bytes'],f['fits']) for f in r['functions']])
