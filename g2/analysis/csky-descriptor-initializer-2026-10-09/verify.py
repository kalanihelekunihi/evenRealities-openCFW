from pathlib import Path
import hashlib,json,re,subprocess,struct
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent;C=R/'g2/build/pseudocode-first/20260930T190500Z'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
image=C/'reviews/codec-canonical-images-003/images/binh_a_stage2_xip.bin';payload=R/'g2/blobs/official/g2-2.2.6.10/firmware_codec.bin';tool=C/'tools/csky-binutils-001/install/bin/csky-elfabiv2-objdump'
assert sha(image)=='49c9aed0126493220a3e48827c267d5e94f64d51d9ede0ccc3e84b8946744584'
assert sha(payload)=='b06dfef7faa2f1e52d2aacd07958d4b96ffc36dca5077ac9149e48f19fc9c4d0'
assert sha(tool)=='7150f7ffc2ac163f3d2d465620e5dac96df4b29411e5d0944419c41657cc2382'
start,end,base=0x102058d4,0x10205950,0x10203004
owners=[]
for p in sorted((C/'tasks').glob('*.json')):
 d=json.loads(p.read_text());scope=d.get('scope','');scope=scope if isinstance(scope,str) else json.dumps(scope)
 spans=[(int(a,16),int(b,16)) for a,b in re.findall(r'\[\s*(0x[0-9a-fA-F]+)\s*,\s*(0x[0-9a-fA-F]+)\s*\)',scope)]
 hit=any(a<end and start<b for a,b in spans);owners.append({'path':str(p.relative_to(R)),'sha256':sha(p),'overlap':hit})
assert not any(x['overlap'] for x in owners)
b=image.read_bytes();assert payload.read_bytes().find(b)==0xc590
body=b[start-base:end-base];assert payload.read_bytes()[0xee60:0xeedc]==body
argv=[str(tool),'-D','--disassemble-zeroes','-b','binary','-m','csky','-EL',f'--adjust-vma={base:#x}',f'--start-address={start:#x}','--stop-address=0x10205946',str(image)]
p=subprocess.run(argv,capture_output=True,text=True,check=True);(O/'instructions.txt').write_text(p.stdout)
rows=[]
for line in p.stdout.splitlines():
 m=re.match(r'^([0-9a-f]+):\s+([0-9a-f]+)\s+(.*)',line)
 if m:rows.append({'address':int(m[1],16),'bytes':len(m[2])//2,'instruction':m[3]})
assert sum(x['bytes'] for x in rows)==114
assert rows[-1]['address']==0x10205944 and rows[-1]['instruction'].startswith('jmp')
assert b[0x10205946-base:0x10205948-base]==b'\x00\x00'
assert struct.unpack('<II',b[0x10205948-base:0x10205950-base])==(0x20027350,0x4100ff)
caller=C/'analysis/csky-recovery-5316/001/full-xip.objdump.txt'
calls=[x for x in caller.read_text().splitlines() if re.search(r'\bbsr\s+0x102058d4\b',x)]
record={'schema_version':1,'campaign_id':'20260930T190500Z','target_sha256':'f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa','component':'codec','image_id':'binh_a_stage2_xip','isa_mode':'C-SKY_ABIv2','status':'partial_unreviewed_not_admitted','accepted':False,'range':[start,end],'body_sha256':hashlib.sha256(body).hexdigest(),'code_range':[start,0x10205946],'code_bytes':114,'bkpt_range':[0x10205946,0x10205948],'bkpt_bytes':2,'literal_range':[0x10205948,end],'literal_bytes':8,'child_range':[start-base,end-base],'payload_range':[0xee60,0xeedc],'conditional_runtime_base':base,'direct_inputs':[{'path':str(x.relative_to(R)),'sha256':sha(x)} for x in (image,payload,tool,caller)],'decoder_argv':argv,'decoder_exit_code':p.returncode,'instructions':rows,'direct_callers':calls,'ownership_contracts_scanned':len(owners),'original_instruction_execution':False,'semantic_model_execution':False,'unresolved':['MULA.32.L and BNEZAD manual-backed exact semantics','register ABI/caller contracts','live mapping and structure meaning','independent review and adoption']}
(O/'ownership.json').write_text(json.dumps(owners,indent=2)+'\n');(O/'results.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:record[k] for k in ('body_sha256','code_bytes','bkpt_bytes','literal_bytes','direct_callers')},indent=2))
