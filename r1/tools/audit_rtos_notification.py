#!/usr/bin/env python3
"""Strict pinned-source/native/composed admission for notifications, delay and events."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
WRAPPERS=['IRQ_Context','osThreadFlagsSet','osThreadFlagsWait','osEventFlagsSet','osDelay']
WRAPPER_MACROS=['IS_IRQ_MASKED','IS_IRQ_MODE','MAX_BITS_TASK_NOTIFY','MAX_BITS_EVENT_GROUPS','THREAD_FLAGS_INVALID_BITS','EVENT_FLAGS_INVALID_BITS']
TASKS=['xTaskGenericNotify','xTaskGenericNotifyFromISR','xTaskGenericNotifyWait','vTaskDelay','prvAddCurrentTaskToDelayedList','prvResetNextTaskUnblockTime']
TASK_MACROS=['taskRECORD_READY_PRIORITY','prvAddTaskToReadyList','portRESET_READY_PRIORITY','taskNOT_WAITING_NOTIFICATION','taskWAITING_NOTIFICATION','taskNOTIFICATION_RECEIVED','taskYIELD_IF_USING_PREEMPTION']
UNORDERED=['vTaskRemoveFromUnorderedEventList','prvResetNextTaskUnblockTime']
UNORDERED_MACROS=['taskRECORD_READY_PRIORITY','prvAddTaskToReadyList','portRESET_READY_PRIORITY','taskEVENT_LIST_ITEM_VALUE_IN_USE']
def audit():
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';app_hash=sha(app);assert app_hash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';baseline=json.loads((BASE/'rtos/report.json').read_text());originals={u['source']:u['source_sha256'] for u in baseline['units']};board=json.loads((BASE/'board/report.json').read_text());tests={};evidence={}
 for name,file,count,entries in [('rtos-notification-wrappers','notification-wrappers.o',25128,{0x7d154,0x7d1a0,0x7d6f4,0x7d780}),('rtos-notification-tasks','notification-tasks.o',14840,{0x95fd4,0x98484,0x985ac,0x98700}),('rtos-event-groups','event-groups.o',4568,{0x977de,0x977f4,0x9787c,0x95c8c,0x9779c}),('rtos-timer-pend','timer-pend.o',4568,{0x98d98}),('rtos-unordered-event','unordered-event.o',7290,{0x963e8})]:
  folder=BASE/name;rp=folder/'report.json';r=json.loads(rp.read_text());obj=folder/file;assert sha(obj)==r['selected_object_sha256']==board['objects'][str(obj.relative_to(ROOT))] and board['input_reports'][name+'/report.json']==sha(rp) and r['rtos_report_sha256']==sha(BASE/'rtos/report.json')
  for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
  for unit in r['units']:assert sha(ROOT/unit['source'])==unit['source_sha256'] and sha(Path(unit['command'][unit['command'].index('-o')+1]))==unit['object_sha256']
  vp=BASE/'rtos-event-groups/verification.json' if name=='rtos-timer-pend' else folder/'verification.json';v=json.loads(vp.read_text());tests[name]=v;assert v['application_sha256']==app_hash and v['comparisons']==count
  if name in ('rtos-event-groups','rtos-timer-pend'):assert v['provider_reports'][name+'/report.json']==sha(rp) and v['driver_sha256']==sha(ROOT/'r1/tools/verify_rtos_event_groups.py')
  else:assert v['report_sha256']==sha(rp) and v['driver_sha256']==sha(ROOT/'r1/tools'/('verify_'+name.replace('-','_')+'.py'))
  if name=='rtos-event-groups':assert r['units'][0]['source']=='third-party/upstream/freertos-kernel/event_groups.c' and r['units'][0]['source_sha256']==originals[r['units'][0]['source']]
  else:
   raw=(ROOT/r['upstream_source']).read_bytes();assert hashlib.sha256(raw).hexdigest()==r['upstream_sha256']==originals[r['upstream_source']];text=raw.decode();license=raw[:raw.index(b'*/')+2];assert len(license)==r['license_bytes'] and hashlib.sha256(license).hexdigest()==r['license_sha256'];parts={}
   for row in r['source_slices']:
    part=text[row['start']:row['end']];assert hashlib.sha256(part.encode()).hexdigest()==row['sha256'] and row['name'] not in parts;parts[row['name']]=part
   extra=''
   if name=='rtos-notification-wrappers':assert list(parts)==WRAPPERS+WRAPPER_MACROS;order=[*reversed(WRAPPER_MACROS),*WRAPPERS];header='notification_wrapper_contract.h'
   elif name=='rtos-notification-tasks':assert list(parts)==TASKS+TASK_MACROS;order=[*reversed(TASK_MACROS),*TASKS];header='notification_task_contract.h';assert r['list_unit']['object_sha256']==sha(folder/'list.o')
   elif name=='rtos-unordered-event':assert list(parts)==UNORDERED+UNORDERED_MACROS;order=[*reversed(UNORDERED_MACROS),*UNORDERED];header='unordered_event_contract.h';assert r['list_unit']['object_sha256']==sha(folder/'list.o')
   else:
    assert name=='rtos-timer-pend';order=['timer_runtime_types','tmrNO_DELAY','tmrSTATUS_IS_ACTIVE','tmrSTATUS_IS_STATICALLY_ALLOCATED','tmrSTATUS_IS_AUTORELOAD','xTimerPendFunctionCallFromISR'];assert list(parts)==order;header='timer_pend_contract.h';extra='\n_Static_assert(sizeof(DaemonTaskMessage_t)==16,"native pended callback message");\n';assert r['generated_suffix']==extra
   assert (ROOT/r['units'][0]['source']).read_bytes()==license+('\n#include "'+header+'"\n').encode()+b'\n'.join(parts[n].encode() for n in order)+extra.encode(),name
  ep=folder/'evidence.json';e=json.loads(ep.read_text());evidence[name]=e;assert e['application_sha256']==app_hash and e['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and e['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c');inventory=ROOT/e['rea_inventory'];assert sha(inventory)==e['rea_inventory_sha256'];assert e['rea_registered_rows']==[row for row in json.loads(inventory.read_text())['normalized_result'] if int(row['address'],16) in entries]
  for span in e['spans']:
   p=folder/span['ghidra_file'];a=int(span['entry'],16);assert sha(p)==span['ghidra_sha256'] and bytes(json.loads(p.read_text())['data'])==app.read_bytes()[a-0x27000:a-0x27000+span['bytes']]
 assert tests['rtos-notification-tasks']['assertion_comparisons']==4830 and tests['rtos-unordered-event']['assertion_comparisons']==4860 and tests['rtos-event-groups']['fault_comparisons']==917
 assert tests['rtos-notification-wrappers']['comparisons_by_function']=={'osDelay':120,'osEventFlagsSet':10368,'osThreadFlagsSet':10368,'osThreadFlagsWait':4272}
 assert tests['rtos-notification-tasks']['comparisons_by_function']=={'xTaskGenericNotify':6052,'xTaskGenericNotifyFromISR':6052,'xTaskGenericNotifyWait':2592,'vTaskDelay':144}
 assert tests['rtos-event-groups']['comparisons_by_function']=={'xEventGroupSetBits':1801,'xEventGroupGetBitsFromISR':30,'xEventGroupSetBitsFromISR':288,'vEventGroupSetBitsCallback':1801,'xTimerPendFunctionCallFromISR':648}
 assert tests['rtos-notification-tasks']['priority_report_sha256']==sha(BASE/'rtos-interrupt-priority/report.json') and tests['rtos-notification-tasks']['priority_object_sha256']==sha(BASE/'rtos-interrupt-priority/interrupt-priority.o')
 stage_path=BASE/'rtos-notification-wrappers/stage-verification.json';stage=json.loads(stage_path.read_text());assert stage['driver_sha256']==sha(ROOT/'r1/tools/check_rtos_notification_stage.py') and stage['board_report_sha256']==sha(BASE/'board/report.json') and stage['board_object_sha256']==sha(BASE/'board/native-board.o') and stage['canonical_board_includes_notification_objects'] and stage['selected_object_sha256']==sha(BASE/'rtos-notification-wrappers/notification-stage.o') and stage['comparisons']==51826 and not stage['new_unresolved_symbols']
 for group in ('provider_reports','isolated_receipts','evidence'):
  for p,d in stage[group].items():assert sha(BASE/p)==d,p
 npath=BASE/'rtos-notification-wrappers/event-next-target.json';n=json.loads(npath.read_text());assert stage['event_next_target_sha256']==sha(npath);body=npath.parent/n['rea_body'];pseudo=npath.parent/n['rea_pseudocode'];assert sha(body)==n['rea_body_sha256'] and sha(pseudo)==n['rea_pseudocode_sha256'];info=json.loads(body.read_text());assert info['subject']['digest']['sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and info['normalized_result']['body']['ranges']==[{'start':'0x9787c','end':'0x97887'},{'start':'0x98d98','end':'0x98db9'}] and info['normalized_result']['body']['total_bytes']==46 and info['normalized_result']['body']['non_contiguous']
 for span in n['spans']:
  p=npath.parent/span['ghidra_file'];a=int(span['entry'],16);assert sha(p)==span['ghidra_sha256'] and bytes(json.loads(p.read_text())['data'])==app.read_bytes()[a-0x27000:a-0x27000+span['bytes']]
 g=json.loads((BASE/'board/notification-verification.json').read_text());assert g['application_sha256']==app_hash and g['board_report_sha256']==sha(BASE/'board/report.json') and g['verification_driver_sha256']==sha(ROOT/'r1/tools/verify_native_board.py') and g['notification_driver_sha256']==sha(ROOT/'r1/tools/verify_notification_graph.py') and g['comparisons']==672 and g['workflows']==64 and g['notification_wakes_per_implementation']==g['event_wakes_per_implementation']==g['daemon_iterations_per_implementation']==64 and not g['provider_interception']
 for name,d in g['provider_reports'].items():assert sha(BASE/name/'report.json')==d,name
 expected={'vTaskDelay':128,'xTaskGenericNotify':64,'xTaskGenericNotifyFromISR':64,'xTaskGenericNotifyWait':64,'xEventGroupSetBits':96,'vTaskRemoveFromUnorderedEventList':64,'xTimerPendFunctionCallFromISR':64,'xQueueGenericSendFromISR':64,'vEventGroupSetBitsCallback':64};assert g['executed_provider_entry_counts']['native']==g['executed_provider_entry_counts']['source']==expected
 bv=json.loads((BASE/'board/verification.json').read_text());assert bv['unresolved_test_guard_base']=='0x1100000' and 0xe000<bv['source_text_bytes']<0x40000
 return {'0x00098700':evidence['rtos-notification-tasks']['ownership_mapping'],'0x0009787c':evidence['rtos-event-groups']['ownership_mapping'],'0x000963e8':evidence['rtos-unordered-event']['ownership_mapping']}
if __name__=='__main__':audit();print('Notification/event source/native/canonical graph audit passed')
