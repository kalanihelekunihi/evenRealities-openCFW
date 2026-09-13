# SPDX-License-Identifier: MIT
"""Build source audio-output bit setters, authenticate exact upstream matches."""
import json,subprocess,struct
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS
FUNCTIONS=(('aout_set_lodac',0xe0e8),)
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='drivers_lib/audio_out/v2.0/hw.o'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
    data=authenticated_blob(sdk/rel,blob);oracle=Elf32(data,rel);stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Aout bits stock identity')
    targets=struct.unpack_from('<7I',stock,0x1020a8f4-0x101f6a74)
    if tuple(a-0x101f6a74 for a in targets)!=(0xe1ca,0xe1d0,0xe12c,0xe1d6,0xe1dc,0xe1e2,0xe1e8):raise ValueError('Lodac switch targets changed')
    out=ROOT/'build/gx8002-audio-output-lodac';out.mkdir(parents=True,exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_audio_output_lodac.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-fno-jump-tables','-fno-tree-switch-conversion','-Os',*FLAGS[1:],'-c',str(source),'-o',str(out/'bits.o')],check=True)
    script='SECTIONS {\n'+''.join(f' .text.{name} {offset+0x101f6a74:#x} : {{ *(.text.open_cfw_gx8002_{name}) *(.text*) }}\n' for name,offset in FUNCTIONS)+'}\n'
    (out/'bits.ld').write_text(script)
    subprocess.run([pre+'ld','-T',str(out/'bits.ld'),str(out/'bits.o'),'-o',str(out/'bits.elf')],check=True)
    elf=Elf32((out/'bits.elf').read_bytes(),'bits.elf');rows=[]
    if any(elf.relocations(s['index']) for s in elf.sections) or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Aout unresolved link')
    if any(s['size'] and s['flags']&2 and s['name'] not in {'.text.'+name for name,offset in FUNCTIONS} for s in elf.sections):raise ValueError('Unaccounted allocated lodac section')
    for name,offset in FUNCTIONS:
        section=next(s for s in oracle.sections if s['name']=='.text._set_lodac')
        if section['size']!=262:raise ValueError('Upstream lodac size changed')
        payload=elf.contents(next(s for s in elf.sections if s['name']=='.text.'+name))
        rows.append({'symbol':'open_cfw_gx8002_'+name,'section_name':'.text.'+name,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'package_offset':offset,'stock_envelope_bytes':264,'stock_sha256':sha(stock[offset:offset+264]),'fits':len(payload)<=264})
    (out/'bits.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'bits.elf')],text=True))
    return {'functions':rows,'source_sha256':sha(source.read_bytes()),'stock_switch_targets':list(targets),'sdk_commit':SDK_COMMIT,'oracle':{'path':rel,'blob':blob,'sha256':sha(data),'role':'identity_evidence_only'},'source_admitted':False,'hardware_qualified':False}
if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-audio-output-lodac-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print([(f['compiled_bytes'],f['fits']) for f in r['functions']])
