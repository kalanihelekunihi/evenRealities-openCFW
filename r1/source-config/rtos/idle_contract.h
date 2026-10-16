#ifndef R1_IDLE_CONTRACT_H
#define R1_IDLE_CONTRACT_H
#include "FreeRTOS.h"
#include "task.h"
#include "list.h"
#include <stdint.h>
/* Native85034 calls the watchdog idle hook; baseline configuration stays intact. */
#undef configUSE_IDLE_HOOK
#define configUSE_IDLE_HOOK 1
_Static_assert(configUSE_PREEMPTION==1 && configIDLE_SHOULD_YIELD==1 && configUSE_TICKLESS_IDLE==1 && configEXPECTED_IDLE_TIME_BEFORE_SLEEP==2,"native idle variant");
extern List_t pxReadyTasksLists[configMAX_PRIORITIES];
extern volatile TickType_t xNextTaskUnblockTime;
#define xTickCount (*(volatile TickType_t *)(uintptr_t)UINT32_C(0x20007828))
#define prvCheckTasksWaitingTermination r1_native_task_idle_cleanup
#define prvGetExpectedIdleTime r1_native_expected_idle_time
#define vApplicationIdleHook r1_native_idle_watchdog_hook
uint32_t r1_native_watchdog_hw_feed_thunk(void);
void r1_native_idle_watchdog_hook(void);
void r1_native_task_idle_cleanup(void);
TickType_t r1_native_expected_idle_time(void);
#endif
