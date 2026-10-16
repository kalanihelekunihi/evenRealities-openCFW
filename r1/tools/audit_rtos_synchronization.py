#!/usr/bin/env python3
"""Require pinned synchronization source reconstruction, native receipts and canonical graph."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
WRAPPERS=['IRQ_Context','osMutexNew','osMutexAcquire','osMutexRelease','osSemaphoreAcquire','osSemaphoreRelease','osSemaphoreGetCount']
KERNEL_MACROS=['queueUNLOCKED','queueLOCKED_UNMODIFIED','queueINT8_MAX','uxQueueType','queueQUEUE_IS_MUTEX','prvLockQueue','prvIncrementQueueTxLock']
KERNEL_FUNCTIONS=['prvInitialiseMutex','xQueueCreateMutex','xQueueCreateMutexStatic','xQueueTakeMutexRecursive','xQueueGiveMutexRecursive','xQueueSemaphoreTake','xQueueGiveFromISR','prvGetDisinheritPriorityAfterTimeout','prvUnlockQueue','prvIsQueueEmpty']
TASK_FUNCTIONS=['pvTaskIncrementMutexHeldCount','xTaskPriorityInherit','vTaskPriorityDisinheritAfterTimeout']
TASK_MACROS=['taskRECORD_READY_PRIORITY','prvAddTaskToReadyList','portRESET_READY_PRIORITY','taskEVENT_LIST_ITEM_VALUE_IN_USE']
def audit():
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';app_hash=sha(app);assert app_hash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';baseline=json.loads((BASE/'rtos/report.json').read_text());originals={u['source']:u['source_sha256'] for u in baseline['units']};board=json.loads((BASE/'board/report.json').read_text());tests={}
 for name,objname,count,entries in [('rtos-synchronization','synchronization.o',18192,{0x7d488,0x7d4d6,0x7d536,0x7d57c,0x7d5e8,0x7d698}),('rtos-mutex-kernel','mutex-kernel.o',5562,{0x8507c,0x97ade,0x97af4,0x97e6c,0x97f14,0x98120,0x98284}),('rtos-mutex-tasks','mutex-tasks.o',5162,{0x85684,0x9626c,0x989ac})]:
  folder=BASE/name;rp=folder/'report.json';r=json.loads(rp.read_text());obj=folder/objname;assert sha(obj)==r['selected_object_sha256']==board['objects'][str(obj.relative_to(ROOT))] and board['input_reports'][name+'/report.json']==sha(rp) and r['rtos_report_sha256']==sha(BASE/'rtos/report.json')
  for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
  for u in r['units']:assert sha(ROOT/u['source'])==u['source_sha256'] and sha(Path(u['command'][u['command'].index('-o')+1]))==u['object_sha256']
  v=json.loads((folder/'verification.json').read_text());tests[name]=v;assert v['application_sha256']==app_hash and v['report_sha256']==sha(rp) and v['driver_sha256']==sha(ROOT/'r1/tools'/('verify_'+name.replace('-','_')+'.py')) and v['comparisons']==count
  raw=(ROOT/r['upstream_source']).read_bytes();assert hashlib.sha256(raw).hexdigest()==r['upstream_sha256']==originals[r['upstream_source']];text=raw.decode();license=raw[:raw.index(b'*/')+2];assert len(license)==r['license_bytes'] and hashlib.sha256(license).hexdigest()==r['license_sha256'];parts={}
  for row in r['source_slices']:
   part=text[row['start']:row['end']];assert hashlib.sha256(part.encode()).hexdigest()==row['sha256'] and row['name'] not in parts;parts[row['name']]=part
  if name=='rtos-synchronization':
   assert list(parts)==WRAPPERS+['IS_IRQ_MASKED','IS_IRQ_MODE'];order=['IS_IRQ_MODE','IS_IRQ_MASKED',*WRAPPERS];header='synchronization_contract.h';extra=''
  elif name=='rtos-mutex-kernel':
   assert list(parts)==KERNEL_MACROS+['queue_native_types_and_mutex_macros']+KERNEL_FUNCTIONS;order=list(parts);header='mutex_kernel_contract.h';extra='\n_Static_assert(sizeof(Queue_t)==80 && offsetof(Queue_t,u.xSemaphore.xMutexHolder)==8 && offsetof(Queue_t,u.xSemaphore.uxRecursiveCallCount)==12 && offsetof(Queue_t,uxMessagesWaiting)==56,"native mutex queue layout");\n';assert r['generated_suffix']==extra
  else:
   assert list(parts)==TASK_FUNCTIONS+TASK_MACROS;order=[*reversed(TASK_MACROS),*TASK_FUNCTIONS];header='mutex_tasks_contract.h';extra='';assert r['list_unit']['object_sha256']==sha(folder/'list.o')
  generated=license+('\n#include "'+header+'"\n').encode()+b'\n'.join(parts[n].encode() for n in order)+extra.encode();assert (ROOT/r['units'][0]['source']).read_bytes()==generated,name
  ep=folder/'evidence.json';e=json.loads(ep.read_text());assert e['application_sha256']==app_hash and e['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and e['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c');inventory=ROOT/e['rea_inventory'];assert sha(inventory)==e['rea_inventory_sha256'];assert e['rea_registered_rows']==[row for row in json.loads(inventory.read_text())['normalized_result'] if int(row['address'],16) in entries]
  for span in e['spans']:
   p=folder/span['ghidra_file'];a=int(span['entry'],16);assert sha(p)==span['ghidra_sha256'] and bytes(json.loads(p.read_text())['data'])==app.read_bytes()[a-0x27000:a-0x27000+span['bytes']]
 assert tests['rtos-mutex-kernel']['assertion_comparisons']==2444 and tests['rtos-mutex-tasks']['assertion_comparisons']==1024
 assert tests['rtos-synchronization']['comparisons_by_function']=={'osMutexAcquire':2592,'osMutexNew':10416,'osMutexRelease':864,'osSemaphoreAcquire':2592,'osSemaphoreGetCount':864,'osSemaphoreRelease':864}
 assert tests['rtos-mutex-kernel']['comparisons_by_function']=={'prvInitialiseMutex':2,'xQueueCreateMutex':16,'xQueueCreateMutexStatic':16,'xQueueGiveFromISR':3073,'xQueueGiveMutexRecursive':361,'xQueueSemaphoreTake':1733,'xQueueTakeMutexRecursive':361}
 for name,row in tests['rtos-mutex-kernel']['actual_providers'].items():assert row['report_sha256']==sha(BASE/name/'report.json') and row['object_sha256']==json.loads((BASE/name/'report.json').read_text())['selected_object_sha256']
 stage=json.loads((BASE/'rtos-synchronization/stage-verification.json').read_text());assert stage['driver_sha256']==sha(ROOT/'r1/tools/check_rtos_synchronization_stage.py') and stage['board_report_sha256']==sha(BASE/'board/report.json') and stage['board_object_sha256']==sha(BASE/'board/native-board.o') and stage['canonical_board_includes_synchronization_objects'] and not stage['compiled_unverified_modules'] and not stage['new_unresolved_symbols'] and stage['comparisons']==28916 and stage['selected_object_sha256']==sha(BASE/'rtos-synchronization/synchronization-stage.o')
 for group in ('provider_reports','isolated_receipts','evidence'):
  for p,d in stage[group].items():assert sha(BASE/p)==d,p
 g=json.loads((BASE/'board/synchronization-verification.json').read_text());assert g['application_sha256']==app_hash and g['board_report_sha256']==sha(BASE/'board/report.json') and g['verification_driver_sha256']==sha(ROOT/'r1/tools/verify_native_board.py') and g['synchronization_driver_sha256']==sha(ROOT/'r1/tools/verify_synchronization_graph.py') and g['comparisons']==1344 and g['workflows']==64 and g['inheritance_lifetimes_per_implementation']==64 and g['semaphore_operations_per_implementation']==320 and not g['provider_interception']
 for name,d in g['provider_reports'].items():assert sha(BASE/name/'report.json')==d,name
if __name__=='__main__':audit();print('Synchronization source/native/canonical graph audit passed')
