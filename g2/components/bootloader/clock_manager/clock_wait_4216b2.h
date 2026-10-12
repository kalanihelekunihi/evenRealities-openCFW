#ifndef OPENCFW_BOOT_CLOCK_WAIT_4216B2_H
#define OPENCFW_BOOT_CLOCK_WAIT_4216B2_H

#include <stdint.h>

void opencfw_bl_clock_wait_active(volatile const uint8_t *active,
                                  uint32_t *remaining);

#endif
