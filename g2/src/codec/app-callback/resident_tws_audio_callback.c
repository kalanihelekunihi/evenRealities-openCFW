/* SPDX-License-Identifier: MIT
 * Image-A SRAM 0x100263dc TWS audio callback, with native stack/call
 * sequence and register argument to its 0x100260e4 child preserved.
 * XIP application operations and the child remain genuine typed imports.
 */
#include <stdint.h>

extern uint32_t gx8002_xip_tws_context_10206ec8(
    uint32_t index, void **out_context, void *out_auxiliary);
extern uint32_t gx8002_xip_tws_mode_10207394(void);
extern uint32_t gx8002_xip_tws_item_10206f08(
    void *context, uint32_t index, uint32_t value);
extern uint32_t gx8002_xip_tws_commit_102075c8(void *context);
extern const uint32_t *gx8002_xip_tws_clock_10206e9c(void);
extern void gx8002_resident_tws_standby_loop_263c4(void);
extern uint32_t gx8002_resident_tws_buffer_update_260e4(void *context);
extern void gx8002_xip_tws_publish_10206c24(
    const void *buffer, uint32_t sequence, uint32_t mode,
    uint32_t channel, uint32_t reserved);
extern uint32_t gx8002_xip_tws_dispatch_10208cc0(const uint32_t *event);
extern const uint8_t gx8002_xip_tws_message_buffer_1020b250[];

static uint32_t load32(const void *base, uint32_t offset)
{
    return *(const uint32_t *)(const void *)((const uint8_t *)base + offset);
}

/* Stock 0x100263DC (gx8002_tws_audio_callback) */
uint32_t gx8002_resident_tws_audio_callback_263dc(int32_t index)
{
    if (index < 0) return 0u;
    void *context = 0;
    uint32_t auxiliary = 0;
    (void)gx8002_xip_tws_context_10206ec8(
        (uint32_t)index, &context, &auxiliary);
    uint8_t *record = (uint8_t *)context;
    *(uint32_t *)(void *)(record + 8u) = (uint32_t)index;
    record[12] &= 0x3fu;
    uint32_t mode = (uint8_t)gx8002_xip_tws_mode_10207394();
    const void *descriptor = *(const void *const *)(const void *)record;
    for (uint32_t item = 0; item < load32(descriptor, 8u); ++item)
        (void)gx8002_xip_tws_item_10206f08(context, item, 0u);
    gx8002_xip_tws_commit_102075c8(context);
    descriptor = *(const void *const *)(const void *)record;
    if (load32(descriptor, 4u) == 0u) mode = 1u;
    else {
        const uint32_t *clock = gx8002_xip_tws_clock_10206e9c();
        if (clock[0x30u / 4u] / clock[0x24u / 4u] >=
            load32(record, 8u)) mode = 1u;
    }
    record[12] = (record[12] & 0xf8u) | (uint8_t)(mode & 7u);
    gx8002_resident_tws_standby_loop_263c4();
    volatile uint8_t *const queue =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x2002e6ec);
    uint32_t current = record[12] & 7u;
    if (current != 0u) {
        *(volatile uint32_t *)(void *)(queue + 0x4cu) = 2u;
        *(volatile uint32_t *)(void *)(queue + 0x50u) = 50u;
    }
    (void)gx8002_resident_tws_buffer_update_260e4(context);
    uint32_t sequence = load32(record, 8u);
    volatile uint32_t *const previous =
        (volatile uint32_t *)(void *)(queue + 0x54u);
    if (sequence % 15u == 0u || current != *previous) {
        gx8002_xip_tws_publish_10206c24(
            gx8002_xip_tws_message_buffer_1020b250, sequence,
            current, record[14] & 7u, 0u);
        if (current != *previous) *previous = current;
    }
    uint32_t event[2] = {91u, sequence};
    (void)gx8002_xip_tws_dispatch_10208cc0(event);
    return 0u;
}
