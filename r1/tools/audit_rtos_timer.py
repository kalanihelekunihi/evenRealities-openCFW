#!/usr/bin/env python3
"""Strict provenance, native-contract and canonical composition admission for timers."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
MODULES={'rtos-timer-runtime':('timer-runtime.o',12349),'rtos-timer-queue':('timer-queue.o',1849),'rtos-timer-task-wait':('task-wait.o',15121),'rtos-timer-api':('timer-api.o',4813),'rtos-timer-isr-queue':('timer-isr-queue.o',27657),'rtos-task-count':('task-count.o',None)}
RUNTIME_FUNCTIONS=['prvInsertTimerInActiveList','prvReloadTimer','prvProcessExpiredTimer','prvSwitchTimerLists','prvSampleTimeNow','prvProcessTimerOrBlockTask','prvGetNextExpireTime','prvProcessReceivedCommands','prvTimerTask']
RUNTIME_MACROS=['tmrNO_DELAY','tmrMAX_TIME_BEFORE_OVERFLOW','tmrSTATUS_IS_ACTIVE','tmrSTATUS_IS_STATICALLY_ALLOCATED','tmrSTATUS_IS_AUTORELOAD']
def audit():
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';app_hash=sha(app);assert app_hash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';board=json.loads((BASE/'board/report.json').read_text());reports={};tests={};baseline=json.loads((BASE/'rtos/report.json').read_text());assert baseline['pins']['third-party/upstream/freertos-kernel']=='def7d2df2b0506d3d249334974f51e427c17a41c';originals={u['source']:u['source_sha256'] for u in baseline['units']}
 for name,(object_name,count) in MODULES.items():
  folder=BASE/name;rp=folder/'report.json';r=json.loads(rp.read_text());reports[name]=r;obj=folder/object_name;assert sha(obj)==r['selected_object_sha256']==board['objects'][str(obj.relative_to(ROOT))] and board['input_reports'][name+'/report.json']==sha(rp)
  assert r['rtos_report_sha256']==sha(BASE/'rtos/report.json')
  for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
  for unit in r['units']:
   assert sha(ROOT/unit['source'])==unit['source_sha256'];assert sha(Path(unit['command'][unit['command'].index('-o')+1]))==unit['object_sha256'];assert unit['compiled']
  if count is not None:
   vp=folder/'verification.json';v=json.loads(vp.read_text());tests[name]=v;assert v['report_sha256']==sha(rp) and v['driver_sha256']==sha(ROOT/'r1/tools'/('verify_'+name.replace('-','_')+'.py')) and v['application_sha256']==app_hash and v['comparisons']==count
  if 'source_slices' not in r:
   assert r['units'][0]['source']=='third-party/upstream/freertos-kernel/queue.c' and r['units'][0]['source_sha256']==originals[r['units'][0]['source']];continue
  raw=(ROOT/r['upstream_source']).read_bytes();assert hashlib.sha256(raw).hexdigest()==r['upstream_sha256']==originals[r['upstream_source']];text=raw.decode();parts={}
  license=raw[:raw.index(b'*/')+2];assert len(license)==r['license_bytes'] and hashlib.sha256(license).hexdigest()==r['license_sha256']
  for row in r['source_slices']:
   part=text[row['start']:row['end']];assert hashlib.sha256(part.encode()).hexdigest()==row['sha256'];assert row['name'] not in parts;parts[row['name']]=part
  if name=='rtos-timer-runtime':
   expected=['timer_runtime_types',*RUNTIME_FUNCTIONS,*RUNTIME_MACROS];assert list(parts)==expected;order=[*reversed(RUNTIME_MACROS),'timer_runtime_types',*RUNTIME_FUNCTIONS];header='timer_runtime_contract.h'
   signatures={'prvTimerTask':'void {alias}(void *)','prvInsertTimerInActiveList':'BaseType_t {alias}(Timer_t *,TickType_t,TickType_t,TickType_t)','prvReloadTimer':'void {alias}(Timer_t *,TickType_t,TickType_t)','prvProcessExpiredTimer':'void {alias}(TickType_t,TickType_t)','prvSwitchTimerLists':'void {alias}(void)','prvSampleTimeNow':'TickType_t {alias}(BaseType_t *)','prvProcessTimerOrBlockTask':'void {alias}(TickType_t,BaseType_t)','prvGetNextExpireTime':'TickType_t {alias}(BaseType_t *)','prvProcessReceivedCommands':'void {alias}(void)'}
   aliases={n:('r1_native_timer_task' if n=='prvTimerTask' else 'r1_timer_runtime_'+n[3:]) for n in RUNTIME_FUNCTIONS};assert r['aliases']==aliases
   extra='\n'+''.join(signatures[n].format(alias=a)+' __attribute__((alias("'+n+'")));\n' for n,a in aliases.items())+'_Static_assert(sizeof(Timer_t)==44 && offsetof(Timer_t,xTimerPeriodInTicks)==24 && offsetof(Timer_t,pxCallbackFunction)==32 && offsetof(Timer_t,ucStatus)==40 && sizeof(DaemonTaskMessage_t)==16,"native timer runtime layout");\n';assert r['generated_suffix']==extra
   assert r['startup_report_sha256']==sha(BASE/'rtos-scheduler-start/report.json')
  elif name=='rtos-timer-api':
   order=['timer_runtime_types','tmrNO_DELAY','tmrSTATUS_IS_ACTIVE','tmrSTATUS_IS_STATICALLY_ALLOCATED','tmrSTATUS_IS_AUTORELOAD','prvInitialiseNewTimer','xTimerCreate','xTimerCreateStatic','xTimerGenericCommand'];assert list(parts)==order;header='timer_api_contract.h'
   extra='\nvoid r1_timer_initialise_new(const char *,TickType_t,BaseType_t,void *,TimerCallbackFunction_t,Timer_t *) __attribute__((alias("prvInitialiseNewTimer")));\n_Static_assert(sizeof(Timer_t)==44 && sizeof(StaticTimer_t)==44 && sizeof(DaemonTaskMessage_t)==16 && offsetof(Timer_t,ucStatus)==40,"native timer API layout");\n';assert r['generated_suffix']==extra
  elif name=='rtos-timer-task-wait':
   assert list(parts)==['vTaskPlaceOnEventListRestricted','prvAddCurrentTaskToDelayedList','taskRECORD_READY_PRIORITY','prvAddTaskToReadyList','portRESET_READY_PRIORITY'];order=['portRESET_READY_PRIORITY','prvAddTaskToReadyList','taskRECORD_READY_PRIORITY','vTaskPlaceOnEventListRestricted','prvAddCurrentTaskToDelayedList'];header='timer_task_wait_contract.h';extra=''
  else:
   assert name=='rtos-task-count' and list(parts)==['uxTaskGetNumberOfTasks'];prefix='\n#include "FreeRTOS.h"\n#include "task.h"\nextern volatile UBaseType_t uxCurrentNumberOfTasks;\n';assert r['generated_prefix']==prefix;assert (ROOT/r['units'][0]['source']).read_bytes()==license+prefix.encode()+parts['uxTaskGetNumberOfTasks'].encode();continue
  generated=license+('\n#include "'+header+'"\n').encode()+b'\n'.join(parts[n].encode() for n in order)+extra.encode();assert (ROOT/r['units'][0]['source']).read_bytes()==generated,name
 # Every lower fixture/actual-provider receipt is bound to its present object/report.
 for name in ('rtos-timer-runtime','rtos-timer-api'):
  assert tests[name]['list_report_sha256']==sha(BASE/'rtos-task-wait/report.json')
  key='list_input_object_sha256' if name=='rtos-timer-runtime' else 'list_object_sha256';assert tests[name][key]==sha(BASE/'rtos-task-wait/list.o')
 for name in ('rtos-timer-queue','rtos-timer-isr-queue'):
  v=tests[name];assert v['memory_report_sha256']==sha(BASE/'runtime/report.json') and v['memory_object_sha256']==sha(BASE/'runtime/memory-runtime.o')
  for p,d in {**v['memory_provider_reports'],**v['memory_provider_objects']}.items():assert sha(BASE/p)==d,p
 iv=tests['rtos-timer-isr-queue'];assert iv['task_count_report_sha256']==sha(BASE/'rtos-task-count/report.json') and iv['task_count_object_sha256']==sha(BASE/'rtos-task-count/task-count.o');assert iv['priority_report_sha256']==sha(BASE/'rtos-interrupt-priority/report.json') and iv['priority_object_sha256']==sha(BASE/'rtos-interrupt-priority/interrupt-priority.o')
 assert tests['rtos-timer-runtime']['fault_comparisons']==217 and tests['rtos-timer-api']['assertion_comparisons']==853 and iv['assertion_comparisons']==8450 and tests['rtos-timer-queue']['assertion_comparisons']==362 and tests['rtos-timer-task-wait']['assertion_comparisons']==1
 allowed={'rtos-timer-runtime':{0x851f4,0x852a0,0x852e0,0x853d4,0x85440,0x85484,0x85510,0x95f8e,0x961b8,0x97f50},'rtos-timer-api':{0x8515a,0x98c48,0x98c7c,0x98d04},'rtos-timer-isr-queue':{0x97da4},'rtos-task-count':{0x9566c}}
 evidence={}
 for name,entries in allowed.items():
  ep=BASE/name/'evidence.json';e=json.loads(ep.read_text());evidence[name]=e;assert e['application_sha256']==app_hash and e['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and e['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c');inventory=ROOT/e['rea_inventory'];assert sha(inventory)==e['rea_inventory_sha256'];rows=json.loads(inventory.read_text())['normalized_result'];assert e['rea_registered_rows']==[r for r in rows if int(r['address'],16) in entries]
  for span in e['spans']:
   p=ep.parent/span['ghidra_file'];a=int(span['entry'],16);assert sha(p)==span['ghidra_sha256'] and bytes(json.loads(p.read_text())['data'])==app.read_bytes()[a-0x27000:a-0x27000+span['bytes']]
 bv=json.loads((BASE/'board/verification.json').read_text());assert bv['timer_sample_state_initial_zero_bytes_compared']==4
 g=json.loads((BASE/'rtos-timer-runtime/graph-verification.json').read_text());stage=json.loads((BASE/'rtos-timer-runtime/stage-verification.json').read_text());assert stage['driver_sha256']==sha(ROOT/'r1/tools/check_rtos_timer_stage.py') and stage['board_report_sha256']==sha(BASE/'board/report.json') and stage['board_object_sha256']==sha(BASE/'board/native-board.o') and stage['canonical_board_includes_timer_objects'] and not stage['new_unresolved_symbols']
 assert g['application_sha256']==app_hash and g['stage_receipt_sha256']==sha(BASE/'rtos-timer-runtime/stage-verification.json') and g['stage_object_sha256']==stage['selected_object_sha256']==sha(BASE/'rtos-timer-runtime/timer-stage.o') and g['driver_sha256']==sha(ROOT/'r1/tools/verify_timer_runtime_graph.py') and g['comparisons']==480 and g['workflows']==96 and g['timer_task_loop_iterations_per_implementation']==96 and not g['provider_interception']
 assert g['api_report_sha256']==sha(BASE/'rtos-timer-api/report.json') and g['api_object_sha256']==sha(BASE/'rtos-timer-api/timer-api.o') and g['api_receipt_sha256']==sha(BASE/'rtos-timer-api/verification.json')
 assert g['executed_provider_entry_counts']['native']==g['executed_provider_entry_counts']['source']=={'uxTaskGetNumberOfTasks':96,'xQueueReceive':576,'vTaskSuspendAll':288,'vQueueWaitForMessageRestricted':192,'vTaskPlaceOnEventListRestricted':96,'xTaskResumeAll':288,'xQueueGenericSendFromISR':96,'vPortValidateInterruptPriority':96,'pvPortMalloc':48,'vPortFree':48}
 for name,row in g['extra_provider_reports'].items():
  assert row['report_sha256']==sha(BASE/name/'report.json') and row['object_sha256']==json.loads((BASE/name/'report.json').read_text())['selected_object_sha256']
  if 'receipt_sha256' in row:assert row['receipt_sha256']==sha(BASE/name/'verification.json')
 return evidence['rtos-timer-runtime']['ownership_correction']
if __name__=='__main__':audit();print('Timer source/native/canonical composition audit passed')
