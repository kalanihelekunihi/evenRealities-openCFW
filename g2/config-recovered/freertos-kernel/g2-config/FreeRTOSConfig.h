/*
 * G2 Apollo-main FreeRTOS configuration, recovered from official firmware
 * s200_v2.2.6.10 (ota_s200_firmware_ota.bin, application VA = file offset
 * + 0x437FE0).
 *
 * Applies to: FreeRTOS-Kernel V10.5.1 def7d2df (third-party/upstream/
 * freertos-kernel) with ../g2-patches/g2-tcb-v10.5.1.patch, the
 * ARM_CM55_NTZ/non_secure port, CMSIS-FreeRTOS cmsis_os2.c d213f261 and
 * FreeRTOS-Plus-CLI 43defa56.
 *
 * Every value carries its confidence (see ../../README.md):
 *   Proven - pinned to instruction or data bytes in the stock image;
 *   Strong - required by consistent structural evidence;
 *   Compat - openCFW choice where the image cannot discriminate.
 * An option that is absent keeps the FreeRTOS/CMSIS default; that default is
 * not itself a recovered value.  Addresses are stock Apollo-main VAs.  The
 * port/TCB/object-layout evidence is summarised in
 * g2/docs/reference/libraries.md section 1.2 (from the retired
 * freertos-g2-config-port-audit.md, Git 4ae5a2d24^).
 */
#ifndef FREERTOS_CONFIG_H
#define FREERTOS_CONFIG_H

#ifndef __ASSEMBLER__
#include <stdint.h>
#endif

/* ---- Port: IAR/GCC ARM_CM55_NTZ/non_secure ------------------------------ */
/* Proven: PendSV 0x5FA0C8 saves only {PSPLIM, EXC_RETURN, r4-r11}; no secure
 * context word, no SecureContext_* calls, SVC C handler 0x442134 accepts only
 * SVC 2. */
#define configENABLE_TRUSTZONE                   0
/* Proven: no CONTROL word in the task frame (pxPortInitialiseStack 0x44215A)
 * and no MPU programming. */
#define configENABLE_MPU                         0
/* Proven: prvSetupFPU 0x4420A6 sets CPACR CP10/CP11 and FPCCR ASPEN|LSPEN;
 * PendSV conditionally saves s16-s31. */
#define configENABLE_FPU                         1
/* Compat: FPU=1 already produces the same port code; MVE is not observable. */
#define configENABLE_MVE                         0
/* Compat: the NTZ port runs non-secure-only; not observable separately. */
#define configRUN_FREERTOS_SECURE_ONLY           0
/* Compat: only the weak SysTick setup/tickless code in port.c reads this, and
 * stock replaces both with the Apollo STIMER versions at 0x45643E/0x456498. */
#define configCPU_CLOCK_HZ                       96000000UL

/* ---- Interrupt priorities ------------------------------------------------ */
/* Proven: ulSetInterruptMask 0x5FA0A4 writes BASEPRI = 0x30 (logical 3 with
 * the Apollo510's four priority bits).  The port's PendSV/SysTick priority
 * is its own constant 0xFF (xPortStartScheduler 0x4421E2), not a config. */
#define configMAX_SYSCALL_INTERRUPT_PRIORITY     0x30

/* ---- Scheduler ------------------------------------------------------------ */
/* Proven: vTaskSwitchContext 0x4551B4 scans ready lists downward (no CLZ). */
#define configUSE_PORT_OPTIMISED_TASK_SELECTION  0
/* Proven: priorities are bounded by 0x38 and clamped to 0x37; 56 ready lists
 * of 20 bytes at 0x2006A49C. */
#define configMAX_PRIORITIES                     56
/* Proven: name copy bound and terminator at TCB +0x53. */
#define configMAX_TASK_NAME_LEN                  32
/* Proven: 32-bit tick arithmetic, portMAX_DELAY = 0xFFFFFFFF
 * (xTaskCheckForTimeOut 0x455566). */
#define configUSE_16_BIT_TICKS                   0
/* Proven: STIMER 32.768 kHz XTAL / 32 counts per tick (vPortSetupTimerInterrupt
 * override 0x45643E stores 32 and selects CFG 0x103). */
#define configTICK_RATE_HZ                       1024
/* Proven: unblocking an equal/higher priority task requests a switch. */
#define configUSE_PREEMPTION                     1
/* Proven: xTaskIncrementTick 0x45504C yields when the current ready list holds
 * more than one task. */
#define configUSE_TIME_SLICING                   1
/* Proven: the idle task yields when the priority-0 list holds two or more. */
#define configIDLE_SHOULD_YIELD                  1
/* Proven: idle calls vPortSuppressTicksAndSleep (STIMER override 0x456498)
 * when prvGetExpectedIdleTime 0x454D88 reaches 2. */
