#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link source-authored PCM channel setting at its original entry, without SDK payload."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
ADDRESS=0x10203dc8
OFFSET=0xd354
SIZE=80

def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';rel='drivers_lib/audio_in/v2.0/audio_in.o'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();oracle=authenticated_blob(sdk/rel,blob)
    oe=Elf32(oracle,rel);os=next(s for s in oe.sections if s['name']=='.text._pcm_channel_setting.isra.0');stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or oe.relocations(os['index']) or oe.contents(os)!=stock[OFFSET:OFFSET+78] or stock[OFFSET+78:OFFSET+SIZE]!=bytes(2):raise ValueError('PCM channel setting identity')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_pcm_channel_setting.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'pcm-channel-setting-candidate.o')],check=True)
    script=out/'pcm-channel-setting-candidate.ld';script.write_text('SECTIONS { .text 0x10203dc8 : { *(.text.open_cfw_gx8002_pcm_channel_setting) } }\n')
    p=out/'pcm-channel-setting-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'pcm-channel-setting-candidate.o'),'-o',str(p)],check=True)
    e=Elf32(p.read_bytes(),str(p));sec=next(s for s in e.sections if s['name']=='.text');payload=e.contents(sec)
    if e.relocations(sec['index']) or any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('PCM channel setting link')
    (out/'pcm-channel-setting-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'sdk_commit':SDK_COMMIT,'oracle':{'path':rel,'blob':blob,'sha256':sha(oracle),'role':'identity_only'},'source_sha256':sha(source.read_bytes()),'flags':flags,'symbol':'open_cfw_gx8002_pcm_channel_setting','section_name':'.text','package_offset':OFFSET,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':SIZE,'stock_sha256':sha(stock[OFFSET:OFFSET+SIZE]),'fits':len(payload)<=SIZE,'source_admitted':False,'limits':['Candidate only. Alignment rejection, ordered parameter writes, channel enable and ABI comparison required. No SDK object payload linked.']}
    (ROOT/'docs/research/gx8002-pcm-channel-setting-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
