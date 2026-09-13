# SPDX-License-Identifier: MIT
"""Attribute retained KWS flash-loading path; no source admission."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,SDK_COMMIT,sha,authenticated_blob
from verify_gx8002_memcpy_source import decode

def analyze():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';relative='lvp/common/snpu_engine/lvp_kws.c'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+relative],text=True).strip()
    upstream=authenticated_blob(sdk/relative,blob)
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Stock identity')
    messages=[]
    for address,suffix in ((0x1020adc1,'Init Flash Failed'),(0x1020adde,'Kws Use:%d ms'),(0x1020adf7,'Read Flash Failed')):
        if suffix.encode() not in upstream:raise ValueError('Upstream diagnostic missing')
        offset=address-0x101f6a74;end=stock.index(b'\0',offset)
        if stock[offset:end] != ('[LVP_KWS ]'+suffix+'\n').encode():raise ValueError('Stock diagnostic changed')
        messages.append({'runtime_address':address,'text':stock[offset:end].decode()})
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-D','--start-address=0x1023c','--stop-address=0x1030a',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    calls=[{'package_offset':pc,'runtime_target':(int(args,0)+0x101f6a74)&0xffffffff} for pc,(op,args,w) in code.items() if op=='bsr']
    return {'stock_sha256':IMAGE_SHA,'package_offset':0x1023c,'envelope_bytes':224,
            'body_sha256':sha(stock[0x1023c:0x1031c]),'sdk_commit':SDK_COMMIT,
            'upstream':{'path':relative,'blob':blob,'sha256':sha(upstream)},'diagnostics':messages,'calls':calls,
            'source_admitted':False,'limits':['Diagnostic and call-topology attribution only; exact upstream configuration and function equivalence require qualification.',
            'Flash command/weight bytes and model semantics remain opaque; source loader alone cannot close those dependencies.']}
if __name__=='__main__':
    r=analyze();(ROOT/'docs/research/gx8002-kws-flash-load-attribution.json').write_text(json.dumps(r,indent=2)+'\n');print(len(r['calls']),'calls attributed')
