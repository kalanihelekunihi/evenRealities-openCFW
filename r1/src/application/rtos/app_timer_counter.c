/* Counter half of Nordic app_timer for the R1 FreeRTOS RTC1 backend.
 * Timer lifecycle remains owned by app_timer_freertos.c. Reading the existing
 * RTC does not initialize it, change its prescaler or claim its interrupt. */
#include "FreeRTOS.h"
#include "app_timer.h"
#include "nrf_rtc.h"
#include "portmacro_cmsis.h"

_Static_assert(configTICK_SOURCE == FREERTOS_USE_RTC && RTC1_IRQn == 17,
               "R1 app_timer counter requires the selected RTC1 backend");
_Static_assert(configTICK_RATE_HZ == 1024 && configSYSTICK_CLOCK_HZ == 32768 &&
               portNRF_RTC_PRESCALER == 31,
               "RTC1 counter and FreeRTOS timer units must agree");
_Static_assert(APP_TIMER_TICKS(1000u) == configTICK_RATE_HZ &&
               RTC_COUNTER_COUNTER_Msk == 0x00ffffffu,
               "app_timer uses RTOS ticks and a 24-bit RTC counter");

uint32_t app_timer_cnt_get(void)
{
    return nrf_rtc_counter_get(NRF_RTC1);
}

uint32_t app_timer_cnt_diff_compute(uint32_t ticks_to, uint32_t ticks_from)
{
    return (ticks_to - ticks_from) & RTC_COUNTER_COUNTER_Msk;
}
