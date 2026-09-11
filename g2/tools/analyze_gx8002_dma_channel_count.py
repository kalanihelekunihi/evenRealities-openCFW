# SPDX-License-Identifier: MIT
"""Authenticate the initialization instructions establishing two DMA channels."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode


def analyze():
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('DMA image identity')
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('DMA wrapper identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-D','--start-address=0xd14c','--stop-address=0xd164',str(wrapper)],text=True))
    expected={0xd14e:('lrw','r4, 0x2002e93c',2),0xd152:('lsli','r3, r3, 24',2),0xd150:('movi','r3, 161',2),0xd154:('st.w','r3, (r4, 0x0)',2),0xd158:('movi','r3, 2',2),0xd15a:('st.w','r3, (r4, 0x4)',2)}
    for pc,instruction in expected.items():
        if code[pc]!=instruction:raise ValueError('DMA initialization instruction changed')
    return {'stock_sha256':IMAGE_SHA,'instruction_bytes_sha256':sha(stock[0xd14c:0xd15c]),'initializer_package_offset':0xd14c,'state_address':0x2002e93c,'device_base':0xa1000000,'channel_count_address':0x2002e940,'initialized_channel_count':2,'initialized_channel_indices':[0,1],'instructions':{hex(k):v for k,v in expected.items()},'source_admitted':False,'limits':['Static initialization evidence; call reachability and later mutation of channel count are not established. This is not proof of physical controller capacity.']}

if __name__=='__main__':
    report=analyze();(ROOT/'docs/research/gx8002-dma-channel-count.json').write_text(json.dumps(report,indent=2)+'\n');print('Initialized DMA channel count:',report['initialized_channel_count'])
