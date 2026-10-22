/* SPDX-License-Identifier: MIT
 * Image-A SRAM 0x100260d0 callback and 0x100260e4 buffer-update body.
 * Direct native call order and stack argument roles; XIP DSP/application
 * callees remain genuine typed external contracts.
 */
#include <stdint.h>

extern void *gx8002_xip_tws_buffer_10206ea4(void);
extern void *gx8002_xip_tws_frame_10206eac(void *context,
                                           uint32_t sequence);
extern uint32_t gx8002_xip_tws_frame_count_10206f50(void);
extern void *gx8002_xip_tws_shift_10206c44(
    void *base, void *source, uint32_t bytes);
extern void gx8002_resident_cache_invalidate_25608(
    void *address, int32_t bytes);
extern void gx8002_resident_memcpy_25738(
    void *destination, const void *source, uint32_t bytes);
extern void g2_codec_header_sync(void *address, uint32_t bytes);
extern uint32_t gx8002_xip_tws_context_10206ec8(
    uint32_t index, void **out_context, void *out_auxiliary);
extern uint32_t gx8002_xip_tws_event_init_10208c28(uint32_t *event);
extern uint32_t gx8002_xip_tws_event_pointer_10208c68(void *address);
extern uint32_t gx8002_xip_tws_next_pointer_10208c6c(void *address);
extern uint32_t gx8002_xip_tws_event_length_10208c74(void);
extern int32_t gx8002_xip_tws_submit_10205d60(
    const uint32_t *event,
    uint32_t (*callback)(uint32_t, uint32_t, uint32_t),
    void *next_context);

/* Stock 0x100260D0 (gx8002_kws_pair) */
uint32_t gx8002_resident_tws_callback_260d0(
    uint32_t arg0, uint32_t arg1, uint32_t arg2)
{
    uint32_t raw = *(volatile uint32_t *)(uintptr_t)UINT32_C(0x20027b50);
    if (raw != 0u && arg2 != 0u) {
        void (*callback)(uint32_t, uint32_t, uint32_t) =
            (void (*)(uint32_t, uint32_t, uint32_t))(uintptr_t)raw;
        callback(arg0, arg1, arg2);
    }
    return 0u;
}

uint32_t gx8002_resident_tws_buffer_update_260e4(void *context)
{
    if (context == 0) return UINT32_MAX;
    uint8_t *const record = (uint8_t *)context;
    uint8_t *const buffer = gx8002_xip_tws_buffer_10206ea4();
    uint32_t sequence = *(uint32_t *)(void *)(record + 8u);
    uint8_t *const frame = gx8002_xip_tws_frame_10206eac(
        context, sequence);
    uint32_t count = gx8002_xip_tws_frame_count_10206f50();
    uint32_t first_bytes = count * 80u;
    uint32_t remaining_bytes = (13u - count) * 80u;
    gx8002_resident_cache_invalidate_25608(frame, (int32_t)first_bytes);
    (void)gx8002_xip_tws_shift_10206c44(buffer, buffer + first_bytes,
                                         remaining_bytes);
    gx8002_resident_memcpy_25738(buffer + remaining_bytes, frame,
                                  first_bytes);
    void *destination = *(void **)(void *)(record + 0x10u);
    gx8002_resident_memcpy_25738(destination, buffer, 1040u);
    g2_codec_header_sync(destination, 1040u);

    void *current = 0;
    void *next = 0;
    uint32_t auxiliary = 0;
    (void)gx8002_xip_tws_context_10206ec8(
        sequence, &current, &auxiliary);
    (void)gx8002_xip_tws_context_10206ec8(
        sequence + 1u, &next, &auxiliary);
    uint32_t event[8];
    (void)gx8002_xip_tws_event_init_10208c28(event);
    uint32_t pointer_a = gx8002_xip_tws_event_pointer_10208c68(
        (uint8_t *)current + 0x10u);
    uint32_t pointer_b = gx8002_xip_tws_next_pointer_10208c6c(
        (uint8_t *)next + 0x10u);
    g2_codec_header_sync((void *)(uintptr_t)pointer_a,
        gx8002_xip_tws_event_length_10208c74() * 2u);
    event[3] = pointer_a & UINT32_C(0x0fffffff);
    event[4] = pointer_b & UINT32_C(0x0fffffff);
    gx8002_xip_tws_submit_10205d60(event,
        gx8002_resident_tws_callback_260d0, next);
    return 0u;
}
