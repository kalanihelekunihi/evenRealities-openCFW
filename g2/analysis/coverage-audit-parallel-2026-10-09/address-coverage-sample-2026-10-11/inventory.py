from pathlib import Path
import json,hashlib,csv
R=Path.cwd();O=Path(__file__).parent;H={};sha=lambda b:hashlib.sha256(b).hexdigest()
def get(p):
 b=(R/p).read_bytes();H[p]=sha(b);return json.loads(b)
def merge(rs):
 out=[]
 for a,b in sorted(rs):
  assert 0<=a<b
  if out and a<=out[-1][1]:out[-1][1]=max(b,out[-1][1])
  else:out.append([a,b])
 return out
def n(rs):return sum(b-a for a,b in merge(rs))
def gaps(rs,size):
 out=[];cur=0
 for a,b in merge(rs):
  assert b<=size
  if cur<a:out.append([cur,a])
  cur=b
 if cur<size:out.append([cur,size])
 return out
manifest=get('g2/manifests/g2-2.2.6.10.json');sizes={c['name']:c['provider']['size'] for c in manifest['components']};payloads={}
for c in manifest['components']:
 p='g2/'+c['provider']['path'];b=(R/p).read_bytes();H[p]=sha(b);assert H[p]==c['provider']['sha256'] and len(b)==sizes[c['name']];payloads[c['name']]=b
P=get('g2/analysis/source-discovery-parallel-2026-10-09/partial-artifact-range-unions.json');K=get('g2/analysis/source-discovery-parallel-2026-10-09/codec-em9305-range-unions-corrected.json');sample=get(str(O.relative_to(R) if O.is_absolute() else O)+'/results.json')
ip='g2/build/pseudocode-first/20260930T190500Z/inventory/images.jsonl';bb=(R/ip).read_bytes();H[ip]=sha(bb);IM={x['id']:x for x in map(json.loads,bb.decode().splitlines())}
rows=[];stages={c:{'function_mapping':[],'pseudocode':[],'disassembly':[],'C_mapped_lower_bound':[],'C_compile_lower_bound':[],'C_behavior_lower_bound':[],'C_identical_lower_bound':[],'integrated_replacement':[]} for c in sizes}
def add(c,module,rs,stage,origin,confidence,functions=None,missing=''):
 rs=merge(rs);assert all(b<=sizes[c] for a,b in rs)
 if stage in stages[c]:stages[c][stage]+=rs
 rows.append({'component':c,'module':module,'stage':stage,'source_origin':origin,'boundary_confidence':confidence,'function_count':functions,'unique_payload_bytes':n(rs),'payload_denominator':sizes[c],'payload_percent':100*n(rs)/sizes[c],'ranges_payload_half_open':rs,'missing_join_fields':missing})
for x in P['components']:
 run_bytes=(R/x['run_path']).read_bytes();H[x['run_path']]=sha(run_bytes);assert sha(run_bytes)==x['run_sha256']
 im=IM[x['image_id']];data=(R/im['content_path']).read_bytes();H[im['content_path']]=sha(data);assert sha(data)==im['content_sha256'];assert len(data)==x['image_bytes']
 for fp in (R/x['run_path']).parent.glob('functions*.jsonl'):
  meta_bytes=fp.read_bytes();H[str(fp.relative_to(R))]=sha(meta_bytes)
  for rec in map(json.loads,meta_bytes.decode().splitlines()):
   lo=int(rec['body_start'],16)-x['base'];hi=int(rec['body_end_inclusive'],16)-x['base']+1;assert 0<=lo<hi<=len(data) and sha(data[lo:hi])==rec['body_sha256']
 c=x['image_id'].split(':')[0];off=0 if c=='apollo_bootloader' else 32;base=x['base']
 for field,stage in [('body_ranges','function_mapping'),('raw_pseudocode_ranges','pseudocode')]:add(c,'recognized flash functions (no semantic module subdivision)',[[a-base+off,b-base+off] for a,b in x[field]],stage,'raw function metadata','authenticated prior interval receipt',x['records'] if stage=='function_mapping' else x['records']-x['decompiled_false_records'],'module ownership and exclusive instruction/data classification')
for x in K['codec']:
 im=IM[x['image']];ib=(R/im['content_path']).read_bytes();assert sha(ib)==im['content_sha256'];H[im['content_path']]=sha(ib)
 off=im.get('candidate_mapping',{}).get('package_component_offset',[None])[0]
 if off is None:
  parent=IM[im['parent_image_id']];off=parent['candidate_mapping']['package_component_offset'][0]+im['source_span'][0]
 assert payloads['codec'][off:off+len(ib)]==ib
 rs=[[a+off,b+off] for a,b in x['raw_pseudocode_ranges_image_offsets']]
 add('codec',x['image'],'rs' if False else rs,'function_mapping','raw function metadata','nested-program boundary; runtime mapping conditional',x['records'],'compiled source and behavior receipts per function')
 add('codec',x['image'],rs,'pseudocode','raw decompiler output','prior verified artifact union',x['records'])
