# SPDX-License-Identifier: MIT
"""Authenticate the observed PDM delay command call site and diagnostic."""
import json,subprocess
from build_gx8002_audio_channel_field import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode

def analyze():
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('PDM delay image identity')
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('PDM delay wrapper identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-D','--start-address=0x12bae','--stop-address=0x12bca',str(wrapper)],text=True))
    expected={0x12bae:('ld.h','r3, (r4, 0x4)'),0x12bb0:('cmpnei','r3, 270'),0x12bb4:('bt','0x12bde'),0x12bb6:('lrw','r0, 0x1020b86f'),0x12bbe:('movi','r1, 1'),0x12bc0:('movi','r0, 0'),0x12bc6:('bsr','0xdf3c')}
    for pc,want in expected.items():
        if code[pc][:2]!=want:raise ValueError('PDM delay caller changed '+hex(pc))
    offset=0x1020b86f-0x101f6a74;message=stock[offset:stock.index(0,offset)].decode('ascii')
    if message!='receive set pdm ch delay req\n':raise ValueError('PDM diagnostic changed')
    pointers=[];needle=(0x102049b0).to_bytes(4,'little');start=0
    while True:
        at=stock.find(needle,start)
        if at<0:break
        pointers.append(at);start=at+1
    return {'stock_sha256':IMAGE_SHA,'caller_package_offset':0x12bc6,'command':270,'diagnostic':message,'arguments':{'index':0,'value':1},'resulting_register':0xa0a00028,'field_bits':[15,10],'literal_function_pointer_occurrences':pointers,'inference':'Observed command identifies this helper as PDM channel delay programming. Only index0/value1 established at this direct call site.','limits':['Literal scan cannot exclude computed indirect calls. Other indices remain arithmetic behavior evidence, not hardware register-domain qualification.']}
if __name__=='__main__':
    r=analyze();(ROOT/'docs/research/gx8002-audio-channel-field-analysis.json').write_text(json.dumps(r,indent=2)+'\n');print(r['inference'])
