# SPDX-License-Identifier: MIT
"""Build the recovered I2S stop routine."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    out=ROOT/'build/gx8002-stop-i2s';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_stop_i2s.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'candidate.o')],check=True)
    bindings={'open_cfw_gx8002_i2s_app':0x2002e8c4,'open_cfw_gx8002_i2s_pending':0x20026d34,'open_cfw_gx8002_i2s_padmux':0x102065dc,'open_cfw_gx8002_i2s_close':0x102053b0,'open_cfw_gx8002_i2s_shutdown':0x10205574,'open_cfw_gx8002_start_i2s_log':0x1020b536,'open_cfw_gx8002_start_i2s_close_log':0x1020b547,'printf':0x10206c24}
    script=out/'candidate.ld';script.write_text('SECTIONS { .text 0x1020913c : { *(.text.open_cfw_gx8002_stop_i2s) } .rodata.name 0x1020b431 : { *(.rodata.open_cfw_gx8002_stop_i2s_name) } }\n'+''.join(f'{n} = {a:#x};\n' for n,a in bindings.items()))
    elfpath=out/'candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'candidate.o'),'-o',str(elfpath)],check=True)
    elf=Elf32(elfpath.read_bytes(),str(elfpath));section=next(s for s in elf.sections if s['name']=='.text');stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or elf.relocations(section['index']):raise ValueError('Authentication/relocation')
    (out/'candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(elfpath)],text=True))
    r={'source_sha256':sha(source.read_bytes()),'flags':flags,'compiled_bytes':section['size'],'compiled_sha256':sha(elf.contents(section)),'stock_envelope_bytes':128,'stock_sha256':sha(stock[0x126c8:0x12748]),'fits':section['size']<=128,'source_admitted':False,'limits':['Stop candidate only; shared diagnostics owned by I2S start; behavior, ownership and ABI require qualification.']}
    (ROOT/'docs/research/gx8002-stop-i2s-candidate.json').write_text(json.dumps(r,indent=2)+'\n');return r
if __name__=='__main__':print(json.dumps(build(),indent=2))
