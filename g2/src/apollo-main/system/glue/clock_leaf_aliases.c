/* Two callback names target the authenticated Apollo clock leaf entries.
 * Keep each at the same source function, without adding a wrapper call. */
#include "../../hal/clock/clock/clock-leaf-providers/providers.c"

__asm__(".global stock_pll_power_enabled\n"
        ".set stock_pll_power_enabled, audio_pll_power_enabled\n"
        ".global stock_hfrc_target\n"
        ".set stock_hfrc_target, audio_hfrc_target\n"
        ".global stock_hfrc_force\n"
        ".set stock_hfrc_force, audio_hfrc_force\n"
        ".global stock_hfrc_disable\n"
        ".set stock_hfrc_disable, audio_hfrc_disable\n"
        ".global stock_hfrc2_force\n"
        ".set stock_hfrc2_force, audio_hfrc2_force\n"
        ".global stock_pll_power_enable\n"
        ".set stock_pll_power_enable, audio_pll_power_enable\n"
        ".global stock_pll_power_disable\n"
        ".set stock_pll_power_disable, audio_pll_power_disable\n"
        ".global stock_syspll_enable\n.set stock_syspll_enable, audio_pll_power_enable\n"
        ".global stock_syspll_disable\n.set stock_syspll_disable, audio_pll_power_disable\n"
        ".global stock_hfrc2_ratio\n.set stock_hfrc2_ratio, audio_hfrc2_ratio\n");
