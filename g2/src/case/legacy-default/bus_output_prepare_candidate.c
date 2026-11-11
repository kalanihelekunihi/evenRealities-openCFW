/* SPDX-License-Identifier: MIT
 * Stock 0x0800a2e6 output preamble: line low for 40 x 350 delay counts.
 * Calls the stock GPIO leaves and the 5-cycle-per-count delay 0x0800a794
 * as stock does (the earlier volatile stack loop ran 2.2x slow).
 */
#include <stdint.h>
extern void case_boot_gpio_a4_output(void);           /* 0x0800ba84 */
extern void case_boot_gpio_a4_high(void);             /* 0x0800bac4 */
extern void case_boot_gpio_a4_low(void);              /* 0x0800bae8 */
extern void case_boot_short_delay_a794(uint32_t count); /* 0x0800a794 */
/* Stock 0x0800A2E6 (case_pulse4_train) */
void case_bus_output_prepare(void)
{
    case_boot_gpio_a4_high();case_boot_gpio_a4_output();case_boot_gpio_a4_high();case_boot_gpio_a4_low();
    for(int32_t i=0;i<40;++i)case_boot_short_delay_a794(0x15eu);
    case_boot_gpio_a4_high();
}
