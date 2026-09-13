# SPDX-License-Identifier: MIT
"""Relink source-generated LTO assembly to the candidate clock-tail plan."""
import json,re,subprocess,struct
from verify_gx8002_memcpy_source import decode
from build_gx8002_backup_cfft import ROOT,FLAGS,Elf32,sha
from analyze_gx8002_fft_cluster_references import DATA,DELTA

def build():
    plan_path=ROOT/'docs/research/gx8002-fft-q15-clock-tail-plan.json';plan=json.loads(plan_path.read_text())
    material_path=ROOT/'docs/research/gx8002-fft-q15-lto-materialized.json';assert sha(material_path.read_bytes())==plan['materialized_report_sha256']
    material=json.loads(material_path.read_text());base=ROOT/'build/gx8002-fft-q15-lto-materialized'
    for r in material['generated_objects']:assert sha((base/r['name']).read_bytes())==r['sha256']
    assembly=list(base.glob('*.ltrans*.s'));assert len(assembly)==1
    original=assembly[0].read_text();text=original
    # Split compiler-generated typed data into individual sections. No data
    # directives or instruction bodies are changed, only section selection.
    for name in ('source_rfft_forward','source_cfft_256','source_rfft_inverse'):
        pattern=r'(\t.global\t'+name+r'\n)(?:\t.section\t.descriptor[^\n]*\n)?'
        text,n=re.subn(pattern,lambda m:m.group(1)+f'\t.section .descriptor.{name},"a"\n',text);assert n==1
    out=ROOT/'build/gx8002-fft-q15-tail-layout';out.mkdir(exist_ok=True)
    (out/'component.s').write_text(text)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc',*FLAGS,'-c',str(out/'component.s'),'-o',str(out/'component.o')],check=True)
    (out/'entry.S').write_text('.section .copy_entry,"ax"\n.global source_copy_entry\nsource_copy_entry:\n br32 open_cfw_gx8002_backup_copy_q15\n')
    subprocess.run([pre+'gcc',*FLAGS,'-c',str(out/'entry.S'),'-o',str(out/'entry.o')],check=True)
    solution=plan['solution'];assert solution
    rows=[{'section':r['section'],'offset':r['offset'],'size':r['size']} for r in solution['reserved'] if not r['branch']]
    rows += [r for group in solution['placements'] for r in group]
    rows.append({'section':'.copy_entry','offset':0x47ac0,'size':4})
    script='SECTIONS {\n';expected={}
    for index,row in enumerate(sorted(rows,key=lambda r:r['offset'])):
        name=f'.code{index}';address=row['offset']+DELTA
        script+=f'{name} {address:#x} : {{ KEEP(*({row["section"]})) }}\nASSERT(SIZEOF({name}) == {row["size"]}, "code size changed")\n'
        expected[name]={'address':address,'offset':row['offset'],'size':row['size']}
    for key,section in [('complex_descriptor','.descriptor.source_cfft_256'),('inverse_descriptor','.descriptor.source_rfft_inverse'),('forward_descriptor','.descriptor.source_rfft_forward'),('complex_coefficients','.complex_coefficients'),('real_coefficients','.q14_pairs')]:
        offset,size,address=DATA[key];name='.'+key
        script+=f'{name} {address:#x} : {{ KEEP(*({section})) }}\nASSERT(SIZEOF({name}) == {size}, "data size changed")\n'
        expected[name]={'address':address,'offset':offset,'size':size}
    script+='/DISCARD/ : { *(.bit_reverse) *(.bit_lengths) }\n}\n'
    for name in ('radix4','radix4_inverse','radix4_by2','radix4_by2_inverse','bit_reverse','cfft','split_forward','split_inverse'):
        script+=f'backup_{name} = open_cfw_gx8002_backup_{name};\n'
    (out/'component.ld').write_text(script);path=out/'component.elf'
    subprocess.run([pre+'ld','-T',str(out/'component.ld'),str(out/'component.o'),str(out/'entry.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'placed source');allocated=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert {s['name'] for s in allocated}==set(expected)
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    for s in allocated:
        row=expected[s['name']];assert (s['address'],s['size'])==(row['address'],row['size']);row['sha256']=sha(elf.contents(s))
    symbols={s['name']:s['value'] for s in elf.symbols() if s['name']}
    for name,offset in [('rfft',0x478a4),('shift_q15',0x47a00),('maxabs_q15',0x47a74),('fill_q15',0x47aec)]:assert symbols['open_cfw_gx8002_backup_'+name]==offset+DELTA
    assert symbols['source_copy_entry']==0x47ac0+DELTA
    (out/'component.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    def data(name):return elf.contents(next(s for s in allocated if s['name']=='.'+name))
    assert data('complex_descriptor')==struct.pack('<H2xIIH2x',256,symbols['open_cfw_gx8002_backup_complex_coefficients'],0,240)
    for name,flag in [('forward_descriptor',0),('inverse_descriptor',1)]:
        assert data(name)==struct.pack('<IBB2xIII',512,flag,1,1,symbols['open_cfw_gx8002_backup_q14_pairs'],symbols['source_cfft_256'])
    code=decode((out/'component.disassembly.txt').read_text());calls=[]
    for pc,(op,args,width) in code.items():
        if op=='bsr':
            target=int(args,0);assert target in code;calls.append({'pc':pc,'target':target})
    entry=code[symbols['source_copy_entry']]
    assert entry[0]=='br' and int(entry[1],0)==symbols['open_cfw_gx8002_backup_copy_q15'] and entry[2]==4
    report={'descriptors_verified':3,'copy_entry_branch_verified':True,'direct_calls':calls,'plan_sha256':sha(plan_path.read_bytes()),'compiler_assembly_sha256':sha(original.encode()),'sectioned_assembly_sha256':sha(text.encode()),'elf_sha256':sha(path.read_bytes()),'sections':expected,'symbols':symbols,'source_admitted':False,'hardware_qualified':False,'limits':['Experimental clock-tail reuse. Source-generated assembly relink, not firmware cutting. Descriptor fields and internal call targets checked; execution and loader checks pending.']}
    (ROOT/'docs/research/gx8002-fft-q15-tail-layout.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(build()['elf_sha256'])
