#ifndef FREERTOS_CONFIG_H
#define FREERTOS_CONFIG_H

#ifdef SOFTDEVICE_PRESENT
#include "nrf_soc.h"
#endif
#include "app_util_platform.h"

#define FREERTOS_USE_RTC 0
#define FREERTOS_USE_SYSTICK 1
#define configTICK_SOURCE FREERTOS_USE_RTC

/* Recovered CMSIS-FreeRTOS configuration boundary. */
#define configCPU_CLOCK_HZ (SystemCoreClock)
#define configTICK_RATE_HZ 1024
#define configMAX_PRIORITIES 56
#define configMINIMAL_STACK_SIZE 256
#define configMAX_TASK_NAME_LEN 16

#define configUSE_PREEMPTION 1
#define configUSE_PORT_OPTIMISED_TASK_SELECTION 0
#define configUSE_TICKLESS_IDLE 1
#define configUSE_TICKLESS_IDLE_SIMPLE_DEBUG 1
#define configTOTAL_HEAP_SIZE 32768
#define configUSE_16_BIT_TICKS 0
#define configIDLE_SHOULD_YIELD 1
#define configUSE_MUTEXES 1
#define configUSE_RECURSIVE_MUTEXES 1
#define configUSE_COUNTING_SEMAPHORES 1
#define configUSE_TASK_NOTIFICATIONS 1
#define configUSE_ALTERNATIVE_API 0
#define configQUEUE_REGISTRY_SIZE 2
#define configUSE_QUEUE_SETS 0
#define configUSE_TIME_SLICING 1
#define configUSE_NEWLIB_REENTRANT 0
#define configENABLE_BACKWARD_COMPATIBILITY 1
#define configSUPPORT_STATIC_ALLOCATION 1
#define configSUPPORT_DYNAMIC_ALLOCATION 1

#define configUSE_IDLE_HOOK 0
#define configUSE_TICK_HOOK 0
#define configCHECK_FOR_STACK_OVERFLOW 2
#define configUSE_MALLOC_FAILED_HOOK 0
#define configGENERATE_RUN_TIME_STATS 0
#define configUSE_TRACE_FACILITY 1
#define configUSE_STATS_FORMATTING_FUNCTIONS 0
#define configUSE_CO_ROUTINES 0
#define configMAX_CO_ROUTINE_PRIORITIES 2

#define configUSE_TIMERS 1
#define configTIMER_TASK_PRIORITY 40
#define configTIMER_QUEUE_LENGTH 32
#define configTIMER_TASK_STACK_DEPTH 256
#define configEXPECTED_IDLE_TIME_BEFORE_SLEEP 2

#define configUSE_OS2_THREAD_ENUMERATE 0
#define configUSE_OS2_THREAD_SUSPEND_RESUME 1
#define configUSE_OS2_EVENTFLAGS_FROM_ISR 1
#define configUSE_OS2_THREAD_FLAGS 1
#define configUSE_OS2_TIMER 1
#define configUSE_OS2_MUTEX 1

#if defined(DEBUG_NRF) || defined(DEBUG_NRF_USER)
#define configASSERT(x) ASSERT(x)
#endif

#define configINCLUDE_APPLICATION_DEFINED_PRIVILEGED_FUNCTIONS 1
#define INCLUDE_vTaskPrioritySet 1
#define INCLUDE_uxTaskPriorityGet 1
#define INCLUDE_vTaskDelete 1
#define INCLUDE_vTaskSuspend 1
#define INCLUDE_xResumeFromISR 1
#define INCLUDE_xTaskDelayUntil 1
#define INCLUDE_vTaskDelay 1
#define INCLUDE_xTaskGetSchedulerState 1
#define INCLUDE_xTaskGetCurrentTaskHandle 1
#define INCLUDE_uxTaskGetStackHighWaterMark 1
#define INCLUDE_xTaskGetIdleTaskHandle 1
#define INCLUDE_xTimerGetTimerDaemonTaskHandle 1
#define INCLUDE_pcTaskGetTaskName 1
#define INCLUDE_eTaskGetState 1
#define INCLUDE_xEventGroupSetBitFromISR 1
#define INCLUDE_xTimerPendFunctionCall 1
#define INCLUDE_xSemaphoreGetMutexHolder 1

/*
 * Arm CMSIS-FreeRTOS v10.5.1 contains an osDelayUntil section for the newer
 * xTaskDelayUntil API. Nordic's identified 10.0.0 kernel has the same-width
 * types but exports only vTaskDelayUntil. The stock R1 image did not retain
 * osDelayUntil, so declare the upstream API solely to compile that unused
 * section; --gc-sections removes it and no local implementation is supplied.
 */
int32_t xTaskDelayUntil(uint32_t * const previous_wake_time,
                        const uint32_t time_increment);

#define configLIBRARY_LOWEST_INTERRUPT_PRIORITY 0x0f
#define configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY _PRIO_APP_HIGH
#define configKERNEL_INTERRUPT_PRIORITY configLIBRARY_LOWEST_INTERRUPT_PRIORITY
#define configMAX_SYSCALL_INTERRUPT_PRIORITY configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY

#define vPortSVCHandler SVC_Handler
#define xPortPendSVHandler PendSV_Handler

#if (configTICK_SOURCE == FREERTOS_USE_SYSTICK)
#define xPortSysTickHandler SysTick_Handler
#elif (configTICK_SOURCE == FREERTOS_USE_RTC)
#define configSYSTICK_CLOCK_HZ (32768UL)
#define xPortSysTickHandler RTC1_IRQHandler
#else
#error Unsupported configTICK_SOURCE value
#endif

#if !(defined(__ASSEMBLY__) || defined(__ASSEMBLER__))
#include "nrf.h"
#include "nrf_assert.h"
#ifdef __NVIC_PRIO_BITS
#define configPRIO_BITS __NVIC_PRIO_BITS
#else
#error This port requires __NVIC_PRIO_BITS
#endif
#endif

#define configUSE_DISABLE_TICK_AUTO_CORRECTION_DEBUG 0

#endif
