#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile recognition/audio shutdown and a typed callback BSS definition."""
import json,re,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
BINDINGS={'gx_snpu_exit':0x10205d40,'gx_audio_in_exit':0x10204984}
FUNCTIONS=[('LvpKwsDone',0x10206dac,0x10338,20),('LvpAudioInDone',0x102073f8,0x10984,12)]
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';deps=[]
    for rel in ('lvp/common/snpu_engine/lvp_kws.c','lvp/common/lvp_audio_in.c','include/driver/gx_snpu.h','include/driver/gx_audio_in/gx_audio_in_v2.h','LICENSE'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();deps.append({'path':rel,'blob':blob,'sha256':sha(authenticated_blob(sdk/rel,blob))})
    config=out/'stream-shutdown-config';config.mkdir(exist_ok=True);(config/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    matches=re.findall(r'int gx_audio_in_exit\(void\);',(sdk/'include/driver/gx_audio_in/gx_audio_in_v2.h').read_text())
    if len(matches)!=1:raise ValueError('stream exit interface')
    header=config/'stream-shutdown-interfaces.h';header.write_text('/* Exact authenticated upstream declaration. */\n'+matches[0]+'\n')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_stream_shutdown.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-I'+str(config),'-I'+str(sdk/'include'),'-c',str(source),'-o',str(out/'stream-shutdown-candidate.o')],check=True)
    script=out/'stream-shutdown-candidate.ld';script.write_text('SECTIONS {\n'+''.join(f'.text.{n} {a:#x} : {{ *(.text.{n}) }}\n' for n,a,o,size in FUNCTIONS)+'.bss.callback 0x20027b50 (NOLOAD) : { *(.bss.open_cfw_gx8002_snpu_callback) }\n}\n'+''.join(f'{k} = {v:#x};\n' for k,v in BINDINGS.items()))
    p=out/'stream-shutdown-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'stream-shutdown-candidate.o'),'-o',str(p)],check=True);e=Elf32(p.read_bytes(),str(p));stock=IMAGE.read_bytes();rows=[]
    if sha(stock)!=IMAGE_SHA or any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('stream shutdown stock/link')
    for n,a,o,size in FUNCTIONS:
        sec=next(s for s in e.sections if s['name']=='.text.'+n);payload=e.contents(sec)
        if e.relocations(sec['index']):raise ValueError('stream shutdown relocation')
        rows.append({'symbol':n,'section_name':sec['name'],'package_offset':o,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':size,'stock_sha256':sha(stock[o:o+size]),'fits':len(payload)<=size,'exact_stock_payload':payload==stock[o:o+size]})
    bss=next(s for s in e.sections if s['name']=='.bss.callback')
    if bss['size']!=4 or bss['address']!=0x20027b50 or bss['type']!=8:raise ValueError('callback BSS')
    (out/'stream-shutdown-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'sdk_commit':SDK_COMMIT,'dependencies':deps,'bindings':BINDINGS,'flags':flags,'source_sha256':sha(source.read_bytes()),'interface_header_sha256':sha(header.read_bytes()),'config_sha256':sha((config/'autoconf.h').read_bytes()),'regions':rows,'defined_bss':{'address':bss['address'],'size':4},'source_admitted':False,'limits':['Candidate only. Need ordered driver call/callback clear, zero return, ABI qualification. Driver exits and callback execution remain separate.']}
    (ROOT/'docs/research/gx8002-stream-shutdown-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