A=get('g2/analysis/dependency-gap-audit-fresh-2026-10-09T192823Z/EXISTING-ARM-LISTING-VERIFICATION.json')
for x in A['components']:add(x['component'],'selected original listings',x['payload_ranges'],'disassembly','original assembly artifact','serialized-byte correspondence; not code-only')
for c,count in [('codec',36484),('ble_em9305',210072)]:
 if c=='codec':off=IM['binh_a_stage2_xip']['candidate_mapping']['package_component_offset'][0];rs=[[off,off+count]]
 else:
  # Reuse exact listing offset ranges rather than assuming continuous listing.
  x=next(x for x in K['listings'] if 'em9305' in str(x));rs=x.get('matched_ranges_image_offsets',x.get('byte_ranges_image_offsets'))
  if rs is None:rs=x.get('matched_listing_ranges_image_offsets')
  if rs is None:continue
  rs=[[a,b] for a,b in rs]
 add(c,'verified listing image',rs,'disassembly','original assembly artifact','prior exact serialization')
for f in sample['main_TLSF']['functions']:
 rs=[[int(a,16)-0x437fe0,int(b,16)-0x437fe0] for a,b in [f['range']]]
 for stage in ['C_mapped_lower_bound','C_compile_lower_bound','C_behavior_lower_bound']:add('apollo_main','TLSF/'+f['name'],rs,stage,'matched upstream C','selected authenticated function',1,'full dependency/runtime production placement; behavior is bounded fixture sequences')
T=get('g2/analysis/touch-compiler14-successor-2026-10-09/results.json')[0]
for f in T['functions']:
 a=int(f['stock_address'],16);tb=next(x['base'] for x in P['components'] if x['image_id']=='touch:flash');rs=[[a-tb+32,a-tb+32+f['stock_bytes']]];assert sha(payloads['touch'][rs[0][0]:rs[0][1]])==f['sha256'] and f['exact']
 for stage in ['C_mapped_lower_bound','C_compile_lower_bound','C_identical_lower_bound']:add('touch','PDL/MSCLP/'+f['function'],rs,stage,'matched upstream C','prior complete-section compile receipt; hash checked',1,'whole object source chain retained in predecessor; component layout not integrated')
for module,x in sample['EM_source_envelopes']['subcomponents'].items():add('ble_em9305',module,[[a-0x302400+1060,b-0x302400+1060] for a,b in x['ranges']],'C_mapped_lower_bound','recreated C declared correspondence','inferred source-file grouping',x['envelopes'],'per-range selected source hash, object hash, compile command, behavior and equality receipt')
for module,x in sample['CASE_attribution_table']['groups'].items():add('case',module,[[a-0x08000000+32,b-0x08000000+32] for a,b in x['ranges']],'attribution_only','table ownership label','inferred attribution category',x['rows'],'actual C body/source/object/verification join')
summary=[]
for c,ss in stages.items():
 if c=='ble_em9305':ss['function_mapping']=ss['C_mapped_lower_bound'][:]
 for k in ss:ss[k]=merge(ss[k])
 unmapped=gaps(ss['function_mapping'],sizes[c]);assert n(ss['function_mapping'])+n(unmapped)==sizes[c]
 summary.append({'component':c,'payload_bytes':sizes[c],'mapped_function_envelope_bytes':n(ss['function_mapping']),'unmapped_by_selected_function_inventory_bytes':n(unmapped),'unmapped_ranges':unmapped,'stage_unique_bytes':{k:n(v) for k,v in ss.items()},'stage_ranges':ss,'zero_C_stage_is_no_verified_lower_bound_not_no_C':True,'code_data_padding_partition':'unknown except container/image facts; envelope not exclusively code','original_binary_only_bytes':'unknown; reference packaging copies all payload bytes','integrated_replacement_bytes':0})
result={'target':'s200_v2.2.6.10','inputs_sha256':H,'components':summary,'module_rows':rows,'scope':'all available selected six-component mappings; not complete semantic module census','missing_fields':['exclusive code/data/padding classification','module ownership for raw functions','per-body source kind/path/hash and selected compile object/command/hash','per-body behavior receipt and tested provider boundary','complete body/relocation exact-byte receipt','absolute generated image composition and original byte replacement map'],'notes':['Orthogonal stage unions overlap; do not add percentages.','EM source envelope collection is partial; unmapped is not binary-only.','No compilation/firmware/denied-phase work.']}
(O/'inventory.json').write_text(json.dumps(result,indent=2)+'\n')
fields=['component','module','stage','source_origin','boundary_confidence','function_count','unique_payload_bytes','payload_denominator','payload_percent','missing_join_fields']
with (O/'inventory.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:r.get(k) for k in fields} for r in rows)
print([(x['component'],x['mapped_function_envelope_bytes'],x['unmapped_by_selected_function_inventory_bytes']) for x in summary])
