/* Authenticated R1 construction extensions; kernel/port ancestry is pinned
 * FreeRTOS10.5.1 and Nordic SDK17.1.0. No original executable input is linked. */
#include "native_task_construction.h"
#include <string.h>
extern void *pvPortMalloc(size_t);
extern void vPortFree(void *);
extern void vListInitialiseItem(ListItem_t *);
extern uint32_t *pxPortInitialiseStack(uint32_t *,TaskFunction_t,void *);
extern void r1_malloc_failed_hook(void) __attribute__((noreturn));
const uint32_t r1_native_initial_xpsr __attribute__((section(".r1.task.initial_xpsr")))=UINT32_C(0x01000000);
void r1_native_task_initialize(TaskFunction_t code,const char *name,uint32_t depth,void *parameter,uint32_t priority,r1_native_tcb **out,r1_native_tcb *tcb,const void *regions){
 (void)regions;
 memset(tcb->pxStack,0xa5,depth*4u);
 uintptr_t top=((uintptr_t)tcb->pxStack+depth*4u-4u)&~(uintptr_t)7u;
 if(top&7u)r1_malloc_failed_hook();
 tcb->uxNativeStackDepth=depth;
 if(name){for(uint32_t i=0;i<32;i++){tcb->pcTaskName[i]=name[i];if(!name[i])break;}tcb->pcTaskName[31]=0;}
 if(priority>=56)r1_malloc_failed_hook();
 tcb->uxPriority=priority;tcb->uxBasePriority=priority;
 vListInitialiseItem(&tcb->xStateListItem);vListInitialiseItem(&tcb->xEventListItem);
 tcb->xStateListItem.pvOwner=tcb;tcb->xEventListItem.pvOwner=tcb;
 tcb->xEventListItem.xItemValue=56u-priority;
 tcb->pxTopOfStack=pxPortInitialiseStack((uint32_t *)top,code,parameter);
 if(out)*out=tcb;
}
int32_t r1_native_task_create(TaskFunction_t code,const char *name,uint32_t depth,void *parameter,uint32_t priority,r1_native_tcb **out){
 uint32_t *stack=pvPortMalloc(depth*4u);if(!stack)return -1;
 r1_native_tcb *tcb=pvPortMalloc(112);if(!tcb){vPortFree(stack);return -1;}
 memset(tcb,0,112);tcb->pxStack=stack;tcb->ucStaticallyAllocated=0;
 r1_native_task_initialize(code,name,depth,parameter,priority,out,tcb,0);
 r1_native_task_add_ready(tcb);return 1;
}
r1_native_tcb *r1_native_task_create_static(TaskFunction_t code,const char *name,uint32_t depth,void *parameter,uint32_t priority,uint32_t *stack,r1_native_tcb *tcb){
 if(!stack || !tcb)r1_malloc_failed_hook();
 memset(tcb,0,112);tcb->pxStack=stack;tcb->ucStaticallyAllocated=2;
 r1_native_tcb *result=0;r1_native_task_initialize(code,name,depth,parameter,priority,&result,tcb,0);r1_native_task_add_ready(tcb);return result;
}
