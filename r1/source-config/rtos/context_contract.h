#ifndef R1_CONTEXT_CONTRACT_H
#define R1_CONTEXT_CONTRACT_H
#include "FreeRTOS.h"
#include "../../components/board/native_task_construction.h"
#include "task.h"
#include "list.h"
typedef r1_native_tcb TCB_t;
extern TCB_t *volatile pxCurrentTCB;
extern volatile UBaseType_t uxTopReadyPriority;
extern volatile BaseType_t xYieldPending;
extern List_t pxReadyTasksLists[configMAX_PRIORITIES];
#define uxSchedulerSuspended (*(volatile UBaseType_t *)(uintptr_t)UINT32_C(0x20007850))
#include "stack_macros.h"
_Static_assert(sizeof(TCB_t)==112 && offsetof(TCB_t,pxStack)==48 && offsetof(TCB_t,pcTaskName)==52 && configCHECK_FOR_STACK_OVERFLOW==2 && configUSE_PORT_OPTIMISED_TASK_SELECTION==0 && configMAX_PRIORITIES==56,"native task-selection ABI");
_Static_assert(configMAX_SYSCALL_INTERRUPT_PRIORITY==2 && configKERNEL_INTERRUPT_PRIORITY==15 && configPRIO_BITS==3,"native context masks");
#endif
