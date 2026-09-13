# SPDX-License-Identifier: MIT
"""Compare ordinary and LTO links retaining all four public Q15 helpers."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,FLAGS,Elf32,sha

def probe(include_fft=False,align_two=False):
    out=ROOT/('build/gx8002-fft-q15-align2-probe' if align_two else 'build/gx8002-fft-q15-cluster-lto-probe' if include_fft else 'build/gx8002-q15-cluster-lto-probe');out.mkdir(exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    if align_two:assert include_fft
    names=('shift','maxabs','copy','fill');symbols=['open_cfw_gx8002_backup_'+name+'_q15' for name in names]
    script=out/'cluster.ld';script.write_text('SECTIONS { .text 0x10010000 : { *(.text*) } }\n')
    fft=None
    if include_fft:
        from build_gx8002_source_rfft_cluster import build
        fft=build(True,True,generated_reverse=True)
        symbols.append('open_cfw_gx8002_backup_rfft')
        aliases=('radix4','radix4_inverse','radix4_by2','radix4_by2_inverse','bit_reverse','cfft','split_forward','split_inverse')
        script.write_text('SECTIONS { .text 0x10010000 : { *(.text*) } .rodata ALIGN(4) : { KEEP(*(.descriptor)) *(.complex_coefficients) *(.q14_pairs) *(.rodata*) } /DISCARD/ : { *(.bit_lengths) *(.bit_reverse) } }\n'+''.join(f'backup_{n} = open_cfw_gx8002_backup_{n};\n' for n in aliases))
    rows=[]
    for lto in (False,True):
        objects=[];sources=[];extra=(['-flto'] if lto else [])+(['-falign-functions=2'] if align_two else [])
        for name in names:
            source=ROOT/f'components/shared/gx8002/runtime_gx8002_backup_{name}_q15.c'
            obj=out/f'{name}-{int(lto)}.o';objects.append(str(obj))
            optimization='-fno-tree-scev-cprop' if name=='fill' else '-fno-tree-loop-optimize'
            subprocess.run([pre+'gcc','-Os',*FLAGS[1:],optimization,*extra,'-c',str(source),'-o',str(obj)],check=True)
            sources.append({'source':str(source.relative_to(ROOT)),'sha256':sha(source.read_bytes()),'extra_flags':[optimization,*extra]})
        if fft:
            for row in fft['sources']:
                source=ROOT/row['source'];assert sha(source.read_bytes())==row['sha256']
                obj=out/f'fft-{row["name"]}-{int(lto)}.o';objects.append(str(obj))
                subprocess.run([pre+'gcc','-Os',*FLAGS[1:],*row['extra_flags'],*extra,'-I',str(ROOT/'build/gx8002-source-rfft-generated-reverse-cluster'),'-c',str(source),'-o',str(obj)],check=True)
                sources.append(row)
        path=out/f'cluster-{int(lto)}.elf'
        command=[pre+'gcc','-Os',*FLAGS[1:],*extra,'-nostdlib','-Wl,--gc-sections','-Wl,-T,'+str(script)]
        command += ['-Wl,-u,'+symbol for symbol in symbols]
        result=subprocess.run([*command,*objects,'-o',str(path)],capture_output=True,text=True);assert result.returncode==0,result.stderr
        elf=Elf32(path.read_bytes(),'Q15 cluster');allocated=[s for s in elf.sections if s['flags']&2 and s['size']]
        assert {s['name'] for s in allocated}==({'.text','.rodata'} if include_fft else {'.text'})
        text=next(s for s in allocated if s['name']=='.text')
        assert not any(s['name'] and s['section']==0 for s in elf.symbols())
        assert not any(elf.relocations(s['index']) for s in elf.sections)
        defined={s['name']:s for s in elf.symbols() if s['name']}
        assert all(symbol in defined and defined[symbol]['section']==text['index'] for symbol in symbols)
        (out/f'cluster-{int(lto)}.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
        rows.append({'lto':lto,'sources':sources,'code_bytes':text['size'],'total_bytes':sum(s['size'] for s in allocated),'public_entries':{n:defined[n]['value'] for n in symbols},'elf_sha256':sha(path.read_bytes()),'diagnostics':result.stderr})
    report={'align_two':align_two,'variants':rows,'original_helper_bytes':4606 if include_fft else 276,'source_admitted':False,'hardware_qualified':False,'limits':['All public entries forced live and unresolved symbols rejected. Analysis-address size experiment only; linked behavior and physical entry preservation not qualified.']}
    (ROOT/('docs/research/gx8002-fft-q15-align2-probe.json' if align_two else 'docs/research/gx8002-fft-q15-cluster-lto-probe.json' if include_fft else 'docs/research/gx8002-q15-cluster-lto-probe.json')).write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print([(r['lto'],r['code_bytes']) for r in probe()['variants']])
