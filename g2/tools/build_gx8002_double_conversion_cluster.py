# SPDX-License-Identifier: MIT
"""Link upstream greater/less comparison wrappers to the complete source core."""
import json,subprocess
from build_gx8002_exp_source_closure import build as closure
from build_gx8002_double_core_layout import build as core
from build_gx8002_backup_cfft import ROOT,sha,Elf32

def build():
    evidence=closure();layout=core()
    base=ROOT/'build/gx8002-double-core-layout';out=ROOT/'build/gx8002-double-conversion-cluster';out.mkdir(exist_ok=True)
    lib=ROOT/'build/csky-macos/gcc-build/csky-unknown-elf/libgcc'
    script=(base/'core.ld').read_text();inputs=[base/(name+'.o') for name in ('pack','right','unpack','left','compare')]
    rows=[]
    for name,off,size,symbol in [('gt',0x4aae0,64,'__gtdf2'),('lt',0x4ab60,56,'__ltdf2'),('si',0x4abd0,104,'__floatsidf')]:
        original=lib/('_si_to_df.o' if name=='si' else '_'+name+'_df.o');expected=next(r for r in evidence['rebuilt_objects'] if r['name']==original.name)
        assert sha(original.read_bytes())==expected['sha256']
        obj=out/(name+'.o');obj.write_bytes(original.read_bytes());inputs.append(obj)
        address=off-0x3b940+0x10003000
        script+=f'SECTIONS {{ .{name} {address:#x} : {{ {obj}(.text) }} }}\nASSERT(SIZEOF(.{name}) <= {size}, "wrapper exceeds envelope")\n'
        rows.append({'name':name,'offset':off,'stock_bytes':size,'symbol':symbol,'object_sha256':sha(obj.read_bytes())})
    ld=out/'wrappers.ld';ld.write_text(script);path=out/'wrappers.elf';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'ld','-T',str(ld),*[str(p) for p in inputs],'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'wrappers');assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    for row in rows:
        sec=next(s for s in elf.sections if s['name']=='.'+row['name']);row['compiled_bytes']=sec['size'];row['sha256']=sha(elf.contents(sec))
        assert next(s['value'] for s in elf.symbols() if s['name']==row['symbol'])==row['offset']-0x3b940+0x10003000
    (out/'wrappers.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result={'gcc_revision':evidence['gcc_revision'],'core':layout,'wrappers':rows,'elf_sha256':sha(path.read_bytes()),'source_admitted':False,'limits':['Original public entries, linked only to source core. Decoded wrapper behavior and firmware composition remain pending; no stock helper binding.']}
    (ROOT/'docs/research/gx8002-double-conversion-cluster.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(build()['wrappers'])
