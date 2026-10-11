/* SPDX-License-Identifier: MIT
 * Image-A XIP leaves 0x102073a0, 0x102077f8, 0x10208cc0. Their runtime
 * addresses are authenticated inline literal words in the XIP image.
 */
#include <stdint.h>

extern uint32_t g2_codec_queue_enqueue(void *queue, const void *event);

uint32_t gx8002_xip_tws_ack_102073a0(uint32_t bytes)
{
    volatile uint32_t *const read_state =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002ecb0);
    uint32_t next = read_state[0] + bytes;
    if (read_state[1] < next) return UINT32_MAX;
    read_state[0] = next;
    return 0u;
}

int32_t gx8002_xip_tws_ready_102077f8(void)
{
    return *(volatile int32_t *)(uintptr_t)UINT32_C(0x2002dfbc) != 0;
}

uint32_t gx8002_xip_tws_dispatch_10208cc0(const uint32_t *event)
{
    (void)g2_codec_queue_enqueue(
        (void *)(uintptr_t)UINT32_C(0x2002ecd8), event);
    return 0u;
}
