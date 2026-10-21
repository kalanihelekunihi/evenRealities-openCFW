#ifndef R1_STARTUP_TASK_CONTRACT_H
#define R1_STARTUP_TASK_CONTRACT_H
#include "FreeRTOS.h"
#include "../../application/board/native_task_construction.h"
#define StaticTask_t r1_native_tcb
#include "task.h"
#include "timers.h"
#define xTaskCreateStatic r1_native_task_create_static
#define prvIdleTask r1_native_idle_task
void r1_native_idle_task(void *);
extern TaskHandle_t xIdleTaskHandle;
extern const volatile UBaseType_t uxTopUsedPriority;
extern volatile TickType_t xNextTaskUnblockTime;
#define xTickCount (*(volatile TickType_t *)(uintptr_t)UINT32_C(0x20007828))
#define xSchedulerRunning (*(volatile BaseType_t *)(uintptr_t)UINT32_C(0x20007830))
#define configIDLE_TASK_NAME "IDLE"
_Static_assert(sizeof(StaticTask_t)==112 && configSUPPORT_STATIC_ALLOCATION==1 && configMINIMAL_STACK_SIZE==256 && configUSE_TIMERS==1,"native scheduler startup ABI");
#endif
