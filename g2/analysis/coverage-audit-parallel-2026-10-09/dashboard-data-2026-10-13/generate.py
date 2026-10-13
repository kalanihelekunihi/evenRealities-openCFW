from pathlib import Path
import json,hashlib,datetime,subprocess
R=Path.cwd();O=Path(__file__).parent;sha=lambda b:hashlib.sha256(b).hexdigest();L=R/'g2/analysis/coverage-audit-parallel-2026-10-09/address-coverage-sample-2026-10-11/inventory.json';I=json.loads(L.read_text());T=json.loads((R/'g2/workflow/target.json').read_text());P=json.loads((R/'g2/analysis/source-discovery-parallel-2026-10-09/partial-artifact-range-unions.json').read_text());K=json.loads((R/'g2/analysis/source-discovery-parallel-2026-10-09/codec-em9305-range-unions-corrected.json').read_text());MI={x['id']:x for x in map(json.loads,(R/'g2/build/pseudocode-first/20260930T190500Z/inventory/images.jsonl').read_text().splitlines())};G=json.loads((R/'g2/analysis/coverage-audit-parallel-2026-10-09/component-percentages-2026-10-10/metrics.json').read_text());stagekeys=['function_mapping','disassembly','pseudocode','C_mapped_lower_bound','C_compile_lower_bound','C_behavior_lower_bound','C_identical_lower_bound','integrated_replacement'];names={'codec':'GX8002 codec','ble_em9305':'EM9305 BLE','touch':'Touch PSoC','case':'Charging case','apollo_main':'Apollo main','apollo_bootloader':'Apollo bootloader'};sources=[]
for p,h in I['inputs_sha256'].items():
 assert sha((R/p).read_bytes())==h;sources.append({'path':p,'sha256':h})
sources.insert(0,{'path':str(L.relative_to(R)),'sha256':sha(L.read_bytes())});functions={x['component']:{'success':x.get('pseudocode_export_functions',[None,None])[0] if x.get('pseudocode_export_functions') else None,'recognized':x.get('pseudocode_export_functions',[None,None])[1] if x.get('pseudocode_export_functions') else None,'scope':'raw identified-function output; codec five historical images only; not reviewed semantics'} for x in G['components']};components=[]
for c in I['components']:
 cid=c['component'];size=c['payload_bytes'];events={0:[],size:[]}
 for bit,key in enumerate(stagekeys):
  for a,b in c['stage_ranges'][key]:events.setdefault(a,[]).append((bit,1));events.setdefault(b,[]).append((bit,-1))
 active=[0]*len(stagekeys);runs=[];points=sorted(events)
 for index,a in enumerate(points[:-1]):
  for bit,d in events[a]:active[bit]+=d;assert active[bit]>=0
  b=points[index+1];mask=sum(1<<bit for bit,v in enumerate(active) if v)
  if runs and runs[-1][1]==a and runs[-1][2]==mask:runs[-1][1]=b
  else:runs.append([a,b,mask])
 assert runs[0][0]==0 and runs[-1][1]==size and all(x[1]==y[0] for x,y in zip(runs,runs[1:]))
 for bit,key in enumerate(stagekeys):assert sum(b-a for a,b,m in runs if m&(1<<bit))==c['stage_unique_bytes'][key]
 spaces=[]
 if cid in ['apollo_main','apollo_bootloader','touch','case']:
  x=next(x for x in P['components'] if x['image_id'].split(':')[0]==cid);off=0 if cid=='apollo_bootloader' else 32;spaces=[{'id':x['image_id'],'kind':'canonical loaded-image address','payloadStart':off,'payloadEnd':size,'addressStart':x['base'],'addressEnd':x['base']+size-off}]
 elif cid=='codec':
  for x in K['codec']:
   im=MI[x['image']];off=im.get('candidate_mapping',{}).get('package_component_offset',[None])[0]
   if off is None:off=MI[im['parent_image_id']]['candidate_mapping']['package_component_offset'][0]+im['source_span'][0]
   spaces.append({'id':'codec:'+x['image'],'kind':'candidate runtime mapping; hardware/loader conditional','payloadStart':off,'payloadEnd':off+x['image_bytes'],'addressStart':x['base'],'addressEnd':x['base']+x['image_bytes'],'qualification':im.get('mapping_status','conditional')})
 else:
  for im in MI.values():
   if im['id'].startswith('ble_em9305:record-'):
    for asp in im['address_spaces']:
     for m in asp['mappings']:spaces.append({'id':im['id']+':'+asp['id'],'kind':'canonical record load mapping; target operation unqualified','payloadStart':im['source_span'][0]+m['image_start'],'payloadEnd':im['source_span'][0]+m['image_end'],'addressStart':m['loaded_start'],'addressEnd':m['loaded_end']})
 unmapped=[];cursor=0
 for sp in sorted(spaces,key=lambda x:x['payloadStart']):
  assert sp['payloadEnd']-sp['payloadStart']==sp['addressEnd']-sp['addressStart']
  if cursor<sp['payloadStart']:unmapped.append([cursor,sp['payloadStart']])
  cursor=max(cursor,sp['payloadEnd'])
 if cursor<size:unmapped.append([cursor,size])
 modules=[{'name':r['module'],'stage':r['stage'],'origin':r['source_origin'],'confidence':r['boundary_confidence'],'bytes':r['unique_payload_bytes'],'ranges':r['ranges_payload_half_open'],'missing':r['missing_join_fields']} for r in I['module_rows'] if r['component']==cid and r['stage'] in ['C_mapped_lower_bound','attribution_only']]
 comp=next(x for x in T['components'] if x['id']==cid);components.append({'id':cid,'name':names[cid],'payloadBytes':size,'sha256':comp['sha256'],'outline':[0,size],'coordinate':'payload file offsets; translate only using addressSpaces','addressSpaces':spaces,'withoutAddressBinding':unmapped,'runs':runs,'modules':modules,'summary':c['stage_unique_bytes'],'functionCounts':functions[cid],'identifiedEnvelopeBytes':c['mapped_function_envelope_bytes'],'codeOnlyDenominator':None,'sourceComplete':False,'integratedReplacementBytes':0})
revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();d={'schema':'opencfw-flash-stages-v1','asOfUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'version':'s200_v2.2.6.10','gitRevision':revision,'workspaceQualification':'Concurrent working changes; git revision is not complete file identity; source hashes govern.','bundleSha256':T['bundle']['sha256'],'runEncoding':['payloadStartInclusive','payloadEndExclusive','stageBitmask'],'stages':[{'bit':i,'key':k} for i,k in enumerate(stagekeys)],'sources':sources,'components':components,'rules':['Use separate component wrapper and address-space lanes; never global contiguous flash.','Stage layers overlap; bitmask preserves every gap without sampling.','Color priority exact C > compiled C > pseudocode > disassembly > unknown; mapped C alone is hatch/annotation, not compiled.','compiled C means selected mapped source compile; not integrated replacement or safe all-input behavior.','All complement/code-only classifications remain unknown, not binary-only.','Pseudocode is authenticated raw output; not full understood-function coverage.','Module labels are inferred source/ownership groups; storage partitions are not C module boundaries.','No newer aggregate symbol count is mapped spatially.'],'totals':{'referenceBlobBytes':4300283,'integratedReplacementBytes':0,'fullSourceComponents':0,'components':6,'completeCompiledCPercent':None}}
(O/'flash-dashboard.json').write_text(json.dumps(d,separators=(',',':')));print('bytes', (O/'flash-dashboard.json').stat().st_size,'runs',sum(len(c['runs']) for c in components),'source hashes',len(sources));(O/'validation.json').write_text(json.dumps({'pass':True,'componentCount':6,'payloadRunPartitionComplete':True,'stageUnionCountsMatch':True,'addressLengthAssertions':True,'losslessNoDownsampling':True,'datasetSha256':sha((O/'flash-dashboard.json').read_bytes())},indent=2)+'\n')
