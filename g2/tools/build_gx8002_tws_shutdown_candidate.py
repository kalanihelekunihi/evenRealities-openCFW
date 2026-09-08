#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build TWS shutdown and buffer wrapper; admission requires separate comparison."""
import json,re,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
BINDINGS={'memset':0x102099cc,'printf':0x10206c24,'LvpKwsDone':0x10206dac,'LvpAudioInDone':0x102073f8,'LvpInitBuffer':0x10206dc0,'open_cfw_gx8002_tws_queue':0x2002e6ec}
REGIONS=[('buffer','open_cfw_gx8002_tws_buffer_init',0x10208644,8),('done','open_cfw_gx8002_tws_done',0x1020864c,36),('message','open_cfw_gx8002_tws_exit',0x1020b218,24)]
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';deps=[]
    for rel in ('lvp/lvp_mode_tws.c','lvp/lvp_mode.h','lvp/common/lvp_queue.h','lvp/common/snpu_engine/lvp_kws.h','lvp/common/lvp_audio_in.h','include/lvp_buffer.h','LICENSE'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();deps.append({'path':rel,'blob':blob,'sha256':sha(authenticated_blob(sdk/rel,blob))})
    excerpts=[]
    for rel,name in [('lvp/common/snpu_engine/lvp_kws.h','LvpKwsDone'),('lvp/common/lvp_audio_in.h','LvpAudioInDone'),('include/lvp_buffer.h','LvpInitBuffer')]:
        matches=re.findall(r'int '+name+r'\(void\);',(sdk/rel).read_text())
        if len(matches)!=1:raise ValueError('TWS shutdown interface')
        excerpts.extend(matches)
    header=out/'tws-shutdown-interfaces.h';header.write_text('/* Exact authenticated upstream interfaces. */\n'+'\n'.join(excerpts)+'\n')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_tws_shutdown.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-I'+str(out),'-I'+str(sdk/'lvp'),'-c',str(source),'-o',str(out/'tws-shutdown-candidate.o')],check=True)
    script=out/'tws-shutdown-candidate.ld';script.write_text('SECTIONS {\n'+''.join(f'.{n} {a:#x} : {{ *(.{"rodata" if n=="message" else "text"}.{symbol}) }}\n' for n,symbol,a,size in REGIONS)+'}\n'+''.join(f'{k} = {v:#x};\n' for k,v in BINDINGS.items()))
    p=out/'tws-shutdown-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'tws-shutdown-candidate.o'),'-o',str(p)],check=True);e=Elf32(p.read_bytes(),str(p));stock=IMAGE.read_bytes();rows=[]
    if sha(stock)!=IMAGE_SHA or any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('TWS shutdown stock/link')
    for name,symbol,address,size in REGIONS:
        sec=next(s for s in e.sections if s['name']=='.'+name);payload=e.contents(sec);offset=address-0x101f6a74
        if e.relocations(sec['index']):raise ValueError('TWS shutdown relocation')
        rows.append({'symbol':symbol,'section_name':sec['name'],'package_offset':offset,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':size,'stock_sha256':sha(stock[offset:offset+size]),'fits':len(payload)<=size,'exact_stock_payload':payload==stock[offset:offset+size]})
    (out/'tws-shutdown-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'sdk_commit':SDK_COMMIT,'dependencies':deps,'bindings':BINDINGS,'flags':flags,'source_sha256':sha(source.read_bytes()),'interface_header_sha256':sha(header.read_bytes()),'regions':rows,'source_admitted':False,'limits':['Candidate only. Need ordered memset/KWS/audio/logging calls and buffer return propagation, frame and ABI comparison. Downstream shutdown and buffer helpers remain retained.']}
    (ROOT/'docs/research/gx8002-tws-shutdown-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
