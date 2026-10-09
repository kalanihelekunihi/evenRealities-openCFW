from pathlib import Path
import json,hashlib
R=Path.cwd();O=R/'g2/analysis/coverage-audit-parallel-2026-10-09';sha=lambda b:hashlib.sha256(b).hexdigest();P=R/'g2/build/pseudocode-first/20260930T190500Z/inventory';m=json.loads((R/'g2/manifests/g2-2.2.6.10.json').read_text());images=[json.loads(l) for l in (P/'images.jsonl').read_text().splitlines()];out={'definitions':{'fully_C_buildable':'whole locked payload from integrated C/source, no retained executable blob; no such receipt exists','blob':'current default reference manifest retained payload bytes / full payload bytes including metadata and data','pseudocode':'raw historical export successful functions / recognized functions, not whole executable coverage or correctness','assembly':'whole unique executable-byte denominator unavailable; presence of dump not a percentage'},'components':[]}
for c in m['components']:
 p=R/'g2'/c['provider']['path'];assert len(p.read_bytes())==c['provider']['size'] and sha(p.read_bytes())==c['provider']['sha256'];out['components'].append({'name':c['name'],'payload_bytes':c['provider']['size'],'current_reference_blob_percent':100,'whole_payload_source_build_proven':False,'integrated_C_executable_percent':None,'whole_executable_pseudocode_percent':None,'whole_executable_disassembly_percent':None,'images':[{'id':x['id'],'size':x['size'],'parent':x['parent_image_id']} for x in images if x['payload_id']==c['name']]})
manifest={}
for l in (R/'g2/research/MANIFEST.sha256').read_text().splitlines():
 if l.strip():h,p=l.split(None,1);manifest[p.lstrip('*')]=h
out['raw_exports']=[]
base=R/'g2/research/corpus';dirs=[base/'apollo-main/ghidra/decomp',base/'touch/ghidra/open-2026-09-29',base/'case/ghidra/open-2026-09-29',base/'apollo-bootloader/ghidra/open-2026-09-29',*sorted((base/'codec/ghidra/open-2026-09-29').iterdir())]
for q in dirs:
 fs=list(q.glob('functions*.jsonl'))
 if not fs:continue
 rows=[]
 for f in fs:
  key=str(f.relative_to(R/'g2/research'));assert sha(f.read_bytes())==manifest[key];rows +=[json.loads(l) for l in f.read_text().splitlines()]
 n=sum(x.get('decompiled') is True for x in rows);out['raw_exports'].append({'path':str(q.relative_to(R)),'functions':len(rows),'raw_pseudocode_functions':n,'raw_function_percent':round(100*n/len(rows),3),'recognized_function_body_bytes_sum':sum(x['body_bytes'] for x in rows),'manifest_verified':True,'warning':'body sum may overlap/include data; not an executable denominator'})
out['inventory']={'images':len(images),'coverage_rows':70,'all_coverage_kinds':sorted(set(json.loads(l)['kind'] for l in (P/'coverage.jsonl').read_text().splitlines())),'decoded_summary_is_historical_not_current':True};out['payload_bytes_total']=sum(x['payload_bytes'] for x in out['components']);out['global_reference_blob_percent']=100;out['whole_payload_source_build_proven_count']=0
(O/'COMPONENT-METRICS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'payload_bytes':out['payload_bytes_total'],'raw_exports':out['raw_exports']},indent=2))
