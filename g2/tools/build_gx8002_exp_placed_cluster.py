# SPDX-License-Identifier: MIT
"""Place whole source exponential functions within reconstructed arithmetic space."""
import json,re,subprocess
from build_gx8002_exp_corrected_cluster import build as analysis
from build_gx8002_backup_cfft import ROOT,sha,Elf32

def build():
    prior=analysis(helpers=True)
    base=ROOT/'build/gx8002-double-muldiv-corrected'
    out=ROOT/'build/gx8002-exp-placed-cluster';out.mkdir(exist_ok=True)
    script=(base/'muldiv.ld').read_text()
    oldcopy=ROOT/'build/gx8002-double-addsub-placed/copy.o'
    source=ROOT/'components/shared/gx8002/runtime_gx8002_arithmetic_memcpy.c';copy=out/'copy.o'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    cmd=[pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-Dopen_cfw_gx8002_arithmetic_memcpy=memcpy','-c',str(source),'-o',str(copy)]
    subprocess.run(cmd,check=True)
    script=script.replace(str(oldcopy),str(copy)).replace('SIZEOF(.copy) <= 156','SIZEOF(.copy) == 20')
    inputs=list(dict.fromkeys(re.findall(r'(/[^\s()]+\.o)\(',script)))
    obj=ROOT/'build/gx8002-exp-helper-probe/tiny_scale.o'
    assert sha(obj.read_bytes())==prior['variant']['object_sha256'];inputs.append(str(obj))
    for name,section,offset,size in [('exp','open_cfw_gx8002_backup_exp',0x4818c,700),('scale','exp_scale',0x4a668,60),('tiny','exp_tiny',0x4a6a4,60)]:
        address=offset-0x3b940+0x10003000
        script+=f'SECTIONS {{ .{name} {address:#x} : {{ {obj}(.text.{section}) }} }}\nASSERT(SIZEOF(.{name}) == {size}, "{name} size drift")\n'
    ld=out/'exp.ld';ld.write_text(script);path=out/'exp.elf'
    subprocess.run([pre+'ld','-T',str(ld),*inputs,'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'placed');assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    sections=sorted([{'name':s['name'],'offset':s['address']-0x10003000+0x3b940,'bytes':s['size'],'sha256':sha(elf.contents(s))} for s in elf.sections if s['flags']&2 and s['size']],key=lambda s:s['offset'])
    assert all(a['offset']+a['bytes']<=b['offset'] for a,b in zip(sections,sections[1:]))
    assert all(0x3b940<=s['offset'] and s['offset']+s['bytes']<=0x4f9cc for s in sections)
    (out/'exp.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result={'prior':prior,'copy_source_sha256':sha(source.read_bytes()),'copy_compile_command':cmd,'sections':sections,'elf_sha256':sha(path.read_bytes()),'source_admitted':False,'limits':['Complete C functions in bounded physical regions. Compact copy and placed exponential execution, references and integration remain pending.']}
    (ROOT/'docs/research/gx8002-exp-placed-cluster.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(build()['elf_sha256'])
