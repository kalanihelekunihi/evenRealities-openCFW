#ifndef OPENCFW_BOOTLOADER_CLOCK_MANAGER_H
#define OPENCFW_BOOTLOADER_CLOCK_MANAGER_H

#include <stdint.h>

/* Private bootloader dispatch ABI. Both register arguments are truncated to
 * 8 bits by the entry points before validation and clock-class selection. */
uint32_t clock_request(uint32_t clock_id_register, uint32_t user_id_register);
uint32_t clock_release(uint32_t clock_id_register, uint32_t user_id_register);

#endif
