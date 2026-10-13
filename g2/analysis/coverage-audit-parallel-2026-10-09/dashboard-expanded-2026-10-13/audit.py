from pathlib import Path
import json,hashlib,re,collections,os,datetime
R=Path.cwd();O=Path(__file__).parent;sha=lambda b:hashlib.sha256(b).hexdigest();base=json.loads((R/'g2/analysis/coverage-audit-parallel-2026-10-09/dashboard-data-2026-10-13/flash-dashboard.json').read_text());sizes={c['id']:c['payloadBytes'] for c in base['components']};bounds={c['id']:c['addressSpaces'] for c in base['components']};SOURCE_ROOTS=['g2/components','g2/analysis','g2/firmware_c','g2/research','g2/build','g2/tools','g2/config-recovered','g2/docs'];excluded=[];files=[];scanstats=collections.Counter();source=[];compilejoins=[];receiptevidence=[];missing=[]
prune={'node_modules','.git','__pycache__','.venv','venv','acquisitions','tools','toolchain','toolchains','source','scratch','reproduction','replay'}
# Directory-name 'source' is pruned only inside recognized compiler/emulator projects.
for root in SOURCE_ROOTS:
 for d,ds,fs in os.walk(R/root):
  for sub in list(ds):
   if sub in prune and (sub!='source' or any(x in d.lower() for x in ['qemu','toolchain','binutils','gcc','gdb','ablation','ghidra-mcp'])):
    excluded.append({'path':str((Path(d)/sub).relative_to(R)),'reason':'tool/vendor dependency, cache or replicated replay subtree; not product source census'});ds.remove(sub)
  for f in fs:
   p=Path(d)/f;rel=str(p.relative_to(R));ext=p.suffix.lower();scanstats[ext or '<none>']+=1
   if ext in ['.c','.s','.h'] or f.endswith('receipt.json') or f in ['REPORT.md','README.md','inventory.json','results.json','build-receipt.json','provider-census.json','mapped-functions.json']:files.append((p,rel))
def component(p):
 s=p.lower()
 if any(x in s for x in ['/em9305/','/components/em9305/','/ble_em9305/','/em9305-','/em-']):return 'ble_em9305'
 if any(x in s for x in ['/codec/','/nationalchip','/csky','/gx-native/','/image_b_sram']):return 'codec'
 if any(x in s for x in ['/components/touch/','/touch/','/touch-','/touch_']):return 'touch'
 if any(x in s for x in ['/components/case/','/case/','/case-','/case_','/m0/']):return 'case'
 if any(x in s for x in ['/bootloader/','/bootloader-','/bootloader_','/bootloader-completion','/apollo/boot','/startup-initialize/']):return 'apollo_bootloader'
 if any(x in s for x in ['/components/main/','/components/audio/','/apollo/','/peripherals/','/main-','/audio-','/smp-','/tlsf-','/flashdb-','/wsf-','/kernel-','/extended-log']):return 'apollo_main'
 return 'unassigned'
def origin(p,t):
 if any(x in p for x in ['/upstream/','/third-party/','/pdl/']):return 'upstream_source'
 if any(x in p.lower() for x in ['harness','fixture','simulator','stub','test_','/tests/']):return 'test_or_fixture'
 if re.search(r'\bundefined[1248]?\b',t) or '/decomp' in p or '/research/corpus/' in p:return 'generated_pseudocode'
 return 'recreated_or_candidate_source_unreviewed'
def union(rs):
 out=[]
 for a,b in sorted(rs):
  if out and a<=out[-1][1]:out[-1][1]=max(b,out[-1][1])
  else:out.append([a,b])
 return out
def count(rs):return sum(b-a for a,b in union(rs))
# Catalogue endpoints allow entry-named source candidates without guessing next function boundaries.
cat=collections.defaultdict(dict)
P=json.loads((R/'g2/analysis/source-discovery-parallel-2026-10-09/partial-artifact-range-unions.json').read_text())
for x in P['components']:
 cid=x['image_id'].split(':')[0]
 for p in (R/x['run_path']).parent.glob('functions*.jsonl'):
  for l in p.read_text().splitlines():
   r=json.loads(l);cat[cid][int(r['entry'],16)]={'ranges':[[int(a,16),int(b,16)+1] for a,b in r['ranges']],'stock_sha256':r['body_sha256'],'metadata':str(p.relative_to(R)),'qualification':'recognized function boundaries; candidate correspondence not equivalence'}
