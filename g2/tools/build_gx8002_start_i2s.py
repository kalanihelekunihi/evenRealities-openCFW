# SPDX-License-Identifier: MIT
"""Native macOS build of recovered I2S application startup candidate."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
DIAGNOSTICS={'name':(0x1020b427,'start_i2s'), 'log':(0x1020b536,'[YW_APP]:%s, %d\n'), 'close_log':(0x1020b547,'[YW_APP]:%s, %d, handle = %d\n'), 'mclk':(0x1020b565,'\tMCLK:%dHz\n'), 'lrclk':(0x1020b571,'\tLRCLK:%dHz\n'), 'bits':(0x1020b57e,'\tbits:%d\n'), 'master':(0x1020b588,'I2S out Master'), 'done':(0x1020b597,'\t%s Init OK\n')}
def build():
    out=ROOT/'build/gx8002-start-i2s';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_start_i2s.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    diagnostic=out/'diagnostics.c';diagnostic.write_text('/* SPDX-License-Identifier: MIT */\n'+''.join('const char open_cfw_gx8002_start_i2s_'+n+'[] __attribute__((aligned(1)))='+json.dumps(t)+';\n' for n,(a,t) in DIAGNOSTICS.items()))
    for src,obj in ((source,'candidate.o'),(diagnostic,'diagnostics.o')):subprocess.run([pre+'gcc',*flags,'-c',str(src),'-o',str(out/obj)],check=True)
    bindings={'open_cfw_gx8002_i2s_app':0x2002e8c4,'open_cfw_gx8002_i2s_pending':0x20026d34,'printf':0x10206c24,'open_cfw_gx8002_next_range':0x10208d98}
    helpers={'close':0xe93c,'shutdown':0xeb00,'padmux':0xfb68,'clock_set':0xffe2e16c,'initialize':0xeabc,'clock_get':0xffe2e79c,'open':0xe908,'callback':0xe9dc,'mode':0xea4c,'buffer_size':0x10404,'channel':0xea84,'buffer_base':0x103f8,'buffers':0xe970,'format':0xe9a4}
    bindings.update({'open_cfw_gx8002_i2s_'+n:(a+0x101f6a74)&0xffffffff for n,a in helpers.items()})
    script=out/'candidate.ld';script.write_text('SECTIONS { .text 0x10208ff0 : { *(.text.open_cfw_gx8002_start_i2s) } '+''.join(f'.rodata.{n} {a:#x} : {{ *(.rodata.open_cfw_gx8002_start_i2s_{n}) }} ' for n,(a,t) in DIAGNOSTICS.items())+'}\n'+''.join(f'{n} = {a:#x};\n' for n,a in bindings.items()))
    path=out/'candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'candidate.o'),str(out/'diagnostics.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),str(path));stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Stock authentication')
    sections={s['name']:s for s in elf.sections};text=sections['.text'];rows=[]
    for n,(a,t) in DIAGNOSTICS.items():
        s=sections['.rodata.'+n];data=elf.contents(s);offset=a-0x101f6a74
        if s['address']!=a or data!=stock[offset:offset+len(data)] or data!=t.encode()+b'\0':raise ValueError('Diagnostic')
        rows.append({'name':n,'address':a,'bytes':len(data),'sha256':sha(data)})
    if any(elf.relocations(s['index']) for s in elf.sections if s['flags']&2):raise ValueError('Relocations')
    (out/'candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    r={'source_sha256':sha(source.read_bytes()),'flags':flags,'compiled_bytes':text['size'],'compiled_sha256':sha(elf.contents(text)),'stock_envelope_bytes':332,'stock_sha256':sha(stock[0x1257c:0x126c8]),'fits':text['size']<=332,'diagnostics':rows,'bindings':bindings,'source_admitted':False,'limits':['Linked candidate only; decoded behavior, helper mutations, ownership and ABI qualification outstanding.']}
    (ROOT/'docs/research/gx8002-start-i2s-candidate.json').write_text(json.dumps(r,indent=2)+'\n');return r
if __name__=='__main__':print(json.dumps(build(),indent=2))
