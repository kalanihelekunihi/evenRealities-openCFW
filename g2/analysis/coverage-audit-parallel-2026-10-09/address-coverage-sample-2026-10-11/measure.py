from pathlib import Path
import json,hashlib,collections
R=Path.cwd();O=Path(__file__).parent;sha=lambda b:hashlib.sha256(b).hexdigest()
def union(rs):
 out=[]
 for a,b in sorted(rs):
  if out and a<=out[-1][1]:out[-1][1]=max(out[-1][1],b)
  else:out.append([a,b])
 return out
def size(rs):return sum(b-a for a,b in union(rs))
inputs={}
def read(p):
 b=(R/p).read_bytes();inputs[p]=sha(b);return b
main=read('g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin');assert sha(main)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
rows=json.loads(read('g2/analysis/tlsf-main-source-comparison-20261010-implementation/byte-comparison.json'));tlsf=[]
for x in rows:
 s=x['stock'];a=int(s['entry'],16);n=s['bytes'];assert sha(main[a-0x437fe0:a-0x437fe0+n])==s['sha256'];tlsf.append({'name':x['name'],'range':[hex(a),hex(a+n)],'bytes':n,'stock_sha256':s['sha256'],'source_kind':'matched upstream C comparator','compile_verified':True,'behavior_verified':'selected allocator sequences only, per independent prior review','byte_identical':False,'integrated_reference_replacement':False})
ble=read('g2/blobs/official/g2-2.2.6.10/firmware_ble_em9305.bin');assert sha(ble)=='91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9'
em=json.loads(read('g2/analysis/c-source-completion-20261011/em9305/body-coverage-boundary.json'));groups=collections.defaultdict(list)
for x in em['native_envelopes_with_C_candidates']:
 a=int(x['start'],16);b=int(x['end_exclusive'],16);assert b-a==x['bytes'] and 0x302400<=a<b<=0x335bc8;groups[x['source_file']].append([a,b])
emunion=union([r for rs in groups.values() for r in rs]);EM={'envelopes':len(em['native_envelopes_with_C_candidates']),'declared_sum':sum(x['bytes'] for x in em['native_envelopes_with_C_candidates']),'deduplicated_envelope_bytes':size(emunion),'ranges':emunion,'subcomponents':{k:{'envelopes':len(v),'unique_bytes':size(v),'ranges':v} for k,v in groups.items()},'stage':'declared static recreated-C correspondence only; per-body compiled/behavior/identity stages not inferred','denominator':'receipt record payload211824; whole official payload211948; neither is classified executable code'}
case=read('g2/blobs/official/g2-2.2.6.10/firmware_box.bin');assert sha(case)=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';cg=collections.defaultdict(list);count=0;unmapped=[]
for l in read('g2/tools/manifests/g2-box-function-map.tsv').decode().splitlines():
 if not l or l.startswith('#') or l.startswith('entry'):continue
 t=l.split('\t');a=int(t[0],16);n=int(t[1]);count+=1
 if not 0x08000000<=a<a+n<=0x08000000+len(case)-32:unmapped.append(t);continue
 cg[t[3]].append([a,a+n])
CU=union([r for rs in cg.values() for r in rs]);C={'table_rows':count,'unmapped_rows':unmapped,'unique_envelope_bytes':size(CU),'groups':{k:{'rows':len(v),'unique_envelope_bytes':size(v),'ranges':union(v)} for k,v in cg.items()},'stage':'function ownership attribution, not mapped compiling C','payload_bytes':len(case),'classified_code_data_padding':'unknown; table function envelopes do not supply exhaustive classification'}
res={'artifact':'official s200_v2.2.6.10','inputs_sha256':inputs,'main_TLSF':{'functions':tlsf,'unique_stock_envelope_bytes':size([[int(x['range'][0],16),int(x['range'][1],16)] for x in tlsf]),'known_source_subsample_only':True},'EM_source_envelopes':EM,'CASE_attribution_table':C,'integrated_replacement_bytes_reference':0,'full_payloads_reference_blob_bytes':4300283,'unknown_remainder_is_not_proven_binary_only':True}
(O/'results.json').write_text(json.dumps(res,indent=2)+'\n');print('TLSF',res['main_TLSF']['unique_stock_envelope_bytes'],'EM',EM['envelopes'],EM['deduplicated_envelope_bytes'],'CASE',count,C['unique_envelope_bytes'])
