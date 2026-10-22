/* Not stock: LVGL build shim for the freestanding Apollo-main profile.
 * Values are the recovered G2 kernel settings in
 * g2/docs/reference/libraries.md (FreeRTOS); LVGL only needs the FreeRTOS
 * handle types and the lv_freertos.c API surface. Replace this -I with the
 * recovered kernel FreeRTOSConfig.h once the FreeRTOS integration provides it. */
#ifndef FREERTOS_CONFIG_H
#define FREERTOS_CONFIG_H
#include <stdint.h>
#define configENABLE_TRUSTZONE 0
#define configENABLE_MPU 0
#define configENABLE_FPU 1
#define configENABLE_MVE 0
#define configRUN_FREERTOS_SECURE_ONLY 0
#define configCPU_CLOCK_HZ 96000000UL
#define configTICK_RATE_HZ 1024
#define configMAX_SYSCALL_INTERRUPT_PRIORITY 0x30
#define configKERNEL_INTERRUPT_PRIORITY 0xFF
#define configMAX_PRIORITIES 56
#define configMAX_TASK_NAME_LEN 32
#define configMINIMAL_STACK_SIZE 256
#define configUSE_16_BIT_TICKS 0
#define configUSE_PREEMPTION 1
#define configUSE_TIME_SLICING 1
#define configIDLE_SHOULD_YIELD 1
#define configUSE_PORT_OPTIMISED_TASK_SELECTION 0
#define configUSE_TICKLESS_IDLE 1
#define configEXPECTED_IDLE_TIME_BEFORE_SLEEP 2
#define configUSE_IDLE_HOOK 1
#define configUSE_TICK_HOOK 0
#define configUSE_MALLOC_FAILED_HOOK 1
#define configCHECK_FOR_STACK_OVERFLOW 2
#define configSUPPORT_STATIC_ALLOCATION 1
#define configSUPPORT_DYNAMIC_ALLOCATION 1
#define configTOTAL_HEAP_SIZE 0x2F000
#define configUSE_TIMERS 1
#define configTIMER_TASK_PRIORITY 54
#define configTIMER_QUEUE_LENGTH 50
#define configTIMER_TASK_STACK_DEPTH 512
#define INCLUDE_xTimerPendFunctionCall 1
#define configUSE_MUTEXES 1
#define configUSE_RECURSIVE_MUTEXES 1
#define configUSE_COUNTING_SEMAPHORES 1
#define configUSE_TRACE_FACILITY 1
#define configUSE_QUEUE_SETS 0
#define configQUEUE_REGISTRY_SIZE 0
#define configTASK_NOTIFICATION_ARRAY_ENTRIES 1
#define configUSE_TASK_NOTIFICATIONS 1
#define configUSE_APPLICATION_TASK_TAG 0
#define configNUM_THREAD_LOCAL_STORAGE_POINTERS 0
#define configGENERATE_RUN_TIME_STATS 0
#define configUSE_NEWLIB_REENTRANT 0
#define INCLUDE_vTaskSuspend 1
#define INCLUDE_vTaskDelete 1
#define INCLUDE_vTaskDelay 1
#define INCLUDE_vTaskDelayUntil 1
#define INCLUDE_xTaskGetSchedulerState 1
#define INCLUDE_xTaskGetCurrentTaskHandle 1
#define INCLUDE_uxTaskGetStackHighWaterMark 1
#define INCLUDE_eTaskGetState 1
#define INCLUDE_uxTaskPriorityGet 1
#define INCLUDE_vTaskPrioritySet 1
#define INCLUDE_xSemaphoreGetMutexHolder 1
/* Stock assert shape (e.g. vQueueDelete 0x441ea2): mask, store to 0xFFFFFFFF, spin */
#define configASSERT(x) if ((x) == 0) { portDISABLE_INTERRUPTS(); *(volatile uint32_t *)0xFFFFFFFFu = 0u; for (;;) {} }
#endif
