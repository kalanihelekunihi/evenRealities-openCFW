#!/usr/bin/env python3
"""Compose recovered product scheduler and pinned timer providers without stubs."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
from audit_rtos_timer_controls import audit as audit_timer_controls
from audit_rtos_timer_new import audit as audit_timer_new
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 audit_timer_controls();audit_timer_new();rp=BASE/'board/report.json';board=json.loads(rp.read_text());board_obj=BASE/'board/native-board.o';assert sha(board_obj)==board['relocatable_sha256'];objects=[board_obj];reports={};receipts={};board_objects=set(board['objects']);included=[]
 for name,filename,receipt_name in [('native-delayed-schedule','native_delayed_schedule.o','verification.json'),('native-delayed-push','native_delayed_push.o','verification.json'),('native-delayed-reschedule','native_delayed_reschedule.o','verification.json'),('rtos-timer-controls','timer-controls.o','verification.json'),('rtos-timer-active','timer-active.o',None),('native-delayed-state','native_delayed_state.o',None),('native-delayed-worker','native_delayed_worker.o','verification.json'),('native-delayed-initialize','native_delayed_initialize.o','verification.json'),('rtos-timer-new','timer-new.o','verification.json'),('rtos-timer-id','timer-id.o',None),('native-delayed-cancel','native_delayed_cancel.o','verification.json')]:
  p=BASE/name/'report.json';r=json.loads(p.read_text());obj=p.parent/filename;assert sha(obj)==r['units'][0]['object_sha256'];included.append(str(obj.relative_to(ROOT)) in board_objects)
  if not included[-1]:objects.append(obj)
  reports[name+'/report.json']=sha(p)
  for path,h in r['inputs'].items():assert sha(ROOT/path)==h,path
  if receipt_name:
   v=p.parent/receipt_name;receipts[name+'/'+receipt_name]=sha(v)
 out=BASE/'native-delayed-reschedule/delayed-stage.o';vp=out.parent/'stage-verification.json';vp.unlink(missing_ok=True);subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(out)],check=True)
 before=set(undefined_symbols(board_obj)[0]);after=set(undefined_symbols(out)[0]);anchors={'r1_delayed_context':0x20006718,'r1_delayed_callbacks':0x20015104,'r1_delayed_arguments':0x20015204,'r1_delayed_deadlines':0x20015304};assert not after-before,after-before
 for n in ('r1_native_delayed_schedule','r1_native_delayed_push','r1_native_delayed_reschedule','osTimerStart','osTimerStop','xTimerIsTimerActive'):assert n in undefined_symbols(out)[1]
 result=dict(driver_sha256=sha(Path(__file__)),board_report_sha256=sha(rp),board_object_sha256=sha(board_obj),provider_reports=reports,provider_receipts=receipts,objects={str(p.relative_to(ROOT)):sha(p) for p in objects},selected_object_sha256=sha(out),resolved_board_symbols=sorted(before-after),new_unresolved_symbols=sorted(after-before),unresolved_state_anchors={},source_owned_state_anchors=anchors,application_linked=False,canonical_board_integrated=all(included),graph_verified=False,instruction_identity=False,limitations=['Authenticated source storage resolves the four anchors; runtime factory initialization remains a separate gate','Product and timer-control bodies are real C; this link inserts no fixture providers','Native graph verification and canonical board admission remain separate gates']);vp.write_text(json.dumps(result,indent=2)+'\n');print('Delayed product stage resolves',result['resolved_board_symbols'],'; unresolved state anchors:',result['new_unresolved_symbols'])
if __name__=='__main__':main()
