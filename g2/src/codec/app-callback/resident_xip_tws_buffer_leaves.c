/* SPDX-License-Identifier: MIT
 * Image-A XIP connected TWS/CTC leaves. Literal target pointers come from
 * the authenticated XIP image based at 0x10203004; C remains relocatable.
 */
#include <stdint.h>

void *gx8002_xip_tws_buffer_10206ea4(void)
{
    return (void *)(uintptr_t)UINT32_C(0x20030000);
}

void *gx8002_xip_tws_frame_10206eac(void *context, uint32_t sequence)
{
    uint8_t *const record = (uint8_t *)context;
    uint8_t *const header = *(uint8_t **)(void *)record;
    uint32_t index = *(uint32_t *)(void *)(header + 0x24u) * sequence;
    uint32_t modulus = *(uint32_t *)(void *)(header + 0x30u);
    uint32_t frame = index % modulus;
    uint32_t bytes = *(uint32_t *)(void *)(header + 0x6cu);
    uint32_t base = *(uint32_t *)(void *)(header + 0x70u);
    return (void *)(uintptr_t)(base + frame * bytes * 2u);
}

uint32_t gx8002_xip_tws_frame_count_10206f50(void)
{
    volatile uint32_t *const header =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20027b60);
    return header[0x24u / 4u];
}

uint32_t gx8002_xip_tws_frames_per_channel_10206f74(void)
{
    volatile const uint8_t *const header =
        (volatile const uint8_t *)(uintptr_t)UINT32_C(0x20027b60);
    return *(volatile const uint32_t *)(const void *)(header + 0x30u);
}

uint32_t gx8002_xip_tws_context_gap_10206f80(void)
{
    return 1u;
}

uint32_t gx8002_xip_tws_context_count_10206f84(void)
{
    volatile const uint8_t *const header =
        (volatile const uint8_t *)(uintptr_t)UINT32_C(0x20027b60);
    return *(volatile const uint32_t *)(const void *)(header + 0x3cu);
}

uint32_t gx8002_xip_tws_event_init_10208c28(uint32_t *event)
{
    const volatile uint32_t *const model =
        (const volatile uint32_t *)(uintptr_t)UINT32_C(0x2002e85c);
    event[0] = 0x100u;
    event[5] = model[0x14u / 4u] & UINT32_C(0x07ffffff);
    event[7] = model[0x1cu / 4u] & UINT32_C(0x07ffffff);
    event[1] = model[4u / 4u] & UINT32_C(0x07ffffff);
    uint32_t field18 = model[0x18u / 4u];
    event[2] = model[8u / 4u] & UINT32_C(0x07ffffff);
    event[6] = field18 & UINT32_C(0x07ffffff);
    return 0u;
}

uint32_t gx8002_xip_tws_event_pointer_10208c68(void *address)
{
    return (uint32_t)(uintptr_t)address;
}

uint32_t gx8002_xip_tws_next_pointer_10208c6c(void *address)
{
    return (uint32_t)(uintptr_t)address + 0x410u;
}

uint32_t gx8002_xip_tws_event_length_10208c74(void)
{
    return 0x208u;
}
