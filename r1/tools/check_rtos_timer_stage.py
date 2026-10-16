#!/usr/bin/env python3
"""Validate isolated timer receipts and compose source objects without promotion."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'r1/research/source-build'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 names={'rtos-timer-runtime':('timer-runtime.o',12349),'rtos-timer-queue':('timer-queue.o',1849),'rtos-timer-task-wait':('task-wait.o',15121)}
 objects=[BASE/'board/native-board.o'];reports={};receipts={};board=json.loads((BASE/'board/report.json').read_text());board_objects=set(board['objects'])
 for name,(obj,count) in names.items():
  folder=BASE/name;rp=folder/'report.json';r=json.loads(rp.read_text());vp=folder/'verification.json';v=json.loads(vp.read_text());assert v['report_sha256']==sha(rp) and v['driver_sha256']==sha(ROOT/'r1/tools'/('verify_'+name.replace('-','_')+'.py')) and v['comparisons']==count
  assert v['application_sha256']==sha(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin')
  assert sha(folder/obj)==r['selected_object_sha256']
  for p,digest in r['inputs'].items():assert sha(ROOT/p)==digest,p
  if 'source_slices' in r:
   raw=(ROOT/r['upstream_source']).read_bytes();assert hashlib.sha256(raw).hexdigest()==r['upstream_sha256'];text=raw.decode()
   for row in r['source_slices']:assert hashlib.sha256(text[row['start']:row['end']].encode()).hexdigest()==row['sha256'],row['name']
  
  if str((folder/obj).relative_to(ROOT)) not in board_objects:objects.append(folder/obj)
  reports[name+'/report.json']=sha(rp);receipts[name+'/verification.json']=sha(vp)
 evidence=BASE/'rtos-timer-runtime/evidence.json';e=json.loads(evidence.read_text());app=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert e['application_sha256']==hashlib.sha256(app).hexdigest()
 for span in e['spans']:
  p=evidence.parent/span['ghidra_file'];assert sha(p)==span['ghidra_sha256'];start=int(span['entry'],16)-0x27000;assert bytes(json.loads(p.read_text())['data'])==app[start:start+span['bytes']]
 assert sha(ROOT/e['rea_inventory'])==e['rea_inventory_sha256']
 board=json.loads((BASE/'board/report.json').read_text());assert sha(objects[0])==board['relocatable_sha256']
 out=BASE/'rtos-timer-runtime/timer-stage.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(out)],check=True)
 before=set(undefined_symbols(objects[0])[0]);after=set(undefined_symbols(out)[0]);assert not after-before,sorted(after-before)
 result=dict(driver_sha256=sha(Path(__file__)),board_report_sha256=sha(BASE/'board/report.json'),board_object_sha256=sha(objects[0]),provider_reports=reports,isolated_receipts=receipts,evidence_sha256=sha(evidence),selected_object_sha256=sha(out),new_unresolved_symbols=sorted(after-before),resolved_board_symbols=sorted(before-after),comparisons=sum(n for _,n in names.values()),canonical_board_includes_timer_objects=all(str((BASE/name/obj).relative_to(ROOT)) in board_objects for name,(obj,_) in names.items()),frontier_promoted_by_this_check=False,combined_graph_verified=False,byte_identity=False,limitations=['Relocatable composition only; actual timer/queue/task-wait scheduler workflows are checked separately by graph-verification.json. Callback execution and physical time progression remain explicit gates. No new ownership rows are admitted by this staging check.'])
 (out.parent/'stage-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(result['comparisons'],'isolated comparisons; staged link adds no unresolved symbols; resolved:',result['resolved_board_symbols'])
if __name__=='__main__':main()
