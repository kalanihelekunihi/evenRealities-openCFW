from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
index_at_verify_start=sha((R/'.git/index').read_bytes())
ns={'__file__':str(R/'g2/analysis/audio-notification-block-insertion-2026-10-09/seal.py')}
exec(Path(ns['__file__']).read_text().split('baseline =',1)[0],ns)
count=0;bad=[]
for root in ['g2/analysis','g2/components']:
 for m in (R/root).rglob('DELIVERABLES.json'):
  if m.parent in ns['TARGETS'] or m.parent==D:continue
  data=json.loads(m.read_text());files=data.get('files',{}) if isinstance(data,dict) else {}
  if not isinstance(files,dict):continue
  for n,v in files.items():
   expected=v if isinstance(v,str) else v.get('sha256') if isinstance(v,dict) else None
   if not expected:continue
   p=R/n if n.startswith(('g2/','r1/','docs/','third-party/')) else m.parent/n;count+=1
   if not p.is_file() or sha(p.read_bytes())!=expected:bad.append(str(p))
audit=json.loads((R/'g2/analysis/audio-queue-cmsis-source-closure-2026-10-09/preservation-before.json').read_text())['audit']
ab=[n for n,v in audit.items() if sha((R/n).read_bytes())!=(v if isinstance(v,str) else v['sha256'])]
ck=json.loads((R/'g2/analysis/rescan-2026-10-09T032723Z/snapshot.json').read_text())['checkpoints'];ck={n:sha((R/v['path']).read_bytes())==v['sha256'] for n,v in ck.items()}
index=sha((R/'.git/index').read_bytes());earlier=json.loads((R/'g2/analysis/iom-queue-offset-stock-binding-20261009-implementation/stock-receipts.json').read_text())['index_before']
p={'prior_sealed_entries':count,'seal_mismatches':bad,'audit_inputs':len(audit),'audit_mismatches':ab,'checkpoints':ck,'index_sha256':index,'index_matches_prior_track_sample':index==earlier,'index_stable_during_verify':index==index_at_verify_start}
assert not bad and not ab and all(ck.values()) and index==index_at_verify_start
print(json.dumps(p,indent=2))
