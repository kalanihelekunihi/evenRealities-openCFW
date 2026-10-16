#!/usr/bin/env python3
"""Select pinned mutex/semaphore bodies while sharing existing queue providers."""
import hashlib,json,re,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
FUNCTIONS=('prvInitialiseMutex','xQueueCreateMutex','xQueueCreateMutexStatic','xQueueTakeMutexRecursive','xQueueGiveMutexRecursive','xQueueSemaphoreTake','xQueueGiveFromISR','prvGetDisinheritPriorityAfterTimeout','prvUnlockQueue','prvIsQueueEmpty')
MACROS=('queueUNLOCKED','queueLOCKED_UNMODIFIED','queueINT8_MAX','uxQueueType','queueQUEUE_IS_MUTEX','prvLockQueue','prvIncrementQueueTxLock')
def main():
 out=BASE/'rtos-mutex-kernel';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);original=json.loads((BASE/'rtos/report.json').read_text());row=next(x for x in original['units'] if x['source'].endswith('/queue.c'));up=ROOT/row['source'];assert sha(up)==row['source_sha256'];raw=up.read_bytes();text=raw.decode();clean=re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"',lambda m:' '*len(m.group()),text,flags=re.S);parts=[];slices=[]
 def add(name,start,end):
  part=text[start:end];parts.append(part);slices.append(dict(name=name,start=start,end=end,sha256=hashlib.sha256(part.encode()).hexdigest()))
 for name in MACROS:
  m=re.search(r'^#define '+name+r'[^\n]*\n',text,re.M);assert m,name;end=m.end()
  while text[m.start():end].rstrip().endswith('\\'):end=text.index('\n',end)+1
  add(name,m.start(),end)
 start=text.index('typedef struct QueuePointers');end=text.index('typedef xQUEUE Queue_t;',start)+len('typedef xQUEUE Queue_t;');add('queue_native_types_and_mutex_macros',start,end)
 for name in FUNCTIONS:
  m=re.search(r'^[ \t]*(?:static )?(?:void|QueueHandle_t|BaseType_t|UBaseType_t) '+name+r'\s*\([^;{]*\)\s*\{',text,re.M);assert m,name;end=m.end();depth=1
  while depth:depth+=(clean[end]=='{')-(clean[end]=='}');end+=1
  add(name,m.start(),end)
 license=raw[:raw.index(b'*/')+2];extra='\n_Static_assert(sizeof(Queue_t)==80 && offsetof(Queue_t,u.xSemaphore.xMutexHolder)==8 && offsetof(Queue_t,u.xSemaphore.uxRecursiveCallCount)==12 && offsetof(Queue_t,uxMessagesWaiting)==56,"native mutex queue layout");\n';source=out/'mutex-kernel.c';source.write_bytes(license+b'\n#include "mutex_kernel_contract.h"\n'+b'\n'.join(p.encode() for p in parts)+extra.encode());obj=out/'mutex-kernel.o';dep=out/'mutex-kernel.d';cmd=['clang',*row['command'][1:row['command'].index('-c')],'-fshort-enums','-fno-delete-null-pointer-checks','-fno-inline','-include',str(ROOT/'r1/source-config/rtos/native_port_assert.h'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True);inputs={}
 for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  q=Path(p);inputs[str(q.relative_to(ROOT)) if q.is_relative_to(ROOT) else p]=sha(q)
 result=dict(units=[dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),defined=undefined_symbols(obj)[1],undefined=undefined_symbols(obj)[0])],inputs=inputs,upstream_source=row['source'],upstream_sha256=sha(up),source_slices=slices,license_bytes=len(license),license_sha256=hashlib.sha256(license).hexdigest(),generated_suffix=extra,rtos_report_sha256=sha(BASE/'rtos/report.json'),selected_object_sha256=sha(obj),remaining_symbols=undefined_symbols(obj)[0],scope='Unchanged pinned native80-byte mutex creation/recursive take-give/semaphore take/ISR give; private wait helpers selected, existing public queue create/send providers shared',limitations=['Kernel task ownership/inheritance/timeout and combined synchronization graph remain separate provider/admission gates. No instruction identity or hardware proof.']);(out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print('Mutex/semaphore bodies compiled; remaining:',result['remaining_symbols'])
if __name__=='__main__':main()
