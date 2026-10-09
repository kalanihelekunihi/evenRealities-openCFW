from pathlib import Path
import json,hashlib,re
R=Path.cwd();O=R/'g2/analysis/coverage-audit-parallel-2026-10-09';D=R/'g2/analysis/source-discovery-parallel-2026-10-09';sha=lambda b:hashlib.sha256(b).hexdigest();d=json.loads((D/'codec-em9305-range-unions-corrected.json').read_text());ims={x['id']:x for x in [json.loads(l) for l in (R/'g2/build/pseudocode-first/20260930T190500Z/inventory/images.jsonl').read_text().splitlines()]};manifest={l.split(None,1)[1].lstrip('*'):l.split(None,1)[0] for l in (R/'g2/research/MANIFEST.sha256').read_text().splitlines() if l.strip()}
def union(rs):
 out=[]
 for a,b in sorted(rs):
  if out and a<=out[-1][1]:out[-1][1]=max(b,out[-1][1])
  else:out.append([a,b])
 return out
mapping={'uart_stage1':'uart_boot_stage1','uart_stage2':'uart_boot_stage2','binh_a_stage2_xip':'image_a_xip','binh_a_stage2_sram':'image_a_sram','binh_b_stage2':'image_b_sram'};cc=[]
for x in d['codec']:
 im=ims[x['image']];b=Path(im['content_path']).read_bytes();assert sha(b)==im['content_sha256'];q=R/'g2/research/corpus/codec/ghidra/open-2026-09-29'/mapping[x['image']];meta=json.loads((q/'RUN.json').read_text());assert meta['image_sha256']==sha(b);rs=[];count=0
 for f in q.glob('functions*.jsonl'):
  assert sha(f.read_bytes())==manifest[str(f.relative_to(R/'g2/research'))]
  for l in f.read_text().splitlines():
   r=json.loads(l);count+=1;a=int(r['body_start'],16)-x['base'];z=int(r['body_end_inclusive'],16)-x['base']+1;assert 0<=a<z<=len(b);assert sha(b[a:z])==r['body_sha256'];assert r['decompiled'];file=q/'decomp'/(r['entry']+'.c');s=file.read_text();assert s.strip() and '{' in s and '}' in s;assert sha(file.read_bytes())==manifest[str(file.relative_to(R/'g2/research'))];rs += [[int(a,16)-x['base'],int(z,16)-x['base']+1] for a,z in r['ranges']]
 u=union(rs);assert u==x['raw_pseudocode_ranges_image_offsets'];assert count==x['records'];n=sum(z-a for a,z in u);assert n==x['raw_pseudocode_union_bytes'];cc.append({'image':x['image'],'envelopes':count,'raw_union_bytes':n,'all_hashes_and_ranges_verified':True})
ll=[]
for x in d['listings']:
 p=R/x['path'];assert sha(p.read_bytes())==x['sha256'];b=(R/'g2/blobs/official/g2-2.2.6.10/firmware_ble_em9305.bin').read_bytes() if 'em9305' in x['path'] else Path(ims['binh_a_stage2_xip']['content_path']).read_bytes();assert sha(b)==x['raw_sha256'];rs=[];n=0
 for l in p.read_text().splitlines():
  m=re.match(r'^\s*([0-9a-fA-F]+):\t([^\t]+)\t',l)
  if not m or not re.fullmatch(r'\s*[0-9a-fA-F]{4}(?:[0-9a-fA-F]{4})?(?:\s+[0-9a-fA-F]{4}(?:[0-9a-fA-F]{4})?)*\s*',m[2]):continue
  a=int(m[1],16)-x['base'];tokens=m[2].split();raw=b''.join(int(token[j:j+4],16).to_bytes(2,'little') for token in tokens for j in range(0,len(token),4));assert 0<=a<a+len(raw)<=len(b);assert raw==b[a:a+len(raw)],(p,l,raw.hex(),b[a:a+len(raw)].hex());rs.append([a,a+len(raw)]);n+=1
 u=union(rs);assert u==x['matched_listing_ranges_image_offsets'];assert n==x['parsed_lines'];represented=sum(z-a for a,z in u);assert represented==x['matched_listing_union_bytes'];ll.append({'path':x['path'],'lines':n,'matched_unique_bytes':represented,'raw_payload_or_image_bytes':len(b),'hash_and_serialization_verified':True})
failed=json.loads((D/'codec-em9305-range-unions.json').read_text());assert failed['listings'][1]['mismatch_count']==3775;assert sum(x['raw_union_bytes'] for x in cc)==92560;assert sum(x['envelopes'] for x in cc)==929;assert 210072+816==210888 and 210888+1060==211948
out={'status':'PASS','codec':cc,'listings':ll,'preserved_CSKY_failed_mismatches':3775,'codec_raw_pseudocode_payload_fraction':92560/326092*100,'EM_listing_payload_fraction':210072/211948*100,'codec_XIP_listing_payload_fraction':36484/326092*100,'EM_unrepresented_record3_bytes':816,'EM_metadata_other_record_bytes':1060,'qualification':'Raw artifact representation fractions only, not executable or semantic coverage; aliases counted once within image, separate terminal codec image identities.'};(O/'CODEC-LISTING-VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
