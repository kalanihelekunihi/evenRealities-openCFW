#include "../eeprom_init_offline/init.h"

/* Original reset copy loads this mutable configuration at 0x200004c0.
 * Values are independently defined by touch_factory_eeprom_configuration
 * and original app validation. This placement candidate is isolated. */
touch_eeprom_configuration touch_reset_eeprom_configuration
    __attribute__((section(".touch_init.eeprom"))) = {256u, 0u, 2u, 1u, 1u, 0u};

/* Pinned vendor system_cat2.c defines this reset value as
 * CY_CLK_SYSTEM_FREQ_HZ_DEFAULT. Later SystemInit updates are separate. */
uint32_t SystemCoreClock __attribute__((section(".touch_init.system_clock"))) = 24000000u;
