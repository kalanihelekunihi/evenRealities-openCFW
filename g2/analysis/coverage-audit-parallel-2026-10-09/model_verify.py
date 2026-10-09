from pathlib import Path
import json,re,hashlib,collections
R=Path.cwd();O=R/'g2/analysis/coverage-audit-parallel-2026-10-09';D=R/'g2/analysis/source-discovery-parallel-2026-10-09';r=json.loads((D/'model-provider-discrimination-final.json').read_text());eq=json.loads((D/'model-provider-equivalence-classes.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest();rows=[];groups=collections.defaultdict(list)
for c in r['candidates']:
 source=(R/c['root']/c['path']).read_bytes();headers=[]
 for h in c['model_headers']:
  b=(R/h['path']).read_bytes();text=b.decode();sets={}
  for branch,s in h['sets'].items():
   prefix=''if branch=='default'else branch;actual={}
   for kind in ['cmd','weight','ops','data','tmp']:
    m=re.search(r'unsigned\s+char\s+(\*\s*)?'+prefix+'kws_'+kind+r'_content\s*(?:\[\s*(\d+)\s*\])?',text)
    assert m,(h['path'],kind);actual[kind]=4 if m[1] else int(m[2])
   sets[branch]={'parsed_sizes':actual,'sizes_verified':actual==s['sizes'],'cmd_weight_exclusion_verified':(actual['cmd'],actual['weight'])!=(9164,120800) and s['cmd_weight_exclude']};groups[str(actual)].append({'provider':str(Path(c['root'])/c['path']),'header':h['path'],'branch':branch})
  headers.append({'path':h['path'],'hash_verified':sha(b)==h['sha256'],'sets':sets})
 rows.append({'provider':str(Path(c['root'])/c['path']),'source_hash_verified':sha(source)==c['sha256'],'headers':headers,'all_checked_branches_excluded':all(s['cmd_weight_exclusion_verified'] for h in headers for s in h['sets'].values())})
meta=json.loads((R/'g2/analysis/rescan-2026-10-07/implemented/gx8002/model-metadata.json').read_text());b=(R/'g2/blobs/official/g2-2.2.6.10/firmware_codec.bin').read_bytes();seg=b[meta['codec']['fwpk_segment_offset']:];getters={'cmd':(0x8bf4,'00eacc233c780000'),'weight':(0x8bfc,'00eae0d7b0383c78'),'ops':(0x8c04,'00303c78'),'data':(0x8c08,'cc3006403c78'),'tmp':(0x8c10,'04303c78')};stock={}
for name in ['commands','weights']:
 m=meta['image_a_model'][name];a,e=m['segment_extent'];stock[name]=sha(seg[a:e])==m['sha256']==r['stock_hash_checks'][name]['sha256']
out={'candidate_count':len(rows),'checked_header_variant_count':sum(len(h['sets'])for x in rows for h in x['headers']),'equivalence_class_count':len(groups),'equivalence_class_receipts_verified':dict(groups)==eq,'target_tuple_matches_historical':r['target_tuple']==meta['interface']['getter_return_sizes_bytes'],'codec_hash_verified':sha(b)==meta['codec']['sha256'],'getter_raw_bodies_verified':all(seg[a:a+len(bytes.fromhex(v))].hex()==v for a,v in getters.values()),'in_place_model_span_hashes':stock,'candidates':rows,'no_target_compatible_header_class':all(not any(s['parsed_sizes']==r['target_tuple'] for s in h['sets'].values()) for x in rows for h in x['headers'])};(O/'MODEL-PROVIDER-VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n');print({k:v for k,v in out.items()if k!='candidates'})
