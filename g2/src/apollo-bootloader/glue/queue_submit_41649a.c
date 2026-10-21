/* SPDX-License-Identifier: MIT
 * Authenticated stock 0x41649a..0x4164da (64 bytes), SHA-256
 * 3da32489b13b78370fde01b22ef77515363ac2866a8baa24e444d03ae87ec0e9.
 * Its R1 return is incoming R3 on early errors and zero after queue attempt.
 * The lower 0x41937c queue routine remains an explicit source boundary.
 */
#include <stdint.h>

extern uint32_t opencfw_bl_context_guard(void);
extern uint32_t opencfw_boot_queue_submit_raw(uint32_t queue, uint32_t width,
                                              uint32_t item, uint32_t mode,
                                              uint32_t timeout);

uint64_t opencfw_provider_41649a(uint32_t queue, uint32_t item,
                                  uint32_t unused_r2, uint32_t incoming_r3)
{
    (void)unused_r2;
    if (opencfw_bl_context_guard() != 0u)
        return ((uint64_t)incoming_r3 << 32) | UINT32_C(0xfffffffa);
    if (queue == 0u || item == 0u)
        return ((uint64_t)incoming_r3 << 32) | UINT32_C(0xfffffffc);
    const uint32_t result = opencfw_boot_queue_submit_raw(queue, 4u, item, 0u, 0u);
    return result == 1u ? 0u : UINT32_C(0xfffffffd);
}
