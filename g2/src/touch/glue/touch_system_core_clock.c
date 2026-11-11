/* SPDX-License-Identifier: MIT
 * SystemCoreClockUpdate for touch when system_cat2.c is not linked
 * (delay globals already live in reset_data.c).
 */
#include <stdint.h>
/* W14: stock reset-copy word RAM 0x20000878 (flash 0xb944) = 0x016e3600 = 24 MHz;
 * matches reset_owned_data.c and the 24 MHz delay globals. Was 48000000u (no evidence). */
uint32_t SystemCoreClock = 24000000u;
extern uint32_t Cy_SysClk_ClkHfGetFrequency(void);
extern uint32_t cy_delay32kMs;
extern uint8_t cy_delayFreqMhz;
extern uint32_t cy_delayFreqKhz;

/* W15 evidence: stock 0x4734..0x4768 (/tmp/touch.s disasm):
 *   f = bl 0x46f8 (HFCLK freq: IMO freq 0x9f9c with CLK_SELECT divider rounding,
 *       i.e. Cy_SysClk_ClkHfGetFrequency specialised for IMO source);
 *   if (f) { [0x20000878] = f; t = f - 1;
 *            strb [0x20000870] = t / 0xf4240 + 1;  (__udivsi3 0xa6c0)
 *            [0x20000874] = t / 1000 + 1;  [0x2000086c] = khz << 15; }
 * = mtb-pdl-cat2 system_cat2.c SystemCoreClockUpdate (CY_SYSLIB_DIV_ROUNDUP, CY_DELAY_MS_OVERFLOW 0x8000). */
void SystemCoreClockUpdate(void)
{
    uint32_t locHf = Cy_SysClk_ClkHfGetFrequency();
    if (locHf != 0u) {
        SystemCoreClock = locHf;
        cy_delayFreqMhz = (uint8_t)((locHf - 1u) / 1000000u + 1u);
        cy_delayFreqKhz = (locHf - 1u) / 1000u + 1u;
        cy_delay32kMs = cy_delayFreqKhz * 0x8000u;
    }
}
