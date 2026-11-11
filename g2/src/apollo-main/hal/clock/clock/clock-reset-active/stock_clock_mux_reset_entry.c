/* Stock entry of am_hal_sysctrl_clkmuxrst_low_power_init 0x44b158. The stock
 * code took the GPIO15 ExtRefClk pad configuration from the caller's R5: the
 * upstream HAL (am_hal_sysctrl.c) builds that am_hal_gpio_pincfg_t on the
 * stack, sets only uFuncSel and leaves the other fields uninitialised. They
 * are 0 here, so the pad gets function 10 (REFCLK_EXT) with default settings.
 */
#include "recovery.h"
void stock_clock_mux_reset(void)
{
    clock_reset_recover(0u);
}
