from pathlib import Path
import json, hashlib, collections
OUT=Path(__file__).resolve().parent
rows=json.loads((OUT/'classified-matches.json').read_text())
summary=json.loads((OUT/'summary.json').read_text())
arc=json.loads((OUT/'arc2-summary.json').read_text())
arcrows=[r for r in rows if r['machine']==195]
arc['scope']='historical ARCv2-only supplement; counts and matches exclude other architectures'
arc['matches']=len(arcrows)
arc['match_classes']=dict(collections.Counter(r['class'] for r in arcrows))
arc['combined_matches_after_supplement']=len(rows)
arc['combined_match_classes_after_supplement']=dict(collections.Counter(r['class'] for r in rows))
(OUT/'arc2-summary.json').write_text(json.dumps(arc,indent=2)+'\n')
summary['scope']='current default unified replay across ARM, older ARC, ARCv2 and C-SKY'
assert summary['matches']==len(rows)
assert summary['match_classes']==dict(collections.Counter(r['class'] for r in rows))
summary['historical_arc2_supplement']=arc
summary['final_match_classes']=dict(collections.Counter(r['class'] for r in rows))
summary['native_unique_exact_functions']=json.loads((OUT/'validation.json').read_text())['validated_unique_functions']
shortlist=[r for r in rows if r['class']=='exact_bytes' and r['catalogue_overlaps'] and not any(x['scoped_pass'] for x in r['catalogue_overlaps'])]
(OUT/'previously-unreviewed-shortlist.json').write_text(json.dumps(shortlist,indent=2)+'\n')
summary['historical_catalogue_without_scoped_pass_exact_occurrences']=len(shortlist)
(OUT/'final-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
manifest=[]
for p in sorted(OUT.rglob('*')):
 if p.is_file() and p.name!='SHA256MANIFEST.json':
  b=p.read_bytes();manifest.append({'path':str(p.relative_to(OUT)),'size':len(b),'sha256':hashlib.sha256(b).hexdigest()})
(OUT/'SHA256MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(summary,indent=2))
