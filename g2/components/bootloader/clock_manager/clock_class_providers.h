#ifndef OPENCFW_BOOTLOADER_CLOCK_CLASS_PROVIDERS_H
#define OPENCFW_BOOTLOADER_CLOCK_CLASS_PROVIDERS_H

#include <stdint.h>

uint32_t opencfw_bl_clock_request_id1(uint8_t user_id);
uint32_t opencfw_bl_clock_release_id1(uint8_t user_id);
uint32_t opencfw_bl_clock_request_id3(uint8_t user_id);
uint32_t opencfw_bl_clock_release_id3(uint8_t user_id);

/* Recovered lower helper at stock 0x0041d92c. */
uint32_t opencfw_bl_power_register_update(uint32_t register_id,
                                          uint32_t value);

#endif
