# SPDX-License-Identifier: MIT
"""Check current compiled replacements for dependencies on their retained tails."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,Elf32,sha
from verify_gx8002_memcpy_source import decode
ARTIFACTS={'dma_configure':('backup-dma-configure','configure.elf'),'dma_descriptors':('backup-dma-descriptors','descriptors.elf'),'clock_lookup':('backup-clock-lookup','tables.elf'),'clock_frequency':('backup-clock-frequency','frequency.elf'),'platform_read':('backup-platform-read','platform-read.elf'),'platform_gate':('backup-platform-gate','gate.elf')}
DELTA=0x10003000-0x3b940

def verify():
    census_path=ROOT/'docs/research/gx8002-backup-replacement-tails.json';census=json.loads(census_path.read_text());build_path=ROOT/'build/gx8002-source-candidate/build-report.json'
    assert sha(build_path.read_bytes())==census['source_build_report_sha256']
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');results=[]
    for row in census['tails']:
        kind,artifact=ARTIFACTS[row['function']];path=ROOT/'build/gx8002-source-candidate'/kind/artifact;elf=Elf32(path.read_bytes(),kind)
        begin,end=[v+DELTA for v in row['tail']];start=row['stock_envelope'][0]+DELTA
        section=next(s for s in elf.sections if s['address']==start and s['flags']&4)
        assert sha(elf.contents(section))==row['compiled_sha256'] and section['address']+section['size']==begin
        decoded=decode(subprocess.check_output([pre,'-d',str(path)],text=True));direct=[];literal_values=[];stored=[]
        for pc,(op,args,width) in decoded.items():
            if op in ('br','bsr','bt','bf','bez','bnez','bnezad','bhz','blz','bhsz','blsz'):
                try:target=int(args.split(',')[-1].strip(),0)
                except ValueError:continue
                if begin<=target<end:direct.append({'pc':pc,'target':target})
            elif op=='lrw':
                try:value=int(args.split(',')[-1].strip(),0)
                except ValueError:continue
                if begin<=value<end:literal_values.append({'pc':pc,'value':value})
        for s in elf.sections:
            if not s['flags']&2 or s['type']==8:continue
            body=elf.contents(s)
            for i in range(len(body)-3):
                value=int.from_bytes(body[i:i+4],'little')
                if begin<=value<end:stored.append({'address':s['address']+i,'value':value})
        assert not direct and not literal_values and not stored,(kind,direct,literal_values,stored)
        results.append({'function':row['function'],'artifact_sha256':sha(path.read_bytes()),'tail_runtime':[begin,end],'bytes':end-begin,'direct_references':direct,'literal_value_references':literal_values,'allocated_word_matches':stored})
    report={'tail_census_sha256':sha(census_path.read_bytes()),'results':results,'reclaim_admitted':False,'limits':['Compiled replacement bodies authenticated against completed ownership report. Direct transfers, loaded literal values and all byte-aligned allocated-section words checked.','No computed-address or alternate-alias proof, and no loader reuse experiment. This supplements external stock-reference census without admitting reuse.']}
    (ROOT/'docs/research/gx8002-backup-tail-source-references.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(len(verify()['results']))
