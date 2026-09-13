# SPDX-License-Identifier: MIT
"""Build the recovered notification setup."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    out=ROOT/'build/gx8002-notification-setup';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_notification_setup.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'candidate.o')],check=True)
    bindings={'open_cfw_gx8002_notification_gpio_value':0x10205f88,'open_cfw_gx8002_notification_gpio_direction':0x10205f24,'open_cfw_gx8002_notification_uart_done':0x1020854c,'open_cfw_gx8002_notification_uart_init':0x10208458,'open_cfw_gx8002_app_commands':0x10209258,'memcpy':0x10025738,'printf':0x10206c24,'open_cfw_gx8002_notification_log':0x1020b460}
    diagnostics={'pin':0x1020b8bc,'uart':0x1020b8d7,'bundle':0x1020b678}
    script=out/'candidate.ld';script.write_text('SECTIONS { .text 0x102096fc : { *(.text.open_cfw_gx8002_notification_setup) } '+''.join(f'.rodata.{n} {a:#x} : {{ *(.rodata.open_cfw_gx8002_notification_{n}) }} ' for n,a in diagnostics.items())+'}\n'+''.join(f'{n} = {a:#x};\n' for n,a in bindings.items()))
    elfpath=out/'candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'candidate.o'),'-o',str(elfpath)],check=True)
    elf=Elf32(elfpath.read_bytes(),str(elfpath));section=next(s for s in elf.sections if s['name']=='.text');stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or elf.relocations(section['index']):raise ValueError('Authentication/relocation')
    for n,a in diagnostics.items():
        s=next(s for s in elf.sections if s['name']=='.rodata.'+n);data=elf.contents(s);offset=a-0x101f6a74
        if s['address']!=a or data!=stock[offset:offset+len(data)] or elf.relocations(s['index']):raise ValueError('Diagnostic')
    (out/'candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(elfpath)],text=True))
    r={'source_sha256':sha(source.read_bytes()),'flags':flags,'compiled_bytes':section['size'],'compiled_sha256':sha(elf.contents(section)),'stock_envelope_bytes':96,'stock_sha256':sha(stock[0x12c88:0x12ce8]),'fits':section['size']<=96,'source_admitted':False,'limits':['Notification setup candidate only; behavior, ownership and ABI require qualification.']}
    (ROOT/'docs/research/gx8002-notification-setup-candidate.json').write_text(json.dumps(r,indent=2)+'\n');return r
if __name__=='__main__':print(json.dumps(build(),indent=2))
