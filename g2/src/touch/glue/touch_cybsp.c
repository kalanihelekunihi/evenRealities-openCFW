/* SPDX-License-Identifier: Apache-2.0
 * Board bring-up for G2 touch, adapted from infineon-cy8cproto-040t/cybsp.c
 * (Apache-2.0). Uses reconstructed init_cycfg_all instead of generated
 * cycfg_pins.h from the proto BSP. CY_USING_HAL is left undefined.
 */
#include <stdint.h>
#include "cy_syspm.h"
#include "../pm-callbacks/callbacks.h"

#ifndef CY_RSLT_SUCCESS
#define CY_RSLT_SUCCESS (0u)
#endif

extern void init_cycfg_all(void);
extern touch_pm_callback touch_reset_ilo_pm_descriptor;

/* Stock 0x4634 registers the reset-copied descriptor at 0x20000850.
 * The stock literal at 0x464c is CYBSP_RSLT_ERR_SYSCLK_PM_CALLBACK. */
__attribute__((noinline, used)) uint32_t cybsp_register_sysclk_pm_callback(void)
{
    if (Cy_SysPm_RegisterCallback((cy_stc_syspm_callback_t *)(void *)&touch_reset_ilo_pm_descriptor)) {
        return CY_RSLT_SUCCESS;
    }
    return 0x06020000u;
}

/* Stock 0x4650 calls generated clock/pin init, then registers the descriptor. */
uint32_t cybsp_init(void)
{
    init_cycfg_all();
    return cybsp_register_sysclk_pm_callback();
}
