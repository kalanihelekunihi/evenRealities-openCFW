#ifndef OPENCFW_BOOTLOADER_CLOCK_CLASS_PROVIDER6_H
#define OPENCFW_BOOTLOADER_CLOCK_CLASS_PROVIDER6_H

#include <stdint.h>

uint32_t opencfw_bl_clock_request_id6(uint8_t user_id);
uint32_t opencfw_bl_clock_release_id6(uint8_t user_id);

void opencfw_boot_syspll_power_initialize_for_clockmux(void);
void opencfw_boot_syspll_power_restore_for_clockmux(void);

#endif
