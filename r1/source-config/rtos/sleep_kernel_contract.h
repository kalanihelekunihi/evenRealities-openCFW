#ifndef R1_SLEEP_KERNEL_CONTRACT_H
#define R1_SLEEP_KERNEL_CONTRACT_H
#include "FreeRTOS.h"
#include "task.h"
#include "list.h"
#include <stdint.h>
extern List_t xPendingReadyList,xSuspendedTaskList;
extern volatile UBaseType_t uxCurrentNumberOfTasks;
extern volatile BaseType_t xYieldPending;
extern volatile TickType_t xPendedTicks,xNextTaskUnblockTime;
#define xTickCount (*(volatile TickType_t *)(uintptr_t)UINT32_C(0x20007828))
#define uxSchedulerSuspended (*(volatile UBaseType_t *)(uintptr_t)UINT32_C(0x20007850))
_Static_assert(sizeof(TickType_t)==4 && INCLUDE_vTaskSuspend==1 && configUSE_TICKLESS_IDLE==1,"native sleep kernel variant");
#endif
