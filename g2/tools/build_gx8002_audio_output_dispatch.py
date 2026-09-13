# SPDX-License-Identifier: MIT
"""Build named dispatch relocations, requiring admitted source targets."""
import json,re,struct,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS

def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='drivers_lib/audio_out/v2.0/hw.o';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();data=authenticated_blob(sdk/rel,blob);oracle=Elf32(data,rel);stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Dispatch stock identity')
    names=('alloc_playback','init','exit','suspend','resume','free','config_buffer','config_pcm','config_i2s','config_dac','config_cb','push_frame',None,'drain_frame','set_db','get_db','set_mute','get_mute','set_channel','set_fixed_src','get_sdc_addr')
    data_section=next(s for s in oracle.sections if s['name']=='.data');relocations=[r for r in oracle.relocations(data_section['index']) if r['offset']>=52];symbols=oracle.symbols()
    if len(relocations)!=20:raise ValueError('Dispatch relocation count')
    for relocation,(slot,name) in zip(relocations,((i,n) for i,n in enumerate(names) if n)):
        if relocation['offset']!=52+slot*4 or relocation['type']!=1 or relocation['addend']!=0 or oracle.sections[symbols[relocation['symbol']]['section']]['name']!='.text.aout_'+name or symbols[relocation['symbol']]['value']!=0:raise ValueError('Dispatch SDK target')
    addresses=struct.unpack_from('<21I',stock,0x18bdc)
    if addresses[12]!=0:raise ValueError('Dispatch null slot')
    admissions={}
    for filename in set(re.findall(r"'(gx8002-[^']+\.json)'",(ROOT/'tools/build_gx8002_source_candidate.py').read_text())):
        path=ROOT/'docs/research'/filename
        if not path.exists():continue
        report=json.loads(path.read_text())
        if not report.get('source_admitted'):continue
        for row in report.get('functions',[report]):
            for occurrence in row.get('stock_occurrences',[]):
                admissions[(row.get('symbol'),occurrence['package_offset']+0x101f6a74)]=(filename,sha(path.read_bytes()))
    bindings=[]
    for name,address in zip(names,addresses):
        if name:
            symbol='open_cfw_gx8002_aout_'+name
            if (symbol,address) not in admissions:raise ValueError(('Dispatch target lacks source admission',symbol,hex(address)))
            evidence,digest=admissions[(symbol,address)];bindings.append({'symbol':symbol,'address':address,'report':evidence,'report_sha256':digest})
    out=ROOT/'build/gx8002-audio-output-dispatch';out.mkdir(parents=True,exist_ok=True);source=ROOT/'components/shared/gx8002/runtime_gx8002_audio_output_dispatch.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-I'+str(sdk/'include/driver'),'-Os',*FLAGS[1:],'-c',str(source),'-o',str(out/'bits.o')],check=True)
    script='SECTIONS { .data.aout_dispatch 0x20026bc8 : { *(.data*) } }\n'+''.join(f"{b['symbol']} = {b['address']:#x};\n" for b in bindings)
    (out/'bits.ld').write_text(script);subprocess.run([pre+'ld','-T',str(out/'bits.ld'),str(out/'bits.o'),'-o',str(out/'bits.elf')],check=True);elf=Elf32((out/'bits.elf').read_bytes(),'bits.elf')
    if any(s['size'] and s['flags']&2 and s['name']!='.data.aout_dispatch' for s in elf.sections):raise ValueError('Unaccounted dispatch section')
    if any(elf.relocations(s['index']) for s in elf.sections) or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Unresolved dispatch')
    section=next(s for s in elf.sections if s['name']=='.data.aout_dispatch');payload=elf.contents(section)
    if payload!=stock[0x18bdc:0x18c30] or not section['flags']&1 or section['flags']&4:raise ValueError('Dispatch source bytes/flags')
    return {'functions':[{'symbol':'open_cfw_gx8002_aout_dispatch','section_name':section['name'],'compiled_bytes':84,'compiled_sha256':sha(payload),'package_offset':0x18bdc,'stock_envelope_bytes':84,'stock_sha256':sha(payload),'ownership_kind':'generated_source_data','fits':True}],'bindings':bindings,'source_sha256':sha(source.read_bytes()),'sdk_commit':SDK_COMMIT,'oracle':{'path':rel,'blob':blob,'sha256':sha(data)},'source_admitted':False,'hardware_qualified':False}
if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-audio-output-dispatch-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print('Dispatch84 bytes;20 admitted source targets')
