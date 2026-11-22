#ifndef R1_PORT_START_CONTRACT_H
#define R1_PORT_START_CONTRACT_H
#include "FreeRTOS.h"
#include "task.h"
#include "nrf_rtc.h"
#include "nrf_drv_clock.h"
#if defined(R1_CORDIO_RTC0)
/* Cordio owns RTC1 and all four of its compare channels. The R1 tick uses
 * RTC0 only in the source-built BLE variant. */
#undef portNRF_RTC_REG
#undef portNRF_RTC_IRQn
#define portNRF_RTC_REG NRF_RTC0
#define portNRF_RTC_IRQn RTC0_IRQn
#endif
/* Existing selected port units own these private state words. */
#define ucMaxSysCallPriority (*(volatile uint8_t *)(uintptr_t)UINT32_C(0x20007810))
#define uxCriticalNesting (*(volatile UBaseType_t *)(uintptr_t)UINT32_C(0x20007814))
#define ulMaxPRIGROUPValue (*(volatile uint32_t *)(uintptr_t)UINT32_C(0x20007818))
void vPortStartFirstTask(void);
void vPortSetupTimerInterrupt(void);
static void vPortEnableVFP(void);
#define prvTaskExitError r1_port_start_unexpected_return
static void prvTaskExitError(void);
_Static_assert(configASSERT_DEFINED==1 && configMAX_SYSCALL_INTERRUPT_PRIORITY==2 && configKERNEL_INTERRUPT_PRIORITY==15,"native raw priority configuration");
_Static_assert(configTICK_SOURCE==FREERTOS_USE_RTC && portNRF_RTC_PRESCALER==31,"R1 RTC tick setup");
#if defined(R1_CORDIO_RTC0)
_Static_assert(RTC0_IRQn==11 && portNRF_RTC_IRQn==RTC0_IRQn,"Cordio RTC0 tick ownership");
#else
_Static_assert(RTC1_IRQn==17 && portNRF_RTC_IRQn==RTC1_IRQn,"native RTC1 setup");
#endif
#endif