E=json.loads((R/'g2/analysis/c-source-completion-20261011/em9305/body-coverage-boundary.json').read_text())
for x in E['native_envelopes_with_C_candidates']:cat['ble_em9305'][int(x['start'],16)]={'ranges':[[int(x['start'],16),int(x['end_exclusive'],16)]],'qualification':'declared reconstructed C envelope; endpoint receipt'}
latest={};ps=sorted((R/'g2/build/c-firmware').glob('*/*/receipt.json'),key=lambda p:p.stat().st_mtime,reverse=True)
for p in ps:
 try:j=json.loads(p.read_text())
 except Exception:continue
 for c,v in j.get('images',{}).items():
  if c not in latest:latest[c]={'receipt':str(p.relative_to(R)),'receipt_sha256':sha(p.read_bytes()),'captured_utc':j.get('captured_utc'),'sourceComplete':v.get('source_complete'),'fullPayloadLinked':v.get('full_payload_linked'),'candidateCompiles':v.get('candidate_compilation_passed'),'definedSymbols':len(v.get('relocatable_link',{}).get('defined_symbols',[])),'imports':len(v.get('relocatable_link',{}).get('unresolved_symbols',[])),'value':v}
 if len(latest)==6:break
compiled=collections.defaultdict(list)
def walk(o,receipt,cid):
 if isinstance(o,dict):
  p=o.get('source');h=o.get('source_sha256');obj=o.get('object');oh=o.get('object_sha256');snap=o.get('compile_source_snapshot',{})
  p=p or snap.get('path');h=h or snap.get('sha256_after')
  if not obj and oh and isinstance(o.get('argv'),list) and '-o' in o['argv']:
   candidate=o['argv'][o['argv'].index('-o')+1]
   obj=str(Path(o['log']).parent/Path(candidate).name) if candidate.startswith('/out/') and o.get('log') else candidate
  if p and h and obj and oh and o.get('returncode')==0:
   fp=Path(p);fp=fp if fp.is_absolute() else R/fp;op=Path(obj);op=op if op.is_absolute() else R/op
   if fp.is_file() and op.is_file():
    ok=sha(fp.read_bytes())==h and sha(op.read_bytes())==oh
    row={'component':cid,'source':str(fp.relative_to(R)),'source_sha256':h,'object':str(op.relative_to(R)),'object_sha256':oh,'receipt':receipt,'currentHashCoherent':ok,'sourceSnapshotStable':snap.get('stable_during_command'),'validation':o.get('validation','compile only')}
    compilejoins.append(row)
    if ok:compiled[row['source']].append(row)
  for v in o.values():walk(v,receipt,cid)
 elif isinstance(o,list):
  for v in o:walk(v,receipt,cid)
for cid,v in latest.items():walk(v.pop('value'),v['receipt'],cid)
for p,rel in files:
 if p.suffix.lower()!='.c':continue
 st=p.stat()
 if st.st_size>1024*1024:excluded.append({'path':rel,'reason':'C file >1MiB: metadata only; avoid binary/model/generated payload masquerading as source'});continue
 try:b=p.read_bytes();t=b.decode('utf-8')
 except Exception:excluded.append({'path':rel,'reason':'non-text source'});continue
 sourceHash=sha(b);sourceLength=len(b);cid=component(rel);kind=origin(rel,t);clean=re.sub(r'/\*.*?\*/|//[^\n]*',' ',t,flags=re.S);clean=re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'','""',clean)
 defs=re.findall(r'\b([A-Za-z_]\w*)\s*\([^;{}]*\)\s*(?:__attribute__\s*\(\([^{}]*\)\)\s*)?\{',clean);defs=[x for x in defs if x not in ['if','for','while','switch']]
 definition_entries=sorted({int(m.group(1),16) for name in defs for m in [re.search(r'(?:^|_)([0-9a-fA-F]{6,8})(?:_|$)',name)] if m})
 # Explicit stock range comments are correspondence declarations, not a guessed whole file location.
 claims=[(int(a,16),int(b,16)) for a,b in re.findall(r'0x([0-9a-fA-F]{6,8})\s*(?:\.\.|[-–])\s*0x?([0-9a-fA-F]{6,8})',t[:16000])]
 candidates=[]
 if kind not in ['test_or_fixture','generated_pseudocode'] and cid in bounds:
  for e in definition_entries:
   if e in cat[cid]:
    for a,b in cat[cid][e]['ranges']:candidates.append({'start':a,'end':b,'join':'address-suffixed C definition to existing function catalogue','confidence':'candidate correspondence; function body semantics unproved'})
  for a,b in claims:
   if a<b:candidates.append({'start':a,'end':b,'join':'explicit source stock-range annotation','confidence':'declared candidate range; annotation may cover graph rather than one body'})
 translated=[];ambiguous=[]
 for q in candidates:
  compatible=[sp for sp in bounds[cid] if sp['addressStart']<=q['start']<q['end']<=sp['addressEnd']]
  if len(compatible)==1:
   sp=compatible[0];a=q['start']-sp['addressStart']+sp['payloadStart'];bb=q['end']-sp['addressStart']+sp['payloadStart'];translated.append({'payloadRange':[a,bb],'addressSpace':sp['id'],'originalRange':[q['start'],q['end']],'join':q['join'],'confidence':q['confidence']})
  else:ambiguous.append(q)
 source.append({'path':rel,'sha256':sourceHash,'bytes':sourceLength,'component':cid,'origin':kind,'textFunctionDefinitionsHeuristic':len(defs),'addressNamedDefinitions':definition_entries,'correspondenceCandidates':translated,'unplacedAddressClaims':ambiguous,'currentCompileReceiptJoins':compiled.get(rel,[]),'spatiallyVerifiedSemantics':False,'excludedFromColor':kind in ['test_or_fixture','generated_pseudocode']})
