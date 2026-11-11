/* CMSIS system timer for the selected R1 RTC1 FreeRTOS port.
 * RTC1 is already configured by vPortSetupTimerInterrupt. Extend its 24-bit
 * value using the kernel's 32-bit tick epoch, including pending RTC ticks.
 * The kernel may lag RTC by less than one full 24-bit counter wrap. */
#include "FreeRTOS.h"
#include "task.h"
#include "cmsis_os2.h"
#include "nrf_rtc.h"
#include "portmacro_cmsis.h"
_Static_assert(sizeof(TickType_t) == 4 && configTICK_SOURCE == FREERTOS_USE_RTC,
               "system timer requires the 32-bit RTC FreeRTOS port");
_Static_assert(configTICK_RATE_HZ == 1024 && configSYSTICK_CLOCK_HZ == 32768 &&
               portNRF_RTC_PRESCALER == 31 && RTC_COUNTER_COUNTER_Msk == 0x00ffffffu,
               "RTC1 and kernel timer units must match");

uint32_t osKernelGetSysTimerCount(void)
{
    uint32_t primask = __get_PRIMASK();
    __disable_irq();
    uint32_t ticks = xTaskGetTickCount();
    uint32_t rtc = nrf_rtc_counter_get(NRF_RTC1);
    __set_PRIMASK(primask);
    return ticks + ((rtc - ticks) & RTC_COUNTER_COUNTER_Msk);
}

uint32_t osKernelGetSysTimerFreq(void)
{
    return configTICK_RATE_HZ;
}
