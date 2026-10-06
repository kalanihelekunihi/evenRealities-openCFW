from pathlib import Path
import json,hashlib,re
b=Path('g2/build/pseudocode-first/20260930T190500Z');a=b/'analysis';h=lambda x:hashlib.sha256(x).hexdigest()
audit=a/'failed-function-continuation-byte-audit-16350/001/results.json'; report=json.loads(audit.read_text());src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';image=src.read_bytes();assert h(image)==report['image_sha256']; pins={str(audit):h(audit.read_bytes()),str(src):h(image)}
rawpath=Path('g2/research/corpus/apollo-main/ghidra/open-2026-09-29/functions-000.jsonl'); raw=next(q for line in rawpath.open() if (q:=json.loads(line))['entry']=='00540036');pins[str(rawpath)]=h(rawpath.read_bytes());assert raw['ranges']==[['00540036','005409c3']] and raw['body_bytes']==2446 and raw['body_sha256']==h(image[0x540036-0x438000:0x5409c4-0x438000])
rows=[];docs=[]
for c in report['candidates']:
 p=Path(c['path'])
 for fn in ['instructions.json','pseudocode.md']:
  pins[str(p/fn)]=h((p/fn).read_bytes())
 rows+=json.loads((p/'instructions.json').read_text())[0]['instructions'];docs.append((p/'pseudocode.md').read_text())
addresses={r['address'] for r in rows}; assert len(addresses)==959
edges=[];calls=[];returns=[]
for r in rows:
 pc=r['address'];nxt=pc+len(bytes.fromhex(r['bytes']));m=r['mnemonic'].split('.')[0];op=r['operands']
 if m=='bl':
  dst=int(re.match(r'([0-9a-f]+)',op)[1],16);calls.append(dict(pc=pc,target=dst));edges.append(dict(pc=pc,target=nxt,kind='conditional-on-child-return'))
 elif m.startswith('b') and m not in ['bic','bics']:
  match=re.match(r'([0-9a-f]+)',op);assert match,(pc,m,op);dst=int(match[1],16);assert dst in addresses,(pc,dst);edges.append(dict(pc=pc,target=dst,kind='branch',condition=m))
  if m!='b':edges.append(dict(pc=pc,target=nxt,kind='fallthrough'))
 elif 'pc}' in op:
  returns.append(dict(pc=pc,kind='saved-return-context',instruction=r));assert nxt==0x5409c4
 else:
  assert nxt in addresses,(pc,nxt,m);edges.append(dict(pc=pc,target=nxt,kind='fallthrough'))
assert sorted(set(c['target'] for c in calls))==sorted(int(x,16) for x in raw['callees'])
result=dict(status='partial',accepted=False,entry=0x540036,end=0x5409c4,body_bytes=2446,instruction_rows=len(rows),direct_call_sites=len(calls),unique_direct_children=len(set(c['target'] for c in calls)),direct_calls=calls,edges=edges,return_sites=returns,raw_metadata=raw,limitations=['Static direct-edge consistency only; no proof of feasible paths, absence of alternate entries or all child effects.','Every child return-continuation is conditional on actual child completion; no universal child-return assumption.','Architecture fault/self-loop at5401B2 remains; cause of original Ghidra failure not established.','No semantics admission, full reviewed corpus, freeze, C or gate changes.'])
o=Path('reviews/P2-15953-failed-function-cfg-consolidated-draft-independent-review/001/fresh');o.mkdir(parents=True,exist_ok=False)
(o/'results.json').write_text(json.dumps(result,indent=2)+'\n');(o/'input-pins.json').write_text(json.dumps(pins,indent=2)+'\n');(o/'pseudocode-draft.md').write_text('# Candidate540036 consolidated pseudocode draft\n\nPartial; accepted:false. Locked main image; raw discovered envelope2446bytes. This concatenation preserves ordered packet pseudocode and unresolved child/architectural boundaries. Independent review bindings are not promoted by concatenation.\n\n'+'\n\n'.join(docs));(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(status='partial',accepted=False,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',len(rows),'instructions',len(calls),'calls',len(set(c['target'] for c in calls)),'children',len(returns),'return')
