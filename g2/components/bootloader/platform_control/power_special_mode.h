#ifndef OPENCFW_BOOT_POWER_SPECIAL_MODE_H
#define OPENCFW_BOOT_POWER_SPECIAL_MODE_H
#include <stdint.h>
/* Low byte accepts0/3. Native query selector20 guards active resource state. */
uint32_t opencfw_boot_power_special_mode(uint32_t mode);
uint32_t opencfw_boot_power_special_hook(uint32_t operation,uint32_t mode);
#endif
