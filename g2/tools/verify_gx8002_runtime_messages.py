# SPDX-License-Identifier: MIT
"""Recover SDK diagnostics from authenticated source, never from firmware bytes."""
import json,re,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,SDK_COMMIT,authenticated_blob,sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS
SPECS=[('stack',0x1465f,'lvp/common/lvp_system_init.c',[
' The Stack Scope:[%#x - %#x], Stack Size:%x\n',
'Error, The Stack May Used Up, Top[%#x],[Addr:%#x, Value:%#x]\n']),
('tws',0x147bc,'lvp/lvp_mode_tws.c',['LvpAudioInInit Failed\n','Ctx:%d, Vad:%d, Ns:%d, R:%d\n']),
('kws',0x148db,'lvp/vui/kws/kws_strategy.c',['==ERROR== Array [activation_kws] overflow\n'])]

def verify():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-runtime-messages';out.mkdir(exist_ok=True)
    source='/* Diagnostic definitions derived from the authenticated NationalChip SDK. See LICENSE. */\n';deps={};expected={};script='SECTIONS {\n'
    for name,offset,path,strings in SPECS:
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+path],text=True).strip()
        raw=authenticated_blob(sdk/path,blob);text=raw.decode();deps[path]={'git_blob':blob,'sha256':sha(raw)}
        tag=json.loads(re.search(r'#define LOG_TAG\s+("[^"]*")',text)[1]);data=b''
        for index,s in enumerate(strings):
            literal=json.dumps(s);assert literal in text,('Missing upstream literal',path,literal)
            value=tag+s;data+=value.encode()+b'\0'
            source+=f'__attribute__((section(".rodata.{name}.{index}"),aligned(1))) const char message_{name}_{index}[] = {json.dumps(value)};\n'
        expected[name]=(offset,data);script+=f'.rodata.{name} {offset+0x101f6a74:#x} : {{ '+''.join(f'*(.rodata.{name}.{i}) ' for i in range(len(strings)))+'}\n'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':LICENSE'],text=True).strip();license=authenticated_blob(sdk/'LICENSE',blob);(out/'LICENSE').write_bytes(license)
    (out/'candidate.c').write_text(source);(out/'candidate.ld').write_text(script+'}\n');pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc',*FLAGS,'-c',str(out/'candidate.c'),'-o',str(out/'candidate.o')],check=True)
    subprocess.run([pre+'ld','-T',str(out/'candidate.ld'),str(out/'candidate.o'),'-o',str(out/'candidate.elf')],check=True)
    elf=Elf32((out/'candidate.elf').read_bytes(),'messages');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA;rows=[]
    sections=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(sections)==len(expected)
    for s in sections:
        name=s['name'].split('.')[-1];offset,data=expected[name]
        assert not s['flags']&4 and not elf.relocations(s['index']) and s['address']==offset+0x101f6a74
        assert elf.contents(s)==data==stock[offset:offset+len(data)]
        rows.append({'symbol':'open_cfw_gx8002_messages_'+name,'section_name':s['name'],'ownership_kind':'generated_source_data','compiled_bytes':len(data),'compiled_sha256':sha(data),'stock_occurrences':[{'symbol':'open_cfw_gx8002_messages_'+name,'package_offset':offset,'bytes':len(data),'sha256':sha(data),'region':'image_a_xip_text'}]})
    return {'functions':rows,'sdk_commit':SDK_COMMIT,'dependencies':deps,'source_sha256':sha(source.encode()),'license_sha256':sha(license),'source_admitted':False,'limits':['Diagnostic strings and formatting only; caller behavior remains separately qualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-runtime-messages-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(sum(x['compiled_bytes'] for x in r['functions']))
