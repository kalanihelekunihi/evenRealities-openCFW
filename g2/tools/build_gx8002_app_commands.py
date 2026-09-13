# SPDX-License-Identifier: MIT
"""Build the recovered application command registration."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    out=ROOT/'build/gx8002-app-commands';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_app_commands.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'candidate.o')],check=True)
    bindings={'memset':0x102099cc,'open_cfw_gx8002_app_command_callback':0x10209430,'open_cfw_gx8002_app_register_command':0x102082ac,'open_cfw_gx8002_app_command_buffer':0x2002e8f0}
    diagnostics={'mic':0x1020b698,'gsensor':0x1020b6a3,'version':0x1020b6b2,'beamforming':0x1020b6ba,'vad_open':0x1020b6c8,'vad_close':0x1020b6db,'gain':0x1020b6ef,'dmic_start':0x1020b6fc,'dmic_close':0x1020b70b,'pdm_delay':0x1020b71a,'i2s_state':0x1020b727}
    script=out/'candidate.ld';script.write_text('SECTIONS { .text 0x10209258 : { *(.text.open_cfw_gx8002_app_commands) } '+''.join(f'.rodata.{n} {a:#x} : {{ *(.rodata.open_cfw_gx8002_command_{n}) }} ' for n,a in diagnostics.items())+'}\n'+''.join(f'{n} = {a:#x};\n' for n,a in bindings.items()))
    elfpath=out/'candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'candidate.o'),'-o',str(elfpath)],check=True)
    elf=Elf32(elfpath.read_bytes(),str(elfpath));section=next(s for s in elf.sections if s['name']=='.text');stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or elf.relocations(section['index']):raise ValueError('Authentication/relocation')
    for n,a in diagnostics.items():
        s=next(s for s in elf.sections if s['name']=='.rodata.'+n);data=elf.contents(s);offset=a-0x101f6a74
        if s['address']!=a or data!=stock[offset:offset+len(data)] or elf.relocations(s['index']):raise ValueError('Diagnostic')
    (out/'candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(elfpath)],text=True))
    r={'source_sha256':sha(source.read_bytes()),'flags':flags,'compiled_bytes':section['size'],'compiled_sha256':sha(elf.contents(section)),'stock_envelope_bytes':388,'stock_sha256':sha(stock[0x127e4:0x12968]),'fits':section['size']<=388,'source_admitted':False,'limits':['Application commands candidate only; behavior, ownership and ABI require qualification.']}
    (ROOT/'docs/research/gx8002-app-commands-candidate.json').write_text(json.dumps(r,indent=2)+'\n');return r
if __name__=='__main__':print(json.dumps(build(),indent=2))
