#ifndef R1_SCHEDULER_TICK_CONTRACT_H
#define R1_SCHEDULER_TICK_CONTRACT_H
#include "FreeRTOS.h"
#include "task.h"
#include "list.h"
#include <stddef.h>
/* Only the accessed native prefix is admitted. Full TCB allocation remains gated. */
typedef struct { StackType_t *pxTopOfStack; ListItem_t xStateListItem,xEventListItem; UBaseType_t uxPriority; } TCB_t;
_Static_assert(sizeof(TCB_t)==48 && offsetof(TCB_t,xStateListItem)==4 && offsetof(TCB_t,xEventListItem)==24 && offsetof(TCB_t,uxPriority)==44,"native accessed TCB prefix");
_Static_assert(sizeof(List_t)==20 && configMAX_PRIORITIES==56 && configUSE_PORT_OPTIMISED_TASK_SELECTION==0,"native scheduler list variant");
/* Existing tick provider owns this private kernel word at its native address. */
#define uxSchedulerSuspended (*(volatile UBaseType_t *)(uintptr_t)UINT32_C(0x20007850))
extern TCB_t *volatile pxCurrentTCB;
extern volatile UBaseType_t uxCurrentNumberOfTasks,uxTopReadyPriority;
extern volatile TickType_t xPendedTicks,xNextTaskUnblockTime;
extern volatile BaseType_t xYieldPending;
extern List_t *volatile pxDelayedTaskList;
extern List_t pxReadyTasksLists[configMAX_PRIORITIES],xPendingReadyList;
static void prvResetNextTaskUnblockTime(void);
#define taskYIELD_IF_USING_PREEMPTION() portYIELD_WITHIN_API()
/* Existing tick-getter provider owns this private native counter. */
#define xTickCount (*(volatile TickType_t *)(uintptr_t)UINT32_C(0x20007828))
List_t *volatile pxOverflowDelayedTaskList;
volatile BaseType_t xNumOfOverflows;
List_t xDelayedTaskList1,xDelayedTaskList2;
#endif
