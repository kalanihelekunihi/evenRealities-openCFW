# SPDX-License-Identifier: MIT
"""Place the source RFFT component inside original FFT ranges; not admission."""
import json,subprocess
from build_gx8002_source_rfft_cluster import build as component
from build_gx8002_backup_cfft import ROOT,FLAGS,Elf32,sha
from analyze_gx8002_fft_cluster_references import DELTA,DATA

def build(include_fill=False):
    evidence=component(True,True,generated_reverse=True)
    base=ROOT/'build/gx8002-source-rfft-generated-reverse-cluster'
    out=ROOT/('build/gx8002-placed-rfft-fill-cluster' if include_fill else 'build/gx8002-placed-rfft-cluster');out.mkdir(exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    # Keep all externally referenced descriptors and the RFFT entry fixed.
    source=(base/'descriptor.c').read_text()
    for name in ('source_cfft_256','source_rfft_forward','source_rfft_inverse'):
        marker='__attribute__((section(".descriptor"),used))'
        pos=source.index(name+'=');start=source.rfind(marker,0,pos);assert start>=0
        source=source[:start]+source[start:].replace(marker,marker.replace('.descriptor','.'+name),1)
    (out/'descriptor.c').write_text(source)
    descriptor=out/'descriptor.o'
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-I',str(base),'-c',str(out/'descriptor.c'),'-o',str(descriptor)],check=True)
    objects=[base/(s['name']+'.o') for s in evidence['sources'] if s['name']!='descriptor']+[descriptor]
    if include_fill:
        from build_gx8002_backup_fill_q15 import build as fill
        fill_evidence=fill()
        objects.append(ROOT/'build/gx8002-backup-fill-q15/fill.o')
    items=[]
    for obj in objects:
        elf=Elf32(obj.read_bytes(),str(obj))
        for section in elf.sections:
            if section['flags']&4 and section['size']:
                items.append({'object':str(obj),'section':section['name'],'size':section['size'],'align':section['align']})
    fill_item=None
    if include_fill:
        fill_item=next(i for i in items if i['section']=='.text.open_cfw_gx8002_backup_fill_q15');items.remove(fill_item)
        assert fill_item['size']==52
    ranges=[(0x478a4,0x47a00),(0x47b20 if include_fill else 0x47b14,0x4818a),(0x4cd34,0x4cf14)]
    entry=next(i for i in items if i['section']=='.text.open_cfw_gx8002_backup_rfft');items.remove(entry)
    bins=[[entry],[],[]];positions=[ranges[0][0]+entry['size'],ranges[1][0],ranges[2][0]]
    items.sort(key=lambda i:-i['size'])
    def place(index):
        if index==len(items):return True
        item=items[index]
        for b in range(3):
            old=positions[b];aligned=(old+item['align']-1)&-item['align']
            if aligned+item['size']<=ranges[b][1]:
                bins[b].append(item);positions[b]=aligned+item['size']
                if place(index+1):return True
                bins[b].pop();positions[b]=old
        return False
    assert place(0),'No function-section packing fits'
    script='ENTRY(open_cfw_gx8002_backup_rfft)\nSECTIONS {\n'
    expected={}
    if include_fill:
        expected['.fill_q15']=(0x47aec+DELTA,52)
        script+=f'.fill_q15 {0x47aec+DELTA:#x} : {{ KEEP(\"{fill_item["object"]}\"({fill_item["section"]})) }}\n'

    for n,((start,end),group) in enumerate(zip(ranges,bins)):
        name=f'.fft_code{n}';expected[name]=(start+DELTA,end-start)
        script+=f'{name} {start+DELTA:#x} : {{\n'+''.join(f'"{i["object"]}"({i["section"]})\n' for i in group)+'}\n'
        script+=f'ASSERT(SIZEOF({name}) <= {end-start}, "code range overflow")\n'
    for key,section in [('complex_descriptor','.source_cfft_256'),('complex_coefficients','.complex_coefficients'),('real_coefficients','.q14_pairs'),('inverse_descriptor','.source_rfft_inverse'),('forward_descriptor','.source_rfft_forward')]:
        off,size,address=DATA[key];name='.fft_'+key;expected[name]=(address,size)
        script+=f'{name} {address:#x} : {{ KEEP(*({section})) }}\nASSERT(SIZEOF({name}) == {size}, "data size")\n'
    script+='/DISCARD/ : { *(.bit_lengths) *(.bit_reverse) }\n}\n'
    aliases=('radix4','radix4_inverse','radix4_by2','radix4_by2_inverse','bit_reverse','cfft','split_forward','split_inverse')
    script+=''.join(f'backup_{name} = open_cfw_gx8002_backup_{name};\n' for name in aliases)
    (out/'cluster.ld').write_text(script);path=out/'cluster.elf'
    subprocess.run([pre+'ld','--gc-sections','-T',str(out/'cluster.ld'),*[str(o) for o in objects],'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'placed FFT');sections=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert {s['name'] for s in sections}==set(expected)
    assert not any(s['section']==0 and s['name'] for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    rows=[]
    for s in sections:
        address,capacity=expected[s['name']];assert s['address']==address and s['size']<=capacity
        offset=address-DELTA if address<0x20000000 else address-0x20003000+0x3b940
        rows.append({'section':s['name'],'address':address,'offset':offset,'size':s['size'],'capacity':capacity,'sha256':sha(elf.contents(s))})
    symbols={s['name']:s['value'] for s in elf.symbols() if s['name']}
    assert symbols['open_cfw_gx8002_backup_rfft']==0x478a4+DELTA
    (out/'cluster.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'include_fill':include_fill,'source_component':evidence,'entry':symbols['open_cfw_gx8002_backup_rfft'],'elf_sha256':sha(path.read_bytes()),'sections':rows,'packing':bins,'source_admitted':False,'hardware_qualified':False,'limits':['Placed ELF only: loader and external reference closure pending.','Old bit-reversal table range now holds code; fixed CFFT256 contract applies. No firmware ownership registration.']}
    if include_fill:
        standalone=Elf32((ROOT/'build/gx8002-backup-fill-q15/fill.elf').read_bytes(),'standalone fill')
        before=next(s for s in standalone.sections if s['name']=='.text')
        after=next(s for s in elf.sections if s['name']=='.fill_q15')
        assert before['address']==after['address'] and standalone.contents(before)==elf.contents(after)
        report['fill_build']=fill_evidence
        report['placed_fill_matches_standalone']=True
    (ROOT/('docs/research/gx8002-placed-rfft-fill-cluster.json' if include_fill else 'docs/research/gx8002-placed-rfft-cluster.json')).write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
    r=build();print([(s['section'],s['size'],s['capacity']) for s in r['sections']])
