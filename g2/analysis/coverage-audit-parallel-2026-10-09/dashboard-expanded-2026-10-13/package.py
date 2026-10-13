from pathlib import Path
import json,hashlib,datetime
O=Path(__file__).parent;sha=lambda b:hashlib.sha256(b).hexdigest();A=json.loads((O/'expanded-evidence.json').read_text());M=json.loads((O/'inventory-matrix.json').read_text());RES=json.loads((O/'resource-evidence.json').read_text());base=A['baselineDashboard'];compact=json.loads(json.dumps(base));compact['schema']='opencfw-expanded-dashboard-v2';compact['asOfUTC']=datetime.datetime.now(datetime.timezone.utc).isoformat();compact['fullEvidenceLibraryId']='libfile_3d9914466c448191be6edc3918867204';compact['scope']='bounded whole-repository inventory with verified baseline, explicitly provisional compiled-C address joins and confirmed resources';compact['stages'].append({'bit':8,'key':'compile_candidate_address_correspondence','qualification':'current source/object hashes verify compilation; original-range relation declared/inferred, not original behavior or equality'});compact['stages'].append({'bit':9,'key':'confirmed_nonMCU_code_resource','qualification':'resource bytes authenticate; may overlap historical function envelopes'});compact['stages'].append({'bit':10,'key':'accelerator_command_stream','qualification':'non-MCU instructions, not globally non-executable'});compact['scanCoverage']={'roots':A['scanRoots'],'CFilesInspected':len(A['sourceFiles']),'receiptArtifactsIndexed':len(A['receiptIndex']),'excludedSubtreesOrOversizeFiles':len(A['explicitExcludedSubtreesAndFiles']),'countsIncludeRawPseudocodeFixturesCopiesTooling':True};compact['resourceKinds']=sorted({r['kind'] for r in RES['resourceIntervals']});compact['resourceEvidence']=RES['resourceInputHashes'];compact['resourceRuns']=[]
for ci,c in enumerate(compact['components']):
 cid=c['id'];c.pop('modules',None);c['wholeRepositoryWork']=next(x for x in A['componentSummary'] if x['component']==cid).copy();c['wholeRepositoryWork'].pop('candidateRanges');c['wholeRepositoryWork'].pop('compileCandidateRanges');c['buildProgress']=M['currentBuildProgress'].get(cid);c['currentBuildReceipt']=A['latestComponentBuilds'].get(cid);c['evidenceLevelNotice']='Unknown address/stage means unclassified at this evidence level, not no work. File/symbol/test counts are not firmware-function coverage.'
 s=next(x for x in A['componentSummary'] if x['component']==cid);events={0:[],c['payloadBytes']:[]}
 for a,b,mask in c['runs']:
  for bit in range(8):
   if mask&(1<<bit):events.setdefault(a,[]).append((bit,1));events.setdefault(b,[]).append((bit,-1))
 for a,b in s['compileCandidateRanges']:events.setdefault(a,[]).append((8,1));events.setdefault(b,[]).append((8,-1))
 for r in RES['resourceIntervals']:
  if r['component']!=cid:continue
  a,b=r['payloadRange'];bit=9 if r['isConfirmedNonMCUCode'] else 10;events.setdefault(a,[]).append((bit,1));events.setdefault(b,[]).append((bit,-1));compact['resourceRuns'].append([ci,a,b,compact['resourceKinds'].index(r['kind']),r['label'],r['contentsSummary'][:80]])
 active=[0]*11;runs=[];points=sorted(events)
 for i,a in enumerate(points[:-1]):
  for bit,v in events[a]:active[bit]+=v;assert active[bit]>=0
  b=points[i+1];mask=sum(1<<i for i,v in enumerate(active) if v)
  if runs and runs[-1][1]==a and runs[-1][2]==mask:runs[-1][1]=b
  else:runs.append([a,b,mask])
 assert runs[0][0]==0 and runs[-1][1]==c['payloadBytes'] and all(a[1]==b[0] for a,b in zip(runs,runs[1:]));c['runs']=runs
 for bit,st in enumerate(compact['stages'][:8]):assert sum(b-a for a,b,mask in runs if mask&(1<<bit))==c['summary'][st['key']]
 assert sum(b-a for a,b,mask in runs if mask&256)==s['candidateCompileCorrespondenceBytes']
 c['resourceUnionBytes']=sum(b-a for a,b,mask in runs if mask&512);c['provisionalCompiledAddressBytes']=sum(b-a for a,b,mask in runs if mask&256)
compact['rules']+=['Lead dashboard with wholeRepositoryWork and buildProgress cards before address map.','Never present baseline verified joins as exhaustive repo work.','bit8 must be visually distinguished from verified C: candidate address binding, not behavior/equality.','Overlay resource types with labels; do not infer font/image/text-file/padding from strings or gaps.','Fonts/calibration evidence without exact asset bounds stays prominently unplaced.','Do not derive whole executable denominator by subtracting partial resource coverage.']
compact['unplacedResourceEvidence']={k:{'evidenceFiles':len(v['paths']),'reason':v['reason']} for k,v in RES['unplacedResourceEvidence'].items()}
# Source-family inventory cards with representative paths; full lists remain in the transfer artifact.
for c in compact['components']:
 ss=[s for s in A['sourceFiles'] if s['component']==c['id']];families={}
 for s in ss:
  family=str(Path(s['path']).parent);v=families.setdefault(family,{'files':0,'compileHashJoins':0});v['files']+=1;v['compileHashJoins']+=bool(s['currentCompileReceiptJoins'])
 c['workFamilies']=[{'path':p,**v} for p,v in sorted(families.items(),key=lambda x:(-x[1]['compileHashJoins'],-x[1]['files'],x[0]))[:6]]
full={'schema':'opencfw-expanded-evidence-v2','compactDashboard':compact,'fullSourceInventory':A,'independentBuildMatrix':M,'resourceEvidence':RES,'scanAndValidationLimits':['All eight named roots enumerated with explicit excluded vendor/tool/cache/replay/oversize items.','Receipt index is existing-report evidence, not independently rerun behavior.','Definitions regex is heuristic; source origin unknown means not established recreated.','Current selected compile source/object hashes checked; native original equivalence not inferred.','Versions/copies deduplicated by content hashes for file inventory and by image+range for spatial layers.','Confirmed resources do not complete whole-image classification.']}
(O/'compact-dashboard.json').write_text(json.dumps(compact,separators=(',',':')));(O/'expanded-dashboard-data.json').write_text(json.dumps(full,separators=(',',':')));(O/'validation.json').write_text(json.dumps({'pass':True,'allSixPayloadPartitionsComplete':True,'originalEightStageCountsPreserved':True,'provisionalCompilationUnionsMatch':True,'resourceHashRejections':len(RES['rejectedBindings']),'compactBytes':(O/'compact-dashboard.json').stat().st_size,'fullBytes':(O/'expanded-dashboard-data.json').stat().st_size,'compactSha256':sha((O/'compact-dashboard.json').read_bytes()),'fullSha256':sha((O/'expanded-dashboard-data.json').read_bytes()),'losslessRuns':sum(len(c['runs']) for c in compact['components'])},indent=2)+'\n');print((O/'validation.json').read_text())