#define configUSE_TICKLESS_IDLE                  1
#define configEXPECTED_IDLE_TIME_BEFORE_SLEEP    2
/* Proven: osThreadNew 0x4490E2 uses 0x400 words as its default stack
 * (CMSIS takes configMINIMAL_STACK_SIZE), the same depth the idle-task
 * memory callback 0x48D558 returns. */
#define configMINIMAL_STACK_SIZE                 1024
/* Proven: osThreadNew narrows the stack depth with UXTH before calling
 * xTaskCreate 0x4548BA (0x449194). */
#define configSTACK_DEPTH_TYPE                   uint16_t

/* ---- Hooks ---------------------------------------------------------------- */
/* Proven: idle task calls vApplicationIdleHook 0x46D898. */
#define configUSE_IDLE_HOOK                      1
/* Proven: neither xTaskIncrementTick path calls a tick hook. */
#define configUSE_TICK_HOOK                      0
/* Proven: pvPortMalloc 0x456110 calls vApplicationMallocFailedHook 0x46D85E. */
#define configUSE_MALLOC_FAILED_HOOK             1
/* Proven: every switch compares four 0xA5A5A5A5 words at pxStack and calls
 * vApplicationStackOverflowHook 0x46D86C (method 2). */
#define configCHECK_FOR_STACK_OVERFLOW           2
/* Proven: the timer service task starts its loop without a startup hook. */
#define configUSE_DAEMON_TASK_STARTUP_HOOK       0

/* ---- Allocation ------------------------------------------------------------ */
/* Proven: static and dynamic creators for tasks, queues, timers, event groups
 * and stream buffers, plus the provenance bytes in each object. */
#define configSUPPORT_STATIC_ALLOCATION          1
#define configSUPPORT_DYNAMIC_ALLOCATION         1
/* Proven: heap_4 (0x456110..0x456338), immediate 0x2F000 in prvHeapInit
 * 0x456280, ucHeap at 0x20004558. */
#define configTOTAL_HEAP_SIZE                    0x2F000
/* Proven: vPortFree 0x456210 has no payload clear. */
#define configHEAP_CLEAR_MEMORY_ON_FREE          0

/* ---- Timers ------------------------------------------------------------------ */
/* Proven: timer lists, queue, service task and API family present. */
#define configUSE_TIMERS                         1
/* Proven: xTimerCreateTimerTask 0x47E674 passes priority 0x36. */
#define configTIMER_TASK_PRIORITY                54
/* Proven: static timer queue created as (50, 16, ...). */
#define configTIMER_QUEUE_LENGTH                 50
/* Compat: compiled out by static timer-task allocation; 4096 matches the depth
 * the stock vApplicationGetTimerTaskMemory 0x4D3610 returns. */
#define configTIMER_TASK_STACK_DEPTH             4096
/* Proven: 16-byte daemon messages and xTimerPendFunctionCallFromISR. */
#define INCLUDE_xTimerPendFunctionCall           1

/* ---- Kernel objects ------------------------------------------------------------ */
/* Proven: mutex holder / base priority / mutexes-held (TCB +0x60/+0x64). */
#define configUSE_MUTEXES                        1
/* Proven: xQueueGiveMutexRecursive 0x441710 / xQueueTakeMutexRecursive 0x441750. */
#define configUSE_RECURSIVE_MUTEXES              1
/* Proven: xQueueCreateCountingSemaphoreStatic 0x441790 and
 * xQueueCreateCountingSemaphore 0x4417C2. */
#define configUSE_COUNTING_SEMAPHORES            1
/* Proven: trace numbers in TCB (+0x58/+0x5C), Queue_t (+0x48/+0x4C),
 * Timer_t (+0x24), EventGroup_t (+0x18), StreamBuffer_t (+0x20). */
#define configUSE_TRACE_FACILITY                 1
/* Proven: Queue_t is exactly 0x50 bytes, no queue-set container word. */
#define configUSE_QUEUE_SETS                     0
/* Proven: timer-queue creation has no registry call. */
#define configQUEUE_REGISTRY_SIZE                0
/* Proven: one notification value (+0x68) and one state byte (+0x6C). */
#define configUSE_TASK_NOTIFICATIONS             1
#define configTASK_NOTIFICATION_ARRAY_ENTRIES    1
/* Proven: xStreamBufferGenericCreate 0x57DEEA allocates size + 1 + 0x24 and
 * xStreamBufferGenericCreateStatic 0x57DF7C checks a 0x24-byte object:
 * no completed-callback pointers. */
#define configUSE_SB_COMPLETED_CALLBACK          0

