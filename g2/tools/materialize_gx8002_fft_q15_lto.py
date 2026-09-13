# SPDX-License-Identifier: MIT
"""Retain compiler-generated LTO assembly/objects for source-based placement."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,FLAGS,Elf32,sha

def materialize(align_two=False):
    base=ROOT/('build/gx8002-fft-q15-align2-probe' if align_two else 'build/gx8002-fft-q15-cluster-lto-probe')
    report_path=ROOT/('docs/research/gx8002-fft-q15-align2-probe.json' if align_two else 'docs/research/gx8002-fft-q15-cluster-lto-probe.json')
    report=json.loads(report_path.read_text());variant=next(v for v in report['variants'] if v['lto'])
    for row in variant['sources']:assert sha((ROOT/row['source']).read_bytes())==row['sha256']
    out=ROOT/('build/gx8002-fft-q15-align2-materialized' if align_two else 'build/gx8002-fft-q15-lto-materialized');out.mkdir(exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    # LTO inputs are compiler objects from named source jobs, never firmware bytes.
    objects=[base/(name+'-1.o') for name in ('shift','maxabs','copy','fill')]
    fft=json.loads((ROOT/'docs/research/gx8002-source-rfft-generated-reverse-cluster.json').read_text())
    objects += [base/('fft-'+r['name']+'-1.o') for r in fft['sources']]
    path=out/'cluster.elf'
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-flto',*(['-falign-functions=2'] if align_two else []),'-save-temps','-nostdlib','-Wl,--gc-sections','-Wl,-T,'+str(base/'cluster.ld'),*['-Wl,-u,'+n for n in variant['public_entries']],*[str(p) for p in objects],'-o',str(path)],cwd=out,check=True)
    assert sha((base/'cluster-1.elf').read_bytes())==variant['elf_sha256']
    elf=Elf32(path.read_bytes(),'materialized');original=Elf32((base/'cluster-1.elf').read_bytes(),'original')
    for section in original.sections:
        if section['flags']&2 and section['size']:
            match=next(s for s in elf.sections if s['name']==section['name'])
            assert section['address']==match['address'] and original.contents(section)==elf.contents(match)
    generated=list(out.glob('*.ltrans*.o'));assert generated
    sections=[]
    for obj in generated:
        e=Elf32(obj.read_bytes(),str(obj))
        for s in e.sections:
            if s['flags']&2 and s['size']:sections.append({'object':obj.name,'section':s['name'],'size':s['size'],'align':s['align'],'flags':s['flags']})
    result={'align_two':align_two,'probe_report_sha256':sha(report_path.read_bytes()),'allocated_bytes_match_validated_lto':True,'elf_sha256':sha(path.read_bytes()),'generated_objects':[{'name':p.name,'sha256':sha(p.read_bytes())} for p in generated],'sections':sections,'source_admitted':False,'limits':['Compiler-generated intermediate materialization, not firmware extraction. Physical relink and external entry preservation remain pending.']}
    (ROOT/('docs/research/gx8002-fft-q15-align2-materialized.json' if align_two else 'docs/research/gx8002-fft-q15-lto-materialized.json')).write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=materialize();print([(s['section'],s['size'],s['align']) for s in r['sections']])
