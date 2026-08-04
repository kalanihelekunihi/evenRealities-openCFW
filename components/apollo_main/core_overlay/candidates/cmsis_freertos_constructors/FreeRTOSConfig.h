/*
 * Compile-closure-only FreeRTOS configuration for the authenticated
 * CMSIS-FreeRTOS v10.5.1 constructor candidate.
 *
 * This is deliberately outside the production overlay.  Values below are
 * either recovered from the official G2 2.2.6.10 image or are mandatory
 * inclusion switches imposed by the authenticated CMSIS-FreeRTOS wrapper.
 * The latter switches prove that the translation unit can compile; they do
 * not yet claim a complete byte-identical G2 FreeRTOSConfig.h.
 */

#ifndef OPEN_CFW_CMSIS_FREERTOS_CONSTRUCTOR_CONFIG_H
#define OPEN_CFW_CMSIS_FREERTOS_CONSTRUCTOR_CONFIG_H

#include <stdint.h>

/*
 * CMSIS 5.9 tests __ARM_ARCH_8M_MAIN__, whereas Clang identifies Cortex-M55
 * with the more precise __ARM_ARCH_8_1M_MAIN__.  The compatibility alias
 * selects the BASEPRI-aware IRQ_Context path seen in the stock G2 helper.
 */
#if defined(__ARM_ARCH_8_1M_MAIN__) && !defined(__ARM_ARCH_8M_MAIN__)
#define __ARM_ARCH_8M_MAIN__ 1
#endif

/* Recovered G2 scheduler and ABI configuration. */
#define configENABLE_FPU                         1
#define configENABLE_MPU                         0
#define configENABLE_TRUSTZONE                   0
#define configMAX_SYSCALL_INTERRUPT_PRIORITY     0x30U
#define portCRITICAL_NESTING_IN_TCB              0

#define configMAX_PRIORITIES                     56
#define configMAX_TASK_NAME_LEN                  32
#define configMINIMAL_STACK_SIZE                 0x400U
#define configTICK_RATE_HZ                       1024U
#define configUSE_16_BIT_TICKS                   0
#define configUSE_PREEMPTION                     1
#define configUSE_TIME_SLICING                   1
#define configIDLE_SHOULD_YIELD                  1
#define configUSE_PORT_OPTIMISED_TASK_SELECTION  0
#define configUSE_TICKLESS_IDLE                  1
#define configEXPECTED_IDLE_TIME_BEFORE_SLEEP    2

#define configUSE_IDLE_HOOK                      1
#define configUSE_TICK_HOOK                      0
#define configCHECK_FOR_STACK_OVERFLOW           2
#define configUSE_MALLOC_FAILED_HOOK             1

#define configSUPPORT_STATIC_ALLOCATION          1
#define configSUPPORT_DYNAMIC_ALLOCATION         1
#define configTOTAL_HEAP_SIZE                    0x2F000U
#define configHEAP_CLEAR_MEMORY_ON_FREE           0

#define configUSE_TIMERS                         1
#define configTIMER_QUEUE_LENGTH                 50
#define configTIMER_TASK_PRIORITY                54
#define configTIMER_TASK_STACK_DEPTH             0x1000U
#define configUSE_DAEMON_TASK_STARTUP_HOOK       0

#define configQUEUE_REGISTRY_SIZE                0
#define configUSE_MUTEXES                        1
#define configUSE_RECURSIVE_MUTEXES              1
#define configUSE_COUNTING_SEMAPHORES            1
#define configUSE_QUEUE_SETS                     0
#define configUSE_TRACE_FACILITY                 1
#define configUSE_TASK_NOTIFICATIONS             1
#define configTASK_NOTIFICATION_ARRAY_ENTRIES    1

/* Recovered fields needed to retain the observed G2 TCB shape. */
#define configUSE_APPLICATION_TASK_TAG           0
#define configNUM_THREAD_LOCAL_STORAGE_POINTERS  0
#define configGENERATE_RUN_TIME_STATS            0
#define configUSE_NEWLIB_REENTRANT               0
#define configUSE_C_RUNTIME_TLS_SUPPORT          0
#define configUSE_POSIX_ERRNO                    0
#define configRECORD_STACK_HIGH_ADDRESS          0
#define INCLUDE_xTaskAbortDelay                  0

/*
 * Required by freertos_os2.h's full translation-unit contract.  These are
 * compile-surface switches, not a claim that every stock G2 INCLUDE_* value
 * has already been recovered.
 */
#define INCLUDE_xSemaphoreGetMutexHolder         1
#define INCLUDE_vTaskDelay                       1
#define INCLUDE_xTaskDelayUntil                  1
#define INCLUDE_vTaskDelete                      1
#define INCLUDE_xTaskGetCurrentTaskHandle        1
#define INCLUDE_xTaskGetSchedulerState           1
#define INCLUDE_uxTaskGetStackHighWaterMark      1
#define INCLUDE_uxTaskPriorityGet                1
#define INCLUDE_vTaskPrioritySet                 1
#define INCLUDE_eTaskGetState                    1
#define INCLUDE_vTaskSuspend                     1
#define INCLUDE_xTimerPendFunctionCall           1

/*
 * The Apollo STIMER replaces the architectural SysTick calculation, so the
 * original numeric configCPU_CLOCK_HZ is not recoverable from that path.
 * Keep the standard CMSIS clock symbol as an explicit, unresolved seam.
 */
extern uint32_t SystemCoreClock;
#define configCPU_CLOCK_HZ                       SystemCoreClock

/*
 * G2 has assertions enabled.  The production fatal implementation and its
 * final symbol binding remain a stock seam; a no-op assertion would hide it.
 */
void open_cfw_cmsis_freertos_assert_fail(void);
#define configASSERT(condition)                                      \
    do {                                                             \
        if (!(condition)) {                                          \
            open_cfw_cmsis_freertos_assert_fail();                    \
        }                                                            \
    } while (0)

#endif /* OPEN_CFW_CMSIS_FREERTOS_CONSTRUCTOR_CONFIG_H */
