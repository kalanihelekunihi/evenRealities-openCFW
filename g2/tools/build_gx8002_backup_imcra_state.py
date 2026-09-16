# SPDX-License-Identifier: MIT
"""Build the full initializer candidate and authored diagnostics, without admission."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    out=ROOT/'build/gx8002-backup-imcra-state';out.mkdir(exist_ok=True);pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');sources=[]
    for name,obj in [('runtime_gx8002_backup_imcra_state_initialize.c','state.o'),('runtime_gx8002_backup_imcra_state_messages.c','messages.o')]:
        source=ROOT/'components/shared/gx8002'/name;sources.append({'path':str(source.relative_to(ROOT)),'sha256':sha(source.read_bytes())})
        subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-fno-caller-saves','-c',str(source),'-o',str(out/obj)],check=True)
    messages=[('imcra_error_header',0x100142c4),('imcra_error_required',0x10014310),('imcra_error_space',0x10014348),('imcra_memory_temp',0x10014378),('imcra_memory_static',0x1001439c),('imcra_memory_total',0x100143c0)]
    ld='SECTIONS { .imcra_state 0x1000e384 : { *(.text*) }\n'+''.join(f'.{n} {a:#x} : {{ *(.rodata.{n}) }}\n' for n,a in messages)+'}\n'
    bindings={'open_cfw_gx8002_backup_imcra_workspace':0x1000e314,'open_cfw_gx8002_powf':0x100100a4,'csky_cos_f32':0x1000ee64,'memset':0x100113c4,'printf':0x10009934,'__extendsfdf2':0x10011af4}
    ld+=''.join(f'{n} = {a:#x};\n' for n,a in bindings.items());(out/'state.ld').write_text(ld)
    path=out/'state.elf';subprocess.run([pre+'ld','-T',str(out/'state.ld'),str(out/'state.o'),str(out/'messages.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'state');assert not any(elf.relocations(s['index']) for s in elf.sections);assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    body=next(s for s in elf.sections if s['name']=='.imcra_state');diagnostics=[]
    for name,address in messages:
        sec=next(s for s in elf.sections if s['name']=='.'+name);content=elf.contents(sec);offset=address-0x10000000+0x38940;assert content==stock[offset:offset+len(content)]
        diagnostics.append({'name':name,'address':hex(address),'bytes':len(content),'exact_stock':True})
    (out/'state.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result={'compiler_additional_flags':['-fno-caller-saves'],'sources':sources,'bytes':body['size'],'envelope_bytes':1024,'fits':body['size']<=1024,'diagnostics':diagnostics,'source_admitted':False,'limits':['Full C candidate only. Current size, field access ordering, floating behavior and error-path equivalence require verification; not startup integrated. Numeric helper bindings are candidate linkage, not source ownership proof.']}
    (ROOT/'docs/research/gx8002-backup-imcra-state.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(build())
