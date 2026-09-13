/* SPDX-License-Identifier: MIT */
#include <driver/gx_clock.h>

/* Recovered upstream board policy, with a shared setter call. */
void open_cfw_gx8002_clock_lowpower_init_shared(void)
{
    for (int module = CLOCK_MODULE_RTC; module < CLOCK_MODULE_MAX; ++module) {
        GX_CLOCK_MODULE_SOURCE source = MODULE_SOURCE_1M_12M;
        switch (module) {
        case CLOCK_MODULE_AUDIO_IN_ADC:
            if (gx_clock_get_module_source(module) != MODULE_SOURCE_ADC_SYS)
                continue;
            source = MODULE_SOURCE_ADC_32K;
            break;
        case CLOCK_MODULE_AUDIO_IN_PDM:
            if (gx_clock_get_module_source(module) != MODULE_SOURCE_PDM_SYS)
                continue;
            source = MODULE_SOURCE_PDM_OSC_1M;
            break;
        case CLOCK_MODULE_AUDIO_IN_SYS:
            if (gx_clock_get_module_source(module) == MODULE_SOURCE_24M_PLL &&
                (*(volatile unsigned int *)0xa001008cu & 64u))
                continue;
            break;
        default:
            break;
        }
        gx_clock_set_module_source(module, source);
    }
}
