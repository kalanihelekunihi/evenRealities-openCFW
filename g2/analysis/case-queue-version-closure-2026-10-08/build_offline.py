from pathlib import Path
import argparse,subprocess,re,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--gcc',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();D=Path(__file__).resolve().parent;root=D.parents[2];a.output.mkdir(parents=True,exist_ok=True);c=root/'g2/components/case/deferred_event_offline';paths=[];receipts=[]
prefix='''#include "deferred.h"
#include <stddef.h>
typedef int32_t BaseType_t;
typedef uint32_t UBaseType_t;
typedef case_queue Queue_t;
typedef case_queue *QueueHandle_t;
#define uxItemSize item_size
#define uxMessagesWaiting messages
#define uxLength length
#define cTxLock tx_lock
#define xTasksWaitingToReceive receive_wait
#define queueOVERWRITE 2
#define queueUNLOCKED (-1)
#define queueINT8_MAX ((int8_t)127)
#define configUSE_QUEUE_SETS 0
#define pdFALSE 0
#define pdTRUE 1
#define pdPASS 1
#define errQUEUE_FULL 0
#define listLIST_IS_EMPTY(l) ((l)->count==0)
#define configASSERT(x) do{if(!(x)){__asm volatile("cpsid i");for(;;){}}}while(0)
#define portASSERT_IF_INTERRUPT_PRIORITY_INVALID() ((void)0)
#define portSET_INTERRUPT_MASK_FROM_ISR() case_mask_save()
#define portCLEAR_INTERRUPT_MASK_FROM_ISR(s) case_mask_restore(s)
#define traceQUEUE_SEND_FROM_ISR(q) ((void)0)
#define traceQUEUE_SEND_FROM_ISR_FAILED(q) ((void)0)
#define mtCOVERAGE_TEST_MARKER() ((void)0)
uint32_t case_mask_save(void);
void case_mask_restore(uint32_t);
int32_t prvCopyDataToQueue(Queue_t *,const void *,int32_t);
int32_t xTaskRemoveFromEventList(case_list *);
/* Explicit public fixture accessor, not a stock function attribution. */
static uint32_t uxTaskGetNumberOfTasks(void){return *(volatile uint32_t *)0x20000130u;}
'''
sources={'v1043':D.parent/'case-event-waiters-closure-2026-10-08/upstream-queue-v1043.c','v1051':D.parent/'case-deferred-event-closure-2026-10-08/upstream-queue.c'}
for name,file in sources.items():
 s=file.read_text();m=re.search(r'BaseType_t xQueueGenericSendFromISR\s*\([^;{]*\)\s*\{',s);i=m.end();depth=1
 while depth:
  if s[i]=='{':depth+=1
  if s[i]=='}':depth-=1
  i+=1
 body=s[m.start():i];macro=''
 if name=='v1051':
  lines=s.splitlines();idx=next(i for i,l in enumerate(lines) if l.startswith('#define prvIncrementQueueTxLock'));macro=lines[idx]+'\n';idx+=1
  while lines[idx-1].rstrip().endswith('\\'):macro+=lines[idx]+'\n';idx+=1
 out=a.output/(name+'.c');out.write_text(prefix+macro+body.replace('xQueueGenericSendFromISR','case_public_queue_'+name,1));paths.append(out);receipts.append(dict(version=name,source=str(file.relative_to(root)),sha256=hashlib.sha256(file.read_bytes()).hexdigest(),body_sha256=hashlib.sha256(body.encode()).hexdigest(),macro=macro))
link=a.output/'link.ld';link.write_text('case_mask_save = 0x080000f5; case_mask_restore = 0x080000fd; prvCopyDataToQueue = 0x0800ad49; xTaskRemoveFromEventList = 0x0800cba1; SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n');elf=a.output/'queue.elf';flags=['-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib'];subprocess.run([str(a.gcc),*flags,'-I',str(c),'-T',str(link),*[str(x) for x in paths],'-o',str(elf)],check=True);h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();(D/'reproduction-receipt.json').write_text(json.dumps(dict(gcc=str(a.gcc),gcc_sha256=h(a.gcc),elf=str(elf),elf_sha256=h(elf),flags=flags,sources=receipts,public_abi_scaffold=prefix,limits=['Full selected public function bodies compile, with explicit ARM32 queue aliases, queue sets disabled, task count fixture accessor.','Real original copy/critical providers are common peers. No unique complete kernel/configuration/compiler attribution.']),indent=2)+'\n');print(elf)
