# SPDX-License-Identifier: MIT
"""Guarded compiler assembly pool placement for the active SNPU callback."""
import json,subprocess
from build_gx8002_active_snpu_candidate import build as standalone,ROOT,IMAGE,IMAGE_SHA,sha,Elf32

def build():
    evidence=standalone();out=ROOT/'build/gx8002-board';sdk=ROOT/'build/upstream-nationalchip-lvp-kws';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_active_snpu_callback.c';assembly=out/'active-snpu-pool.s'
    subprocess.run([pre+'gcc',*evidence['flags'],'-mconstpool','-I'+str(out/'active-snpu-config'),'-I'+str(sdk/'include'),'-I'+str(sdk/'lvp/common'),'-S',str(source),'-o',str(assembly)],check=True)
    original=assembly.read_text();load='\tlrw\ta0, [.LCP0]';pool='\t.align\t2\n.LCP0:\n\t.long\topen_cfw_gx8002_active_snpu_queue\n';size='\t.size\topen_cfw_gx8002_active_snpu_callback, .-open_cfw_gx8002_active_snpu_callback'
    assert original.count(load)==original.count(pool)==original.count(size)==1
    transformed=original.replace(load,'\tlrw16\ta0, [.LCP0]').replace(pool,'\t.section .rodata.active_pool,"a",@progbits\n'+pool).replace(size,'')
    asm=out/'active-snpu-split.s';asm.write_text(transformed);obj=out/'active-snpu-split.o';path=out/'active-snpu-split.elf'
    subprocess.run([pre+'as','-mcpu=ck804ef',str(asm),'-o',str(obj)],check=True)
    state_source=ROOT/'components/shared/gx8002/runtime_gx8002_active_snpu_state.c';state_obj=out/'active-snpu-state.o'
    subprocess.run([pre+'gcc',*evidence['flags'],'-I'+str(sdk/'lvp/common'),'-c',str(state_source),'-o',str(state_obj)],check=True)
    script=out/'active-snpu-split.ld';script.write_text('SECTIONS { .text 0x10026340 : { *(.text*) } .pool 0x100264d4 : { *(.rodata.active_pool) } .queue 0x2002e6ec (NOLOAD) : { *(.bss.active_snpu_queue) } .buffer 0x2002e700 (NOLOAD) : { *(.bss.active_snpu_buffer) } }\n'+''.join(f'{n} = {a:#x};\n' for n,a in evidence['bindings'].items() if n!='open_cfw_gx8002_active_snpu_queue'))
    subprocess.run([pre+'ld','-T',str(script),str(obj),str(state_obj),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'active split');sections=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(sections)==4
    for name,address,size in ((".queue",0x2002e6ec,20),(".buffer",0x2002e700,56)):
        allocation=next(s for s in sections if s["name"]==name)
        assert (allocation["address"],allocation["size"],allocation["type"],allocation["flags"])==(address,size,8,3)
    text=next(s for s in sections if s['name']=='.text');data=next(s for s in sections if s['name']=='.pool');body=elf.contents(text);literal=elf.contents(data)
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert text['address']==0x10026340 and len(body)==22 and body==stock[0x18354:0x1836a]
    assert data['address']==0x100264d4 and data['flags']==2 and literal==(0x2002e6ec).to_bytes(4,'little')
    assert literal==stock[0x184e8:0x184ec]
    assert not any(elf.relocations(s['index']) for s in sections) and not any(s['name'] and s['section']==0 for s in elf.symbols())
    report={'state_source_sha256':sha(state_source.read_bytes()),'standalone':evidence,'compiler_assembly_sha256':sha(original.encode()),'transformed_assembly_sha256':sha(transformed.encode()),'elf_sha256':sha(path.read_bytes()),'body_bytes':22,'body_sha256':sha(body),'literal_bytes':4,'literal_sha256':sha(literal),'source_admitted':False,'limits':['Guarded compiler-assembly transform forces short literal load and separates source pointer pool. Exact stock instruction bytes and source-derived pointer verified; no stock extraction used in construction. Shared-pool ownership and full admission pending.']}
    (ROOT/'docs/research/gx8002-active-snpu-split-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(build()['body_bytes'])
