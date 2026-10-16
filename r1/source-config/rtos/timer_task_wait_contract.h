#ifndef R1_TIMER_TASK_WAIT_CONTRACT_H
#define R1_TIMER_TASK_WAIT_CONTRACT_H
#include "FreeRTOS.h"
#include "task.h"
#include "list.h"
#include <stddef.h>
/* Native accessed prefix only. The stack-depth extension is not upstream
 * pxEndOfStack semantics. Tail bytes104..111 and complete creation stay gated. */
typedef struct tskTaskControlBlock {StackType_t *pxTopOfStack;ListItem_t xStateListItem,xEventListItem;UBaseType_t uxPriority;StackType_t *pxStack;char pcTaskName[32];UBaseType_t uxNativeStackDepth;uint32_t opaque_words88_92[2];UBaseType_t uxBasePriority,uxMutexesHeld;} TCB_t;
_Static_assert(sizeof(TCB_t)==104 && offsetof(TCB_t,uxPriority)==44 && offsetof(TCB_t,uxNativeStackDepth)==84 && offsetof(TCB_t,uxBasePriority)==96 && offsetof(TCB_t,uxMutexesHeld)==100,"native accessed task prefix");
_Static_assert(sizeof(List_t)==20 && configMAX_PRIORITIES==56 && configUSE_PORT_OPTIMISED_TASK_SELECTION==0 && INCLUDE_xTaskAbortDelay==0,"native wait variant");
extern TCB_t *volatile pxCurrentTCB;
extern volatile UBaseType_t uxTopReadyPriority;
extern volatile TickType_t xNextTaskUnblockTime;
extern volatile BaseType_t xYieldPending,xNumOfOverflows;
extern List_t *volatile pxDelayedTaskList,*volatile pxOverflowDelayedTaskList;
extern List_t pxReadyTasksLists[configMAX_PRIORITIES];
extern List_t xSuspendedTaskList;
#define xTickCount (*(volatile TickType_t *)(uintptr_t)UINT32_C(0x20007828))
static void prvAddCurrentTaskToDelayedList(TickType_t,BaseType_t);
#endif
