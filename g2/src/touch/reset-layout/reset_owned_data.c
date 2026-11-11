/* SPDX-License-Identifier: MIT */
#include "../eeprom-init/init.h"

/* Original reset copy loads this mutable configuration at 0x200004c0.
 * Values are independently defined by touch_factory_eeprom_configuration
 * and original app validation. */
touch_eeprom_configuration touch_reset_eeprom_configuration
    __attribute__((section(".touch_init.eeprom"), used)) = {256u, 0u, 2u, 1u, 1u, 0u};
