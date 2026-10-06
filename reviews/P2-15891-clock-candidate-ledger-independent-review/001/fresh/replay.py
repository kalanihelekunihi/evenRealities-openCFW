from pathlib import Path
import json,hashlib,re,subprocess
b=Path('g2/build/pseudocode-first/20260930T190500Z');h=lambda x:hashlib.sha256(x).hexdigest();src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';audit=b/'analysis/apollo-main-library-clock-primitives-cluster-audit-16264/001/sources.json';sources=json.loads(audit.read_text());reviewpaths=[Path(x) for x in subprocess.check_output(['rg','--files',str(b/'reviews'),'-g','review.json'],text=True).splitlines()];reviewtexts=[(p,p.read_bytes()) for p in reviewpaths];functions=[]
for source in sources:
 p=Path(source['path'])
 for name,pin in source['files'].items():assert h((p/name).read_bytes())==pin,(p,name)
 blocks=json.loads((p/'instructions.json').read_text());assert len(blocks)==1;block=blocks[0];start=block['start'];end=block['end'];refs=[]
 for rp,raw in reviewtexts:
  if p.parent.name.encode() in raw and (b'PASS' in raw):refs.append(dict(path=str(rp.relative_to(b)),sha256=h(raw),qualification='Candidate-linked scoped review; admission and exact per-input binding still require reconciliation'))
 calls=[]
 for row in block['instructions']:
  if row['mnemonic'] in ['bl','blx']:
   m=re.match(r'([0-9a-f]{6,8})\b',row['operands']);calls.append(dict(call_site=row['address'],target=int(m[1],16) if m else None,resolution='within clock primitive cluster' if m and 0x4d38ea<=int(m[1],16)<0x4d39f2 else 'external shipped dependency; contract reconciliation pending'))
 functions.append(dict(schema_version=1,campaign_id='20260930T190500Z',accepted=False,status='draft_partial',stable_id=f'apollo_main:flash:loaded:{start:08x}:Thumb',component='apollo_main',image_id='apollo_main:flash',address_space='loaded',isa_mode='Thumb',entry=start,body_ranges=[[start,end]],image_spans=[[start-0x438000,end-0x438000]],source_bytes_sha256=h(d[start-0x438000:end-0x438000]),image_sha256=h(d),pseudocode=dict(path=str((p/'pseudocode.md').relative_to(b)),sha256=h((p/'pseudocode.md').read_bytes())),instructions=dict(path=str((p/'instructions.json').relative_to(b)),sha256=h((p/'instructions.json').read_bytes())),calling_contract='See hash-bound pseudocode; no C prototype assigned',callees=calls,candidate_review_references=refs,unresolved=['Canonical review binding and image-wide ownership reconciliation','Reachability/indirect-edge and global denominator closure','Applicable FP/FPSCR/fault/MMIO/alias/concurrency contracts remain partial']))
literal_consumers={}
for source in sources:
 p=Path(source['path'])
 refs=json.loads((p/'references.json').read_text())
 for ref in refs:
  addr=ref.get('address')
  if addr is not None:literal_consumers.setdefault(addr,[]).append(str(p.relative_to(b)))
data=[]
for addr,consumers in sorted(literal_consumers.items()):
 raw=d[addr-0x438000:addr-0x438000+4];assert len(raw)==4
 data.append(dict(schema_version=1,campaign_id='20260930T190500Z',accepted=False,status='draft_partial',stable_id=f'apollo_main:flash:loaded:{addr:08x}:literal',image_id='apollo_main:flash',ranges=[[addr,addr+4]],image_spans=[[addr-0x438000,addr-0x438000+4]],source_bytes_sha256=h(raw),value_u32=int.from_bytes(raw,'little'),raw_hex=raw.hex(),candidate_consumers=consumers,unresolved=['Literal ownership may be shared with surrounding functions','Whole image data/code denominator and canonical review admission']))
o=Path('reviews/P2-15891-clock-candidate-ledger-independent-review/001/fresh');o.mkdir(parents=True,exist_ok=False);(o/'functions.jsonl').write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in functions));(o/'data.jsonl').write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in data));(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'summary.json').write_text(json.dumps(dict(accepted=False,status='draft_partial',function_records=len(functions),code_bytes=264,data_records=len(data),data_bytes=4*len(data),limitations=['Local candidate ledger only; not canonical coverage or function completeness','Review references are leads not admission decisions','No implementation modules interfaces graph or C started','No G2 freeze or gate change']),indent=2)+'\n');print('PASS',len(functions),'function drafts',len(data),'data drafts',sum(len(x['candidate_review_references']) for x in functions),'review references')
