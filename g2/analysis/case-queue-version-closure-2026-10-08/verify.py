from pathlib import Path
import struct,json,itertools,hashlib,sys
D=Path(__file__).resolve().parent;s=D.parent/'case-deferred-event-closure-2026-10-08/verify.py';text=s.read_text().split('# Direct copy helper:')[0];ns={'__file__':str(s)};exec(text,ns);rows=[]
for length,count,lock,mask,tasks in itertools.product([1,2],[0,1],[-1,0,1,5,126],[0,1],[0,1,3]):
 vals=[]
 for entry in [0x0800c7a8,ns['symbols']['case_public_queue_v1043'],ns['symbols']['case_public_queue_v1051']]:
  u=ns['fixture'](length,count,0,16,lock,mask);u.mem_write(0x20000130,struct.pack('<I',tasks));vals.append(ns['execute'](u,entry,[ns['Q'],ns['ITEM'],ns['YIELD'],0],mask,True))
 assert vals[0][:2]==vals[1][:2]
 different=count<length and lock>=0 and lock>=tasks
 assert (vals[2][:2]!=vals[0][:2])==different
 rows.append(dict(length=length,count=count,tx_lock=lock,primask=mask,task_count_fixture=tasks,v1043_matches=True,v1051_differs=different))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,v1051_differences=sum(r['v1051_differs'] for r in rows),firmware_sha256=hashlib.sha256(ns['ns']['blob']).hexdigest(),elf_sha256=hashlib.sha256(ns['ns']['elf'].read_bytes()).hexdigest(),limits=['Original full normal back-send path versus selected full public V10.4.3/V10.5.1 function bodies under explicit fixture ABI/configuration.','Real original copy and interrupt-mask peers; empty receive wait list, allocated coherent queues, no scheduler state/task-wake execution.','Public V10.5.1 task-count accessor is explicit compiled SRAM fixture read, not bound original function; configured counts are synthetic.']),indent=2)+'\n');print('PASS',len(rows),'V10.4.3 comparisons;',sum(r['v1051_differs'] for r in rows),'V10.5.1 differences')
