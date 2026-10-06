from pathlib import Path
import hashlib,json
ROOT=Path('/Users/kalani/Repo/evenRealities-openCFW'); base=ROOT/'g2/build/pseudocode-first/20260930T190500Z'; P=base/'analysis/csky-candidate-ledger-15904/002';d=json.loads((P/'ledger.json').read_text());h=lambda b:hashlib.sha256(b).hexdigest();fail=[];pins=0;filechecks=0;manifestbad=[]
for pin in d['pins']:
 p=ROOT/pin['path']
 if not p.is_file() or h(p.read_bytes())!=pin['sha256']:fail.append('pin:'+pin['path'])
 else:pins+=1
for r in d['candidate_records']:
 rp=ROOT/r['attempt_receipt']['path']
 if not rp.is_file() or h(rp.read_bytes())!=r['attempt_receipt']['sha256']:fail.append('receipt:'+r['candidate_record_id'])
 else:filechecks+=1
 for key in ('instruction_record','pseudocode'):
  obj=r[key];p=ROOT/obj['path']
  if not p.is_file() or h(p.read_bytes())!=obj['sha256']:fail.append(key+':'+r['candidate_record_id'])
  else:filechecks+=1
 mr=Path(r['attempt_receipt']['receipt_manifest_path'])
 if not mr.is_absolute(): mr=(ROOT/mr if str(mr).startswith('g2/') else rp.parent/mr)
 actual=h(mr.read_bytes()) if mr.is_file() else None
 # Compare ledger's captured resolved manifest digest; 4056/002 also carries its receipt's own claim and explicit false flag.
 if actual!=r['attempt_receipt']['manifest_sha256']:
  manifestbad.append({'record':r['candidate_record_id'],'reason':'resolved manifest differs from indexed digest','actual':actual})
 rr=json.loads(rp.read_text())
 claim=rr.get('artifact_manifest_sha256')
 if claim is not None and (claim!=actual or r['attempt_receipt'].get('receipt_manifest_binding_matches') is False):
  manifestbad.append({'record':r['candidate_record_id'],'reason':'attempt receipt points at a different attempt manifest','path':str(mr.relative_to(ROOT)) if mr.is_relative_to(ROOT) else str(mr),'receipt_sha256':claim,'resolved_sha256':actual,'receipt_binding_flag':r['attempt_receipt'].get('receipt_manifest_binding_matches')})
# route premises and arithmetic summaries
routes=[]
for m in d['conditional_image_models']:
 model=m['mapping_model']
 for route in model['routes']:
  routes.append({'image_id':m['image_id'],'route_id':route['route_id'],'source_image':model['source']['content_sha256'],'source_size':model['source']['size'],'transfer_kind':route['transfer_kind'],'selection_ast':route['selection']['ast'],'external_premises':[x['id']+':'+x['status'] for x in model['external_premises']],'target':route['expected_execution']})
result={'pins_passed':pins,'pins_total':len(d['pins']),'candidate_records':len(d['candidate_records']),'receipt_and_code_pseudocode_hash_checks':filechecks,'failures':fail,'manifest_findings':manifestbad,'verification_counts':json.loads((P/'verification.json').read_text())['counts'],'routes':routes,'accepted':False}
out=Path('/tmp/csky-ledger-review-results.json');out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
