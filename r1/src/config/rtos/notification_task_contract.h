#ifndef R1_NOTIFICATION_TASK_CONTRACT_H
#define R1_NOTIFICATION_TASK_CONTRACT_H
#include "FreeRTOS.h"
#include "task.h"
#include "list.h"
#include <stddef.h>
/* Same authenticated112-byte ABI, with upstream single-entry array spelling. */
typedef struct tskTaskControlBlock {
 StackType_t *pxTopOfStack;ListItem_t xStateListItem,xEventListItem;
 UBaseType_t uxPriority;StackType_t *pxStack;char pcTaskName[32];
 UBaseType_t uxNativeStackDepth,uxTCBNumber,opaque92,uxBasePriority,uxMutexesHeld;
 volatile uint32_t ulNotifiedValue[1];volatile uint8_t ucNotifyState[1];
 uint8_t ucStaticallyAllocated,padding110[2];
} TCB_t;
_Static_assert(sizeof(TCB_t)==112 && offsetof(TCB_t,pxStack)==48 && offsetof(TCB_t,ucNotifyState)==108 && offsetof(TCB_t,ucStaticallyAllocated)==109,"native termination TCB ABI");
_Static_assert(configTASK_NOTIFICATION_ARRAY_ENTRIES==1 && configUSE_PORT_OPTIMISED_TASK_SELECTION==0,"native termination variant");
extern TCB_t *volatile pxCurrentTCB;
extern volatile UBaseType_t uxCurrentNumberOfTasks,uxTaskNumber;
extern List_t *volatile pxDelayedTaskList,*volatile pxOverflowDelayedTaskList;
extern List_t xSuspendedTaskList,xTasksWaitingTermination;
extern volatile UBaseType_t uxDeletedTasksWaitingCleanUp;
#define xSchedulerRunning (*(volatile BaseType_t *)(uintptr_t)UINT32_C(0x20007830))
#define uxSchedulerSuspended (*(volatile UBaseType_t *)(uintptr_t)UINT32_C(0x20007850))
#define tskDYNAMICALLY_ALLOCATED_STACK_AND_TCB ((uint8_t)0)
#define tskSTATICALLY_ALLOCATED_STACK_ONLY ((uint8_t)1)
#define tskSTATICALLY_ALLOCATED_STACK_AND_TCB ((uint8_t)2)
static void prvResetNextTaskUnblockTime(void);
extern volatile TickType_t xNextTaskUnblockTime;
extern volatile UBaseType_t uxTopReadyPriority;
extern List_t pxReadyTasksLists[configMAX_PRIORITIES];
#define xTickCount (*(volatile TickType_t *)(uintptr_t)UINT32_C(0x20007828))
extern List_t xPendingReadyList;
extern volatile BaseType_t xYieldPending;
#define xTickCount (*(volatile TickType_t *)(uintptr_t)UINT32_C(0x20007828))
static void prvAddCurrentTaskToDelayedList(TickType_t,BaseType_t);
void vPortValidateInterruptPriority(void);
#undef portASSERT_IF_INTERRUPT_PRIORITY_INVALID
#define portASSERT_IF_INTERRUPT_PRIORITY_INVALID() vPortValidateInterruptPriority()
#endif
