#ifndef OPENCFW_BOOTLOADER_CLOCK_CLASS_PROVIDER4_H
#define OPENCFW_BOOTLOADER_CLOCK_CLASS_PROVIDER4_H

#include <stdint.h>

uint32_t opencfw_bl_clock_request_id4(uint8_t user_id);
uint32_t opencfw_bl_clock_release_id4(uint8_t user_id);
void opencfw_bl_delay_us(uint32_t microseconds);

#endif
