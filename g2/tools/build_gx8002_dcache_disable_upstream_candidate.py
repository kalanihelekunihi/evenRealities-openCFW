#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link pinned upstream CSI cache-disable C; no source admission."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
BINDINGS={}
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';rel='arch/soc/grus/include/core_ck804.h';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();oracle=authenticated_blob(sdk/rel,blob)
    header_rel='include/driver/gx_dcache.h';header_blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+header_rel],text=True).strip();header=authenticated_blob(sdk/header_rel,header_blob)
    from verify_gx8002_csi_source import HEADERS
    dependencies=[]
    for name in (*HEADERS,'LICENSE'):
        digest=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+name],text=True).strip()
        data=authenticated_blob(sdk/name,digest);dependencies.append({'path':name,'git_blob':digest,'sha256':sha(data)})
    source=ROOT/'components/shared/gx8002/runtime_gx8002_dcache_disable_upstream.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,*sum((['-isystem',str(sdk/p)] for p in ('arch/soc/grus/include','include/utility','include/utility/libc')),[]),'-c',str(source),'-o',str(out/'dcache-disable-upstream-candidate.o')],check=True)
    script=out/'dcache-disable-upstream-candidate.ld';script.write_text('SECTIONS { .text 0x100255e4 : { *(.text.open_cfw_gx8002_dcache_disable_upstream) } }\n'+''.join(f'{k} = {v:#x};\n' for k,v in BINDINGS.items()))
    p=out/'dcache-disable-upstream-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'dcache-disable-upstream-candidate.o'),'-o',str(p)],check=True);e=Elf32(p.read_bytes(),str(p));sec=next(s for s in e.sections if s['name']=='.text');payload=e.contents(sec);stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or e.relocations(sec['index']) or any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('upstream cache-disable stock/link')
    (out/'dcache-disable-upstream-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'upstream_dependencies':dependencies,'sdk_commit':SDK_COMMIT,'oracle':{'path':rel,'blob':blob,'sha256':sha(oracle),'role':'unmodified upstream C implementation'},'header':{'path':header_rel,'blob':header_blob,'sha256':sha(header)},'bindings':BINDINGS,'flags':flags,'source_sha256':sha(source.read_bytes()),'symbol':'open_cfw_gx8002_dcache_disable_upstream','section_name':'.text','package_offset':0x175f8,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':36,'stock_sha256':sha(stock[0x175f8:0x1761c]),'fits':len(payload)<=36,'source_admitted':False,'limits':['Build evidence only. Decoded barrier/MMIO/ABI and caller integration qualification required. No hardware cache coherence qualification.']}
    (ROOT/'docs/research/gx8002-dcache-disable-upstream-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
