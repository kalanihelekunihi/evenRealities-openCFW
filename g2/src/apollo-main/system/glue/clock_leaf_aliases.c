/* Two callback names target the authenticated Apollo clock leaf entries.
 * Keep each at the same source function, without adding a wrapper call.
 * stock_hfrc_target/force/disable, stock_hfrc2_force and stock_hfrc2_ratio
 * are am_hal_clkgen (AmbiqSuite 5.1.0) entries, bound by payload defsym. */
#include "../../hal/clock/clock/clock-leaf-providers/providers.c"

/* The stock_pll_power_* / stock_syspll_* names formerly set here are bound to
 * the AmbiqSuite 5.1.0 am_hal_pwrctrl_syspll_* functions by payload defsym. */
