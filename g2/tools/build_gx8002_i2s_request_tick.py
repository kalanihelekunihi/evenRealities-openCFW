# SPDX-License-Identifier: MIT
"""Build the recovered I2S request tick."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    out=ROOT/'build/gx8002-i2s-request-tick';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_i2s_request_tick.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'candidate.o')],check=True)
    bindings={'open_cfw_gx8002_i2s_app':0x2002e8c4,'open_cfw_gx8002_i2s_request':0x2002e92c,'open_cfw_gx8002_i2s_mode_state':0x2002e930,'open_cfw_gx8002_i2s_poll':0x102097c8,'open_cfw_gx8002_i2s_acknowledge':0x10209770,'open_cfw_gx8002_start_i2s':0x10208ff0,'open_cfw_gx8002_stop_i2s':0x1020913c,'open_cfw_gx8002_i2s_lock':0x102077a8,'open_cfw_gx8002_i2s_unlock':0x102077d4,'open_cfw_gx8002_i2s_delay':0x10207808,'printf':0x10206c24}
    diagnostics={'request':0x1020b5a4,'lock':0x1020b5d4,'unlock':0x1020b5fb,'timeout':0x1020b624}
    script=out/'candidate.ld';script.write_text('SECTIONS { .text 0x102091bc : { *(.text.open_cfw_gx8002_i2s_request_tick) } '+''.join(f'.rodata.{n} {a:#x} : {{ *(.rodata.open_cfw_gx8002_i2s_tick_{n}) }} ' for n,a in diagnostics.items())+'}\n'+''.join(f'{n} = {a:#x};\n' for n,a in bindings.items()))
    elfpath=out/'candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'candidate.o'),'-o',str(elfpath)],check=True)
    elf=Elf32(elfpath.read_bytes(),str(elfpath));section=next(s for s in elf.sections if s['name']=='.text');stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or elf.relocations(section['index']):raise ValueError('Authentication/relocation')
    for n,a in diagnostics.items():
        s=next(s for s in elf.sections if s['name']=='.rodata.'+n);data=elf.contents(s);offset=a-0x101f6a74
        if s['address']!=a or data!=stock[offset:offset+len(data)] or elf.relocations(s['index']):raise ValueError('Diagnostic')
    (out/'candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(elfpath)],text=True))
    r={'source_sha256':sha(source.read_bytes()),'flags':flags,'compiled_bytes':section['size'],'compiled_sha256':sha(elf.contents(section)),'stock_envelope_bytes':156,'stock_sha256':sha(stock[0x12748:0x127e4]),'fits':section['size']<=156,'source_admitted':False,'limits':['Request tick candidate only; behavior, ownership and ABI require qualification.']}
    (ROOT/'docs/research/gx8002-i2s-request-tick-candidate.json').write_text(json.dumps(r,indent=2)+'\n');return r
if __name__=='__main__':print(json.dumps(build(),indent=2))
