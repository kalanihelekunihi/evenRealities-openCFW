/* Hardware checks for the R1 Cordio replacement of S140 manager enable. */
#if defined(R1_CORDIO_RTC0)
#include <stdbool.h>

#include "nrf_drv_clock.h"
#include "nrf.h"
#include "nrf_soc.h"
#include "cordio_lifecycle_hw.h"
#include "r1_flash_cordio.h"

bool r1_cordio_lfclk_is_running(void)
{
    return nrf_drv_clock_lfclk_is_running();
}

bool r1_cordio_sd_evt_irq_prepare(void)
{
    if (NVIC_GetEnableIRQ(SD_EVT_IRQn) != 0u) {
        return false;
    }
    NVIC_SetPriority(SD_EVT_IRQn, 6u);
    NVIC_ClearPendingIRQ(SD_EVT_IRQn);
    return true;
}

extern void r1_cordio_sys_release_hfclk(void);
extern void r1_cordio_rtc_release_lfclk(void);

void r1_cordio_hardware_shutdown(void)
{
    /* The DM reset completed before the SDK accepted disable. No radio
     * procedure can be left running when these Cordio-owned IRQs stop. */
    NVIC_DisableIRQ(RTC1_IRQn);
    r1_cordio_flash_disable();
    NVIC_DisableIRQ(RADIO_IRQn);
    NVIC_DisableIRQ(TIMER0_IRQn);
    NVIC_DisableIRQ(TIMER1_IRQn);
    NVIC_DisableIRQ(CCM_AAR_IRQn);
    NRF_RTC1->INTENCLR = 0xffffffffu;
    NRF_RTC1->TASKS_STOP = 1u;
    NRF_TIMER0->INTENCLR = 0xffffffffu;
    NRF_TIMER0->TASKS_STOP = 1u;
    NRF_TIMER1->INTENCLR = 0xffffffffu;
    NRF_TIMER1->TASKS_STOP = 1u;
    NRF_RADIO->INTENCLR = 0xffffffffu;
    NRF_RADIO->TASKS_DISABLE = 1u;
    r1_cordio_sys_release_hfclk();
    r1_cordio_rtc_release_lfclk();
}
#endif
