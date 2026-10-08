from pathlib import Path
import argparse,subprocess,re,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--gcc',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();D=Path(__file__).resolve().parent;root=D.parents[2];a.output.mkdir(parents=True,exist_ok=True);c=root/'g2/components/case/deferred_event_offline'
def extract(file,pattern):
 s=(D/file).read_text();m=re.search(pattern,s);i=m.end();depth=1
 while depth:
  if s[i]=='{':depth+=1
  if s[i]=='}':depth-=1
  i+=1
 return s[m.start():i]
copy=extract('upstream-queue.c',r'static BaseType_t prvCopyDataToQueue\s*\([^;{]*\)\s*\{');pend=extract('upstream-timers.c',r'BaseType_t xTimerPendFunctionCallFromISR\s*\([^;{]*\)\s*\{')
read=extract('upstream-queue.c',r'static void prvCopyDataFromQueue\s*\([^;{]*\)\s*\{')
read=read.replace('static void prvCopyDataFromQueue','void case_public_read').replace('pxQueue->u.xQueue.pcTail','pxQueue->tail').replace('pxQueue->u.xQueue.pcReadFrom','pxQueue->read')
prefix='''#include "deferred.h"
#include <stddef.h>
typedef int32_t BaseType_t;
typedef uint32_t UBaseType_t;
typedef case_queue Queue_t;
#define pcHead head
#define pcWriteTo write
#define u xUnion
#define uxMessagesWaiting messages
#define uxItemSize item_size
#define uxQueueType head
#define queueQUEUE_IS_MUTEX 0
#define queueSEND_TO_BACK 0
#define queueOVERWRITE 2
#define pdFALSE 0
#define configUSE_MUTEXES 0
#define mtCOVERAGE_TEST_MARKER() ((void)0)
/* Public selected copy body only; mutex branch excluded from comparisons. */
void *memcpy(void *,const void *,size_t);
'''
# Explicit structural field translations preserve selected public algorithms.
copy=copy.replace('static BaseType_t prvCopyDataToQueue','BaseType_t case_public_copy').replace('pxQueue->u.xQueue.pcTail','pxQueue->tail').replace('pxQueue->u.xQueue.pcReadFrom','pxQueue->read')
prefix+='''typedef uint32_t PendedFunction_t;
typedef struct {PendedFunction_t pxCallbackFunction;void *pvParameter1;uint32_t ulParameter2;} Callback;
typedef struct {int32_t xMessageID;union {Callback xCallbackParameters;} u;} DaemonTaskMessage_t;
_Static_assert(sizeof(DaemonTaskMessage_t)==16,"public message ABI");
#define tmrCOMMAND_EXECUTE_CALLBACK_FROM_ISR (-2)
#define xTimerQueue (*(case_queue **)0x20000164u)
int32_t case_original_queue_send(case_queue *,const void *,int32_t *,int32_t);
#define xQueueSendFromISR(q,m,y) case_original_queue_send(q,m,y,0)
#define tracePEND_FUNC_CALL_FROM_ISR(a,b,c,d) ((void)0)
'''
# 'u' macro belongs to no live copy field; remove before public message declaration.
prefix=prefix.replace('#define u xUnion\n','')
public=a.output/'public.c';public.write_text(prefix+copy+'\n'+read+'\n'+pend.replace('xTimerPendFunctionCallFromISR','case_public_pend',1))
link=a.output/'link.ld';link.write_text('case_mask_save = 0x080000f5; case_mask_restore = 0x080000fd; case_remove_waiter = 0x0800cba1; case_disinherit = 0x0800cb39; case_original_queue_send = 0x0800c7a9; memcpy = 0x080001b5; xEventGroupSetBits = 0x0800c4df; SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
elf=a.output/'deferred.elf';flags=['-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib'];subprocess.run([str(a.gcc),*flags,'-I',str(c),'-T',str(link),str(c/'deferred.c'),str(root/'g2/components/case/event_flags_offline/events.c'),str(public),'-o',str(elf)],check=True);h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();(D/'reproduction-receipt.json').write_text(json.dumps(dict(gcc=str(a.gcc),gcc_sha256=h(a.gcc),flags=flags,elf=str(elf),elf_sha256=h(elf),public_pin='def7d2df2b0506d3d249334974f51e427c17a41c',upstream={file:h(D/file) for file in ['upstream-timers.c','upstream-queue.c']},selected_copy_sha256=hashlib.sha256(copy.encode()).hexdigest(),selected_pend_sha256=hashlib.sha256(pend.encode()).hexdigest(),public_scaffold_and_field_translation=public.read_text(),source_sha256=h(c/'deferred.c'),header_sha256=h(c/'deferred.h'),event_wrapper_sha256=h(root/'g2/components/case/event_flags_offline/events.c')),indent=2)+'\n');print(elf)