# Existing whole-repo receipt index is metadata classification, not re-execution of tests.
receipt_index=[]
for p,rel in files:
 if p.suffix!='.json':continue
 s=p.stat().st_size
 if s>1024*1024:excluded.append({'path':rel,'reason':'large JSON omitted from semantic receipt parse; usually per-case vectors, retained in file index'});continue
 try:j=json.loads(p.read_text())
 except Exception:continue
 if not isinstance(j,dict):continue
 keys=list(j);scope=j.get('scope',j.get('limits',j.get('limitations','')))
 receipt_index.append({'path':rel,'sha256':sha(p.read_bytes()),'component':component(rel),'keys':keys[:20],'scope':str(scope)[:400],'caseCountReported':j.get('cases_passed',j.get('cases',j.get('count'))) if isinstance(j.get('cases_passed',j.get('cases',j.get('count'))),(int,float)) else None,'result':j.get('result',j.get('status',j.get('all_pass'))),'qualifier':'existing receipt report only; no execution/semantic promotion'})
summary=[]
for cid in [c['id'] for c in base['components']]+['unassigned']:
 ss=[s for s in source if s['component']==cid];unique={s['sha256'] for s in ss};eligible=[s for s in ss if not s['excludedFromColor']];placed=[q['payloadRange'] for s in eligible for q in s['correspondenceCandidates']];comp=[q['payloadRange'] for s in eligible if s['currentCompileReceiptJoins'] for q in s['correspondenceCandidates']]
 summary.append({'component':cid,'sourceFiles':len(ss),'uniqueSourceHashes':len(unique),'heuristicCDefinitions':sum(s['textFunctionDefinitionsHeuristic'] for s in eligible),'fixtureFiles':sum(s['origin']=='test_or_fixture' for s in ss),'pseudocodeFiles':sum(s['origin']=='generated_pseudocode' for s in ss),'currentSourceAndObjectHashVerifiedCompileFiles':sum(bool(s['currentCompileReceiptJoins']) for s in eligible),'unplacedSourceFiles':sum(not s['correspondenceCandidates'] for s in eligible),'candidateCorrespondenceBytes':count(placed),'candidateCompileCorrespondenceBytes':count(comp),'candidateRanges':union(placed),'compileCandidateRanges':union(comp),'semanticallyVerifiedCompiledCoverage':'unknown; these are provisional candidate joins, separate from baseline verified colors'})
result={'asOfUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'target':'s200_v2.2.6.10','scanRoots':SOURCE_ROOTS,'scanFileCountsByExtension':dict(scanstats),'filesEnumeratedForInspection':len(files),'explicitExcludedSubtreesAndFiles':excluded,'latestComponentBuilds':latest,'compileJoins':compilejoins,'componentSummary':summary,'sourceFiles':source,'receiptIndex':receipt_index,'baselineDashboard':base,'method':['Definition extraction is heuristic; counts are not recovered firmware functions.','Identical source hashes deduplicate copies, not logical functions.','Exact source/object hash and successful compile records establish compile evidence for source files.','Only address-named definitions or explicit range claims permit provisional spatial joins; no guessed endpoints.','Catalogue boundaries can include literals/padding; semantic equivalence remains unproved.','Fixture/pseudocode files excluded from candidate color.','No new builds, tests, recovery or dependency retrieval.']}
(O/'expanded-evidence.json').write_text(json.dumps(result,separators=(',',':')));print('source files',len(source),'receipt index',len(receipt_index),'compile joins',len(compilejoins),'bytes',(O/'expanded-evidence.json').stat().st_size);print([(s['component'],s['sourceFiles'],s['currentSourceAndObjectHashVerifiedCompileFiles'],s['candidateCompileCorrespondenceBytes']) for s in summary])
