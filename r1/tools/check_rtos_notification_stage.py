#!/usr/bin/env python3
"""Bind isolated notification contracts and closed canonical source composition."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';app_hash=sha(app);board=json.loads((BASE/'board/report.json').read_text());obj=BASE/'board/native-board.o';assert sha(obj)==board['relocatable_sha256'];objects=[obj];reports={};receipts={};evidence={};board_objects=set(board['objects'])
 for name,filename,count in [('rtos-notification-wrappers','notification-wrappers.o',25128),('rtos-notification-tasks','notification-tasks.o',14840),('rtos-event-groups','event-groups.o',4568),('rtos-timer-pend','timer-pend.o',4568),('rtos-unordered-event','unordered-event.o',7290)]:
  folder=BASE/name;rp=folder/'report.json';r=json.loads(rp.read_text());o=folder/filename;assert sha(o)==r['selected_object_sha256'] and r['rtos_report_sha256']==sha(BASE/'rtos/report.json');
  if str(o.relative_to(ROOT)) not in board_objects:objects.append(o)
  reports[name+'/report.json']=sha(rp)
  for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
  if 'upstream_source' in r:
   raw=(ROOT/r['upstream_source']).read_bytes();assert hashlib.sha256(raw).hexdigest()==r['upstream_sha256'];text=raw.decode()
   for row in r['source_slices']:assert hashlib.sha256(text[row['start']:row['end']].encode()).hexdigest()==row['sha256'],row['name']
  else:
   for unit in r['units']:assert sha(ROOT/unit['source'])==unit['source_sha256']
  vp=BASE/'rtos-event-groups/verification.json' if name=='rtos-timer-pend' else folder/'verification.json';v=json.loads(vp.read_text());assert v['application_sha256']==app_hash and v['comparisons']==count
  if name in ('rtos-event-groups','rtos-timer-pend'):assert v['provider_reports'][name+'/report.json']==sha(rp) and v['driver_sha256']==sha(ROOT/'r1/tools/verify_rtos_event_groups.py')
  else:assert v['report_sha256']==sha(rp) and v['driver_sha256']==sha(ROOT/'r1/tools'/('verify_'+name.replace('-','_')+'.py'))
  receipts[str(vp.relative_to(BASE))]=sha(vp)
  if name=='rtos-notification-tasks':assert v['priority_report_sha256']==sha(BASE/'rtos-interrupt-priority/report.json') and v['priority_object_sha256']==sha(BASE/'rtos-interrupt-priority/interrupt-priority.o') and v['assertion_comparisons']==4830
  ep=folder/'evidence.json';e=json.loads(ep.read_text());assert e['application_sha256']==app_hash and e['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf')
  for span in e['spans']:
   p=folder/span['ghidra_file'];a=int(span['entry'],16);assert sha(p)==span['ghidra_sha256'] and bytes(json.loads(p.read_text())['data'])==app.read_bytes()[a-0x27000:a-0x27000+span['bytes']]
  assert sha(ROOT/e['rea_inventory'])==e['rea_inventory_sha256'];evidence[name+'/evidence.json']=sha(ep)
 next_path=BASE/'rtos-notification-wrappers/event-next-target.json';n=json.loads(next_path.read_text());body=next_path.parent/n['rea_body'];pseudo=next_path.parent/n['rea_pseudocode'];assert sha(body)==n['rea_body_sha256'] and sha(pseudo)==n['rea_pseudocode_sha256'];info=json.loads(body.read_text());assert info['subject']['digest']['sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and info['normalized_result']['body']['ranges']==n['observed_ranges'] and info['normalized_result']['body']['total_bytes']==46 and info['normalized_result']['body']['non_contiguous']
 for span in n['spans']:
  p=next_path.parent/span['ghidra_file'];a=int(span['entry'],16);assert sha(p)==span['ghidra_sha256'] and bytes(json.loads(p.read_text())['data'])==app.read_bytes()[a-0x27000:a-0x27000+span['bytes']]
 out=BASE/'rtos-notification-wrappers/notification-stage.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(out)],check=True);before=set(undefined_symbols(obj)[0]);after=set(undefined_symbols(out)[0]);new=sorted(after-before);assert not new,new
 result=dict(driver_sha256=sha(Path(__file__)),application_sha256=app_hash,board_report_sha256=sha(BASE/'board/report.json'),board_object_sha256=sha(obj),provider_reports=reports,isolated_receipts=receipts,evidence=evidence,event_next_target_sha256=sha(next_path),selected_object_sha256=sha(out),comparisons=51826,resolved_board_symbols=sorted(before-after),new_unresolved_symbols=new,canonical_frontier_promoted_by_this_check=False,canonical_board_includes_notification_objects=all(str(p.relative_to(ROOT)) in board_objects for p in (BASE/'rtos-notification-wrappers/notification-wrappers.o',BASE/'rtos-notification-tasks/notification-tasks.o',BASE/'rtos-event-groups/event-groups.o',BASE/'rtos-timer-pend/timer-pend.o',BASE/'rtos-unordered-event/unordered-event.o')),combined_graph_verified_by_this_check=False,byte_identity=False,limitations=['Wrappers and indexed notification/delay task bodies have isolated native contracts. The source stage resolves all four wrapper references using tested event-group, timer-pend and unordered-wake providers without adding unresolved symbols.','The independent graph/audit receipts establish bounded deferred-callback/event-wake composition; this check does not execute that graph. Real blocking resumption, physical interrupts/scheduling and whole-image byte closure remain open.']);(out.parent/'stage-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(result['comparisons'],'isolated comparisons; resolved:',result['resolved_board_symbols'],'; new unresolved symbols:',new)
if __name__=='__main__':main()
