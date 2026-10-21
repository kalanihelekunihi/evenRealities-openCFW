#ifndef OPENCFW_BOOTLOADER_CLOCK_CLASS_PROVIDER2_H
#define OPENCFW_BOOTLOADER_CLOCK_CLASS_PROVIDER2_H

#include <stdint.h>

uint32_t opencfw_bl_clock_request_id2(uint8_t user_id);
uint32_t opencfw_bl_clock_release_id2(uint8_t user_id);
uint32_t opencfw_bl_radio_mode_sample(uint8_t *mode);
/* Private stock ABI: status is returned in R0 and the routine's local value
 * is returned in R1 (AAPCS uint64_t). The third argument is unused; the
 * fourth seeds that local value for selectors 5, 6, and invalid selectors. */
uint64_t opencfw_bl_radio_mode_apply(uint8_t mode, const uint32_t *value,
                                     uint32_t unused, uint32_t value_seed);
void opencfw_bl_radio_callback_finish(uint32_t *timeout);

#endif
