#ifndef R1_TASK_CONSTRUCTION_CONTRACT_H
#define R1_TASK_CONSTRUCTION_CONTRACT_H
#include "native_task_construction.h"
#include "task.h"
typedef r1_native_tcb TCB_t;
extern TCB_t *volatile pxCurrentTCB;
extern volatile UBaseType_t uxCurrentNumberOfTasks,uxTopReadyPriority;
extern List_t pxReadyTasksLists[configMAX_PRIORITIES],xDelayedTaskList1,xDelayedTaskList2,xPendingReadyList,xSuspendedTaskList;
extern List_t *volatile pxDelayedTaskList,*volatile pxOverflowDelayedTaskList;
volatile UBaseType_t uxTaskNumber;
List_t xTasksWaitingTermination;
#define xSchedulerRunning (*(volatile BaseType_t *)(uintptr_t)UINT32_C(0x20007830))
#define taskYIELD_IF_USING_PREEMPTION() portYIELD_WITHIN_API()
static void prvInitialiseTaskLists(void);
#endif
