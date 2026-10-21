#ifndef R1_TICKLESS_PORT_CONTRACT_H
#define R1_TICKLESS_PORT_CONTRACT_H
#include "FreeRTOS.h"
#include "task.h"
#include "nrf_soc.h"
#include "nrf_sdh.h"
#include "app_error.h"
#include "nrf_rtc.h"
void r1_adc_error(uint32_t);
#undef APP_ERROR_CHECK
#define APP_ERROR_CHECK(value) do { uint32_t r1_error=(value); if(r1_error) r1_adc_error(r1_error); } while(0)
/* Native95e62..95e84: clear pending FPU exceptions before wait. */
static inline void r1_tickless_fpu_prepare(void) {
 if (NVIC->ISPR[1] & (UINT32_C(1)<<6)) {
  __set_FPSCR(__get_FPSCR() & ~UINT32_C(0x9f));
  (void)__get_FPSCR();NVIC_ClearPendingIRQ(FPU_IRQn);
 }
}
#undef configPRE_SLEEP_PROCESSING
#define configPRE_SLEEP_PROCESSING(ticks) do { if ((ticks)>0) r1_tickless_fpu_prepare(); } while(0)
_Static_assert(configTICK_SOURCE==FREERTOS_USE_RTC && configUSE_TICKLESS_IDLE==1 && configUSE_TICKLESS_IDLE_SIMPLE_DEBUG==1 && portNRF_RTC_MAXTICKS==0xffffff && configEXPECTED_IDLE_TIME_BEFORE_SLEEP==2,"native RTC sleep configuration");
_Static_assert(RTC1_IRQn==17 && FPU_IRQn==38,"native IRQ numbers");
#endif