/* ---- TCB fields (Strong: required for the 112-byte stock TCB) -------------- */
#define configUSE_APPLICATION_TASK_TAG           0
#define configNUM_THREAD_LOCAL_STORAGE_POINTERS  0
#define configGENERATE_RUN_TIME_STATS            0
#define configUSE_NEWLIB_REENTRANT               0
#define configUSE_C_RUNTIME_TLS_SUPPORT          0
#define configUSE_POSIX_ERRNO                    0
/* Strong: TCB +0x54 is the G2 stack-depth word (g2-tcb patch), not
 * pxEndOfStack. */
#define configRECORD_STACK_HIGH_ADDRESS          0
/* Compat: no formatting functions (vTaskList/vTaskGetRunTimeStats) are linked. */
#define configUSE_STATS_FORMATTING_FUNCTIONS     0

/* ---- Optional API ---------------------------------------------------------------- */
/* Proven: xTaskCheckForTimeOut implements the portMAX_DELAY indefinite wait. */
#define INCLUDE_vTaskSuspend                     1
/* Strong: xTaskCheckForTimeOut has no aborted-delay test. */
#define INCLUDE_xTaskAbortDelay                  0
/* Proven: function present in the stock tasks.c sequence. */
#define INCLUDE_vTaskDelete                      1   /* 0x454AAE */
#define INCLUDE_vTaskDelay                       1   /* 0x454B4C */
#define INCLUDE_eTaskGetState                    1   /* 0x454B88 */
#define INCLUDE_vTaskPrioritySet                 1   /* 0x454C12 */
#define INCLUDE_xTaskGetCurrentTaskHandle        1   /* 0x45589C */
#define INCLUDE_xTaskGetSchedulerState           1   /* 0x4558A4 */
/* Strong: cmsis_os2.c (freertos_os2.h) refuses to build without these, and the
 * stock wrapper set (osMutexNew 0x44971C, osDelayUntil family, osThreadGet*)
 * is CMSIS-FreeRTOS. */
#define INCLUDE_xSemaphoreGetMutexHolder         1
#define INCLUDE_xTaskDelayUntil                  1
#define INCLUDE_uxTaskGetStackHighWaterMark      1
#define INCLUDE_uxTaskPriorityGet                1

/* ---- Assertions ------------------------------------------------------------------- */
/* Proven: every assertion site (e.g. vQueueDelete 0x441EA2) is
 *   bl ulSetInterruptMask; movs r0,#0; mvn r1,#0; str r0,[r1]; b .
 * i.e. mask interrupts, store 0 to 0xFFFFFFFF, spin. */
#define configASSERT( x )                                        \
    if( ( x ) == 0 )                                             \
    {                                                            \
        portDISABLE_INTERRUPTS();                                \
        *( ( volatile uint32_t * ) 0xFFFFFFFFUL ) = 0UL;         \
        for( ; ; )                                               \
        {                                                        \
        }                                                        \
    }

/* ---- FreeRTOS-Plus-CLI ---------------------------------------------------------------- */
/* Compat: FreeRTOS_CLIGetOutputBuffer and its static buffer are absent from
 * the stock image, so the size is not observable; 128 matches the stock
 * console caller buffers. */
#define configCOMMAND_INT_MAX_OUTPUT_SIZE        128

/* ---- Trace hooks ------------------------------------------------------------------- */
/* Proven: vTaskSwitchContext 0x4551B4 records {outgoing, incoming}
 * uxTCBNumber (TCB +0x58) into a 64-entry ring of 8-byte pairs at 0x2006F348,
 * index at 0x20074A5C (re-read volatile, wrapped at 64).  Both objects are
 * defined in the generated G2 tasks.c (see g2/src/sources.json "generated").
 * Compat: stock stores the outgoing number after the stack-overflow check;
 * traceTASK_SWITCHED_OUT runs just before it in V10.5.1 (same effect). */
#define traceTASK_SWITCHED_OUT()                                                         \
    ( xG2TaskSwitchHistory[ uxG2TaskSwitchHistoryIndex ][ 0 ] = pxCurrentTCB->uxTCBNumber )
#define traceTASK_SWITCHED_IN()                                                          \
    do {                                                                                 \
        xG2TaskSwitchHistory[ uxG2TaskSwitchHistoryIndex ][ 1 ] = pxCurrentTCB->uxTCBNumber; \
        uxG2TaskSwitchHistoryIndex++;                                                    \
        if( uxG2TaskSwitchHistoryIndex >= 64U )                                          \
        {                                                                                \
            uxG2TaskSwitchHistoryIndex = 0U;                                             \
        }                                                                                \
    } while( 0 )

#endif /* FREERTOS_CONFIG_H */
