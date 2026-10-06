from pathlib import Path
import json,hashlib,re
b=Path('g2/build/pseudocode-first/20260930T190500Z');a=b/'analysis';h=lambda x:hashlib.sha256(x).hexdigest();src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';rp=Path('g2/research/corpus/apollo-main/ghidra/open-2026-09-29/functions-000.jsonl');raw=next(q for line in rp.open() if (q:=json.loads(line))['entry']=='00514846');assert raw['ranges']==[['00514846','00514aeb']] and raw['body_bytes']==678 and raw['body_sha256']==h(d[0x514846-0x438000:0x514aec-0x438000]);pins={str(src):h(d),str(rp):h(rp.read_bytes())};rows=[];docs=[];cursor=0x514846
for n in [16428,16430,16432,16434,16436]:
 paths=list(a.glob(f'apollo-main-diagnostic-fixed-library-*-{n}-map/001'));assert len(paths)==1;p=paths[0];q=json.loads((p/'instructions.json').read_text());assert len(q)==1 and q[0]['start']==cursor
 for row in q[0]['instructions']:
  rb=bytes.fromhex(row['bytes']);assert row['address']==cursor and rb==d[cursor-0x438000:cursor-0x438000+len(rb)];cursor+=len(rb);rows.append(row)
 assert cursor==q[0]['end'];docs.append((p/'pseudocode.md').read_text())
 for fn in ['instructions.json','pseudocode.md','receipt.json']:pins[str(p/fn)]=h((p/fn).read_bytes())
assert cursor==0x514aec;addresses={r['address'] for r in rows};calls=[];branches=[];returns=[]
for row in rows:
 m=row['mnemonic'].split('.')[0];op=row['operands'];pc=row['address']
 if m=='bl':calls.append(dict(pc=pc,target=int(re.match(r'([0-9a-f]+)',op)[1],16)))
 elif m in ['b','bpl','bmi','bgt','bge','blt','ble','beq','bne','cbz','cbnz','wls','le']:
  match=re.search(r'(?:^|,\s*)([0-9a-f]{6,8})\s*(?:<|$)',op);assert match,(pc,m,op);dst=int(match[1],16);assert dst in addresses,(pc,dst);branches.append(dict(pc=pc,mnemonic=m,target=dst,qualification='Architectural conditional control transfer; does not establish path feasibility.'))
 elif 'pc}' in op:returns.append(pc)
assert sorted(set(c['target'] for c in calls))==sorted(int(x,16) for x in raw['callees'])
res=dict(status='partial',accepted=False,entry=0x514846,end=cursor,instruction_bytes=678,instruction_rows=len(rows),calls=calls,unique_children=len(set(c['target'] for c in calls)),direct_branch_bindings=branches,return_sites=returns,low_overhead_loop_primary_reference='https://documentation-service.arm.com/static/66b9cafa32f35b31ceb30a11',limitations=['Static code tiling and branch starts only; no child semantic closure, physical ownership, all-path emulator proof or function-boundary completeness.','WLS/LE architectural loopmetadata/cache/fault/interrupt behavior remains explicitly conditional; no replacement with ordinary loops validated.','No corpus admission, freeze, C or gates.']);o=Path('/private/tmp/independent-writer-extra-1');o.mkdir(parents=True,exist_ok=False);(o/'results.json').write_text(json.dumps(res,indent=2)+'\n');(o/'input-pins.json').write_text(json.dumps(pins,indent=2)+'\n');(o/'pseudocode-draft.md').write_text('# Command writer514846 consolidated draft\n\nPartial; accepted:false, child and architecture conditions remain.\n\n'+'\n\n'.join(docs));(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(status='partial',accepted=False,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS678',len(rows),'instructions',len(calls),'call sites',res['unique_children'],'children',len(branches),'direct branches',len(returns),'returns')
