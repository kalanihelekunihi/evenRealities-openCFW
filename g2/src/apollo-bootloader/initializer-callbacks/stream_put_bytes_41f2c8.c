/* SPDX-License-Identifier: MIT
 * Stock 0x41f2c8..0x41f2f6 stream callback loop. Each successful byte call
 * updates the state at context+8 and increments the completed count at +0x2c.
 * The AAPCS two-register return carries original requested length in R1 and
 * zero or UINT32_MAX status in R0.
 */
#include <stdint.h>

typedef uint32_t (*opencfw_boot_stream_put_t)(uint32_t state, uint32_t byte);

uint64_t opencfw_boot_stream_put_bytes(opencfw_boot_stream_put_t put,
                                       volatile void *context,
                                       const uint8_t *bytes,
                                       uint32_t length)
{
    volatile uint8_t *const state = (volatile uint8_t *)context;
    const uint64_t high = (uint64_t)length << 32;
    for (uint32_t i = 0; i < length; ++i) {
        const uint32_t next = put(*(volatile uint32_t *)(state + 8u), bytes[i]);
        *(volatile uint32_t *)(state + 8u) = next;
        if (next == 0u)
            return high | UINT32_MAX;
        ++*(volatile uint32_t *)(state + 0x2cu);
    }
    return high;
}
