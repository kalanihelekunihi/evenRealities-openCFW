from pathlib import Path
import json,hashlib,struct,re
R=Path.cwd();O=R/'g2/analysis/coverage-audit-parallel-2026-10-09';P=R/'g2/analysis/csky-board-layout-binding-2026-10-09';sha=lambda b:hashlib.sha256(b).hexdigest();v=json.loads((P/'results.json').read_text());assert all(sha((R/p).read_bytes())==h for p,h in v['inputs'].items());C=R/'g2/build/pseudocode-first/20260930T190500Z';x=(C/'reviews/codec-canonical-images-003/images/binh_a_stage2_xip.bin').read_bytes();s=(C/'reviews/codec-canonical-images-003/images/binh_a_stage2_sram.bin').read_bytes();payload=(R/'g2/blobs/official/g2-2.2.6.10/firmware_codec.bin').read_bytes();b=s[0x100269a4-0x10023400:0x100269a4-0x10023400+240];assert b==payload[0x189b8:0x18aa8]==(P/'board-data.bin').read_bytes();assert sha(b)==v['data']['sha256'];w=lambda o:struct.unpack_from('<I',b,o)[0];assert [w(o) for o in [0,4,32,60,88,168,188]]==[2,0x498,0xc98,0x498,6,1,1];assert [w(o) for o in range(192,220,4)]==[2,0,0,1,0,1,2];assert w(32)&63==24 and (w(32)>>6)&15==2 and (w(32)>>11)&1==1
im=next(json.loads(l) for l in (C/'inventory/images.jsonl').read_text().splitlines() if json.loads(l)['id']=='binh_a_stage2_sram');route=im['mapping_model']['routes'][0];assert route['write']['span'][0]==0x10023400 and route['write']['size']==14716
counts=[]
for label in ['board','output']:
 count=0
 for line in (P/(label+'-instructions.txt')).read_text().splitlines():
  m=re.match(r'^\s*([0-9a-f]+):\t([^\t]+)\t',line)
  if not m:continue
  tokens=m[2].split()
  if not all(re.fullmatch(r'[0-9a-f]{4}(?:[0-9a-f]{4})?',t) for t in tokens):continue
  raw=b''.join(int(t[j:j+4],16).to_bytes(2,'little') for t in tokens for j in range(0,len(t),4));a=int(m[1],16)-0x10203004;assert raw==x[a:a+len(raw)];count+=1
 counts.append({'listing':label,'byte_matched_lines':count})
for z in v['decoder_commands']:
 a,end=[int(k,16) for k in z['range']];assert sha(x[a-0x10203004:end-0x10203004])==z['bytes_sha256']
text=(P/'output-instructions.txt').read_text();assert all(i['instruction'] in text for i in v['original_consumer_evidence']);assert '1020720e:\t320c' in text and '10207212:\te3f0f293' in text and '1020722a:\t3000' in text and '0x10204340' in text;assert x[:4]==bytes.fromhex('01103c78') and struct.unpack_from('<I',x,4)[0]==0x200269a4
res={'status':'PASS','input_hashes_verified':len(v['inputs']),'data_bytes':240,'data_offset_verified':'0x189B8','normal_storage':'0x100269A4','getter_pointer':'0x200269A4','listing_bytes_verified':counts,'output_mask':6,'i2s_seven_words':[2,0,0,1,0,1,2],'register_argument_offsets':[192,196,200,204],'stack_argument_offsets':[208,212,216],'i2s_initially_enabled':False,'alias_visibility_proven':False,'source_rebuild':False,'qualification':'Pinned GRUS v2 little-endian32-bit public layout consistent with checked consumers; no unique producer/configuration/physical mapping proof'};(O/'BOARD-VERIFICATION.json').write_text(json.dumps(res,indent=2)+'\n');print('PASS board data, source hashes, original listing bytes and seven-word argument offsets')
