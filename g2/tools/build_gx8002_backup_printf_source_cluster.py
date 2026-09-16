# SPDX-License-Identifier: MIT
"""Compose main formatter with source integer and floating-point dependencies."""
import json,re,subprocess
from build_gx8002_fixunsdfsi_cluster import build as math_build
from build_gx8002_double_inequality_cluster import build as inequality_build
from build_gx8002_backup_unsigned_division import build as division_build
from build_gx8002_backup_printf_main import build as main_build,ROOT,Elf32,sha
from build_gx8002_backup_printf_integer import build as integer_build
from build_gx8002_backup_printf_reverse import build as reverse_build


def build():
    evidence={'math':math_build(),'inequality':inequality_build(),'division':division_build(),
              'main':main_build(),'integer':integer_build(),'reverse':reverse_build()}
    out=ROOT/'build/gx8002-backup-printf-source-cluster';out.mkdir(exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    script=(ROOT/'build/gx8002-fixunsdfsi-cluster/fix.ld').read_text()
    script+=(ROOT/'build/gx8002-backup-unsigned-division/division.ld').read_text()
    ne=ROOT/'build/gx8002-double-inequality-cluster/ne.o'
    script+=f'SECTIONS {{ .inequality 0x10012168 : {{ {ne}(.text) }} }}\nASSERT(SIZEOF(.inequality) <= 56, "inequality overflow")\n'
    inputs=list(dict.fromkeys(re.findall(r'(/[^\s()]+\.o)\(',script)))
    base=ROOT/'build/gx8002-backup-printf'
    selectors=[]
    for name,globalize,weaken,sections in [
        ('main',[],['_out_rev','_ntoa_long','_ntoa_long_long'],
         [('null',0x10008a00,4,'.text._out_null'),('formatter',0x10008e20,2820,'.text._vsnprintf .rodata._vsnprintf* .rodata.pow10*')]),
        ('integer',['_ntoa_format','_ntoa_long','_ntoa_long_long'],['_out_rev'],
         [('integer_format',0x10008aa0,488,'.text._ntoa_format'),('long',0x10008c88,192,'.text._ntoa_long'),('wide',0x10008d48,216,'.text._ntoa_long_long')]),
        ('reverse',['_out_rev'],[],[('reverse',0x10008a04,156,'.text._out_rev')])]:
        obj=out/(name+'.o')
        subprocess.run([pre+'objcopy',*['--localize-symbol='+s for s in ('printf_','sprintf_','snprintf_','vprintf_','vsnprintf_','fctprintf')],*['--globalize-symbol='+s for s in globalize],
                        *['--weaken-symbol='+s for s in weaken],str(base/(name+'.o')),str(obj)],check=True)
        inputs.append(str(obj));selectors.append(str(obj))
        for sec,addr,limit,pattern in sections:
            selection=' '.join(f'{obj}({part})' for part in pattern.split())
            script+=f'SECTIONS {{ .printf_{sec} {addr:#x} : {{ {selection} }} }}\nASSERT(SIZEOF(.printf_{sec}) <= {limit}, "{sec} overflow")\n'
    script+='__ledf2 = open_cfw_gx8002_double_compare_4ab98;\n'
    script+='SECTIONS { /DISCARD/ : { '+ ' '.join(p+'(.text* .rodata*)' for p in selectors)+' } }\n'
    ld=out/'cluster.ld';ld.write_text(script);path=out/'cluster.elf'
    subprocess.run([pre+'ld','-T',str(ld),*inputs,'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'formatter source cluster')
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    required=['_vsnprintf','_out_rev','_ntoa_format','_ntoa_long','_ntoa_long_long',
              *evidence['main']['external_package_bindings'],'__udivdi3','__umoddi3']
    symbols={s['name']:s for s in elf.symbols() if s['name']}
    assert all(symbols[n]['section'] not in (0,0xfff1) for n in required)
    assert symbols['_vsnprintf']['value']==0x10008e20
    for name,offset in evidence['main']['external_package_bindings'].items():
        assert symbols[name]['value']==offset-0x38940+0x10000000,name
    allocated=sorted([s for s in elf.sections if s['flags']&2 and s['size']],key=lambda s:s['address'])
    assert all(a['address']+a['size']<=b['address'] for a,b in zip(allocated,allocated[1:]))
    assert all(0x10003000<=s['address'] and s['address']+s['size']<=0x1001708c for s in allocated)
    for standalone, pairs in [('main.elf',[('.printf_null','.printf_null'),('.printf_main','.printf_formatter')]),
                              ('integer.elf',[('.text._ntoa_format','.printf_integer_format'),('.text._ntoa_long','.printf_long')]),
                              ('reverse.elf',[('.printf_reverse','.printf_reverse')])]:
        prior=Elf32((base/standalone).read_bytes(),standalone)
        for old_name,new_name in pairs:
            a=next(s for s in prior.sections if s['name']==old_name)
            b=next(s for s in elf.sections if s['name']==new_name)
            assert a['address']==b['address'] and prior.contents(a)==elf.contents(b),(standalone,old_name)
    (out/'cluster.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result={'builds':evidence,'elf_sha256':sha(path.read_bytes()),'required_source_symbols':sorted(set(required)),
            'sections':[{'name':s['name'],'address':s['address'],'bytes':s['size']} for s in allocated],
            'source_admitted':False,'limits':['Source-only formatter dependency composition at bounded addresses. Caller-supplied output callback remains an interface.',
                                           'Main execution, startup integration and full firmware admission/hardware qualification remain pending.']}
    (ROOT/'docs/research/gx8002-backup-printf-source-cluster.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':print(build()['required_source_symbols'])
