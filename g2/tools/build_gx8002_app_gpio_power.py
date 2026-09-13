# SPDX-License-Identifier: MIT
"""Native compilation of recovered application GPIO callbacks."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    out=ROOT/'build/gx8002-app-gpio-power';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_app_gpio_power.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    functions=[('open_cfw_gx8002_app_gpio_suspend',0x12358,32),('open_cfw_gx8002_app_gpio_resume',0x12378,52)]
    flags=['-Os',*FLAGS[1:]];subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'offsets.o')],check=True)
    script=out/'offsets.ld';script.write_text('SECTIONS {\n'+''.join(f'.text.{name} {offset+0x101f6a74:#x} : {{ *(.text.{name}) }}\n' for name,offset,size in functions)+'.rodata 0x1020b43b : { *(.rodata*) } }\nopen_cfw_gx8002_gpio_disable_trigger = 0x10206074;\nopen_cfw_gx8002_padmux_set = 0x102065dc;\nopen_cfw_gx8002_gpio_set_direction = 0x10205f24;\nopen_cfw_gx8002_gpio_enable_trigger = 0x10205fb4;\nopen_cfw_gx8002_app_gpio_callback = 0x10208e20;\nprintf = 0x10206c24;\n')
    p=out/'offsets.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'offsets.o'),'-o',str(p)],check=True);e=Elf32(p.read_bytes(),str(p));stock=IMAGE.read_bytes();rows=[]
    if sha(stock)!=IMAGE_SHA:raise ValueError('Stock')
    for name,offset,size in functions:
        sec=next(s for s in e.sections if s['name']=='.text.'+name);data=e.contents(sec)
        if e.relocations(sec['index']):raise ValueError('Relocation')
        rows.append({'symbol':name,'package_offset':offset,'compiled_bytes':len(data),'compiled_sha256':sha(data),'stock_envelope_bytes':size,'stock_sha256':sha(stock[offset:offset+size]),'fits':len(data)<=size,'exact_stock_prefix':data==stock[offset:offset+len(data)]})
    (out/'offsets.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    r={'source_sha256':sha(source.read_bytes()),'flags':flags,'functions':rows,'source_admitted':False,'limits':['Application pin-six callbacks; helper order, callback ABI, shared diagnostic and ownership qualification pending.']};(ROOT/'docs/research/gx8002-app-gpio-power-candidate.json').write_text(json.dumps(r,indent=2)+'\n');return r
if __name__=='__main__':print(json.dumps(build(),indent=2))
