/* Clock callers use six validated Apollo PLL driver entries.
 * Export their caller names at the original source function offsets. */
#include "../clock_driver_config_offline/driver.c"

__asm__(".global stock_pll_init\n.set stock_pll_init, audio_pll_init\n"
        ".global stock_pll_deinit\n.set stock_pll_deinit, audio_pll_deinit\n"
        ".global stock_pll_enable\n.set stock_pll_enable, audio_pll_enable\n"
        ".global stock_pll_disable\n.set stock_pll_disable, audio_pll_disable\n"
        ".global stock_pll_config\n.set stock_pll_config, audio_pll_configure\n"
        ".global stock_pll_wait\n.set stock_pll_wait, audio_pll_wait\n");
