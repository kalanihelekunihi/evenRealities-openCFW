from pathlib import Path
import hashlib,json,struct,re
R=Path.cwd(); O=R/'g2/analysis/coverage-audit-parallel-2026-10-09'; D=R/'g2/analysis/source-discovery-parallel-2026-10-09'; P=R/'g2/analysis/case-flash-unlock-label-correction-2026-10-09'
h=lambda b:hashlib.sha256(b).hexdigest()
c=[]
def check(n,v): c.append({'check':n,'pass':bool(v)}); assert v,n
q=json.loads((P/'results.json').read_text())
for p,s in q['inputs'].items(): check('case input '+p,h((R/p).read_bytes())==s)
b=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
for t in q['routines']:
 a,z=int(t['start'],16),int(t['end'],16); check(t['corrected_name']+' extent',h(b[a-0x8000000:z-0x8000000])==t['bytes_sha256'])
 listing=(P/(t['corrected_name']+'-instructions.txt')).read_text()
 rows=re.findall(r'^([0-9a-f]+): ([0-9a-f]{4}) ',listing,re.M)
 check(t['corrected_name']+' complete instruction bytes',len(rows)==14 and all(b[int(a,16)-0x8000000:int(a,16)-0x8000000+2]==bytes.fromhex(x) for a,x in rows))
 for l in t['literals']:
  a=int(l['instruction'],16); v=struct.unpack_from('<H',b,a-0x8000000)[0]; target=((a+4)&~3)+(v&255)*4
  check('Thumb literal '+l['instruction'],v&0xf800==0x4800 and target==int(l['literal_address'],16) and struct.unpack_from('<I',b,target-0x8000000)[0]==int(l['value'],16))
a=json.loads((D/'callback-root-static-data.json').read_text()); C=R/'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images'; s=(C/'binh_a_stage2_sram.bin').read_bytes(); x=(C/'binh_a_stage2_xip.bin').read_bytes()
check('SRAM image',h(s)==a['sram_image_sha256']); check('XIP image',h(x)=='49c9aed0126493220a3e48827c267d5e94f64d51d9ede0ccc3e84b8946744584')
u=int(a['stored_slot'],16)-0x10023400
check('slot hash and pointer',h(s[u:u+4])==a['slot_sha256'] and struct.unpack_from('<I',s,u)[0]==int(a['slot_value'],16))
check('descriptor hash and all eight words',h(s[u+4:u+36])==a['descriptor_sha256'] and list(struct.unpack_from('<8I',s,u+4))==[int(v,16) for v in a['descriptor'].values()])
for k,v in [('app_name','sample app'),('suspend_priv','SampleAppSuspend'),('resume_priv','SampleAppResume')]:
 i=int(a['descriptor'][k],16)-0x10203004;check(k+' authenticated string',x[i:x.index(b'\0',i)].decode()==v)
locations=[0x10203004+i for i in range(len(x)-3) if x[i:i+4]==struct.pack('<I',0x20026d38)]
check('exact XIP root literals',locations==[0x10208c94,0x10208cbc,0x10208d30,0x10208d94])
for p,v in json.loads((D/'callback-visibility-contract-hashes.json').read_text()).items(): check('visibility input '+p,h((R/p).read_bytes())==v)
check('combined-copy contains root descriptor',len(s)==14716 and 0x10023400+len(s)==0x10026d7c and u+36<len(s))
check('package offsets',32+0x153f4+u==0x18d4c)
(O/'CASE-CALLBACK-VERIFICATION.json').write_text(json.dumps({'status':'PASS','checks':c,'execution':False,'source_rebuild':False,'runtime_alias_proven':False},indent=2)+'\n')
print(len(c),'checks PASS')
