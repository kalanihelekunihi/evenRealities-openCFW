from pathlib import Path
import json,hashlib,ast
O=Path(__file__).resolve().parent;D=Path('g2/analysis/apollo-lz4-source-discriminator-20261009T211300Z');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();c=[]
def ck(n,v):c.append({'check':n,'pass':bool(v)})
for p,h in json.loads((D/'DELIVERABLES.json').read_text())['files'].items():ck('deliverable '+p,sha(Path(p))==h)
for x in json.loads((D/'acquisition.json').read_text()):ck('source acquisition '+x['file'],sha(Path(x['file']))==x['sha256'] and Path(x['file']).stat().st_size==x['bytes'] and x['status']==200)
r=json.loads((D/'finite-results.json').read_text());f=json.loads((D/'frozen-fixtures.json').read_text());s=json.loads((D/'SUMMARY.json').read_text());ck('exact frozen12 corpus',len(r['rows'])==r['fixtures']==s['fixtures']==12 and [x['fixture'] for x in r['rows']]==f['cases'])
for row in r['rows']:
 name=row['fixture']['name'];a=row['stock'];w=row['locked_caller'];cap=row['fixture']['capacity']
 ck('stock/caller guards '+name,all(a['guards'].values()) and all(w['guards'].values()))
 ck('caller return '+name,w['return']==max(a['return'],0))
 ck('capacity bytes '+name,len(bytes.fromhex(a['output_capacity_hex']))==cap and len(bytes.fromhex(w['output_capacity_hex']))==cap)
 for v,x in row['C'].items():ck('exact C return/full capacity '+name+v,x['return']==a['return'] and x['output_capacity_hex']==a['output_capacity_hex'] and x['destination_before'] and x['destination_after'] and row['C_matches'][v]['return_equal'] and row['C_matches'][v]['full_capacity_equal'])
 ck('caller capacity equality '+name,w['output_capacity_hex']==a['output_capacity_hex'] if row['fixture']['capacity']!=0 and row['fixture']['compressed_hex'] else w['output_capacity_hex']=='a5'*cap)
expected=[-1,0,5,-2,-2,-2,-2,26,-6,-2,26,-6];ck('explicit exact result oracle',[x['stock']['return'] for x in r['rows']]==expected)
ck('zero offset full bytes',r['rows'][7]['stock']['output_capacity_hex']==(b'A'+bytes(20)+b'abcde').hex())
ck('Python policy distinction',r['rows'][0]['emulator_python']['status']=='accepted' and r['rows'][7]['emulator_python']['status']=='rejected')
p=Path('/Users/kalani/Repo/jimrandomh/g2-firmware-emulator/src/g2emu/device.py');txt=p.read_text();node=next(n for n in ast.parse(txt).body if isinstance(n,ast.FunctionDef) and n.name=='_lz4_block_decompress');ck('unchanged extracted Python identity',sha(p)==r['emulator_source_sha256'] and hashlib.sha256(ast.get_source_segment(txt,node).encode()).hexdigest()==r['emulator_function_sha256'])
code=(D/'finite_compare.py').read_text();ck('one instruction profile/no function stubs', 'count=1' in code and 'reg_write' not in code[code.index('def hook('):code.index('u.hook_add(')] and 'if pc==STOP:done.append(True);uc.emu_stop();return' in code)
ck('guards precede comparison','assert all(a[\'guards\'].values())' in code and code.index("assert all(a['guards'].values())")<code.index('match={v:'))
ck('capacity guards and full comparison','DST+cap,32' in code and 'full_capacity_equal' in code)
identity=json.loads((D/'linux-runtime-identity.json').read_text());ck('host comparator binary identity',all(sha(D/v/'liblz4.so')==h for v,h in identity['comparison_libraries'].items()))
res={'all_pass':all(x['pass'] for x in c),'checks':c,'limitations':['No replay. Receipt and harness audit only.','Sentinel write/source-retention checks do not detect out-of-input reads or distant writes outside observed backing bands.','Compiled Linux source comparator uses a different architecture from stock.','No uniform whole-library/version identity claim.']};(O/'LZ4-FINAL-INDEPENDENT-VERIFICATION.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps({'all_pass':res['all_pass'],'checks':len(c),'failed':[x['check'] for x in c if not x['pass']]},indent=2))
