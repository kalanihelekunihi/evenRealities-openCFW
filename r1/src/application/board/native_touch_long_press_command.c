/* Stock 0x62b4c and 0x8e880: legacy touch long-press interval command. */
#include <stdint.h>

extern volatile uint16_t r1_touch_long_press_threshold;
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t, const char *,
                                         const char *, ...);
extern void nrf_log_frontend_std_0(uint32_t, const char *);
extern void nrf_log_frontend_std_1(uint32_t, const char *, uint32_t);
extern uint32_t r1_legacy_bounded_reply_send(const void *, uint32_t);

static int ring_log_enabled(void)
{
    return (r1_structured_log_mode_get() & 1u) ||
           (r1_structured_log_mode_get() & 4u);
}

/* Stock's low-interval diagnostic says 50, though its actual clamp is 100. */
void r1_touch_long_press_clamp(uint32_t milliseconds)
{
    static const char high_ring[] =
        "[RING]touch_long_pre_time is too large, set to 1000";
    static const char high_plain[] =
        "touch_long_pre_time is too large, set to 1000";
    static const char low_ring[] =
        "[RING]touch_long_pre_time is too small, set to 50";
    static const char low_plain[] =
        "touch_long_pre_time is too small, set to 50";

    if (milliseconds > 3000u) {
        milliseconds = 1000u;
        if (ring_log_enabled())
            (void)r1_structured_log_format(0x08000000u,
                                            high_ring, high_ring);
        if (r1_structured_log_mode_get() & 2u)
            nrf_log_frontend_std_0(0x001c0002u, high_plain);
    } else if (milliseconds < 100u) {
        milliseconds = 100u;
        if (ring_log_enabled())
            (void)r1_structured_log_format(0x08000000u,
                                            low_ring, low_ring);
        if (r1_structured_log_mode_get() & 2u)
            nrf_log_frontend_std_0(0x001c0002u, low_plain);
    }
    r1_touch_long_press_threshold = (uint16_t)milliseconds;
}

uint32_t r1_touch_long_press_time_command(uint32_t handle, void *packet)
{
    (void)handle;
    static const char ring[] = "[RING]touch_long_pre_time:%d";
    static const char plain[] = "touch_long_pre_time:%d";
    uint8_t *bytes = (uint8_t *)packet;
    if (bytes[3] == 1u) {
        uint32_t milliseconds = ((uint32_t)bytes[4] << 8u) | bytes[5];
        bytes[4] = 1u;
        if (ring_log_enabled())
            (void)r1_structured_log_format(0x0c400000u,
                                            ring, ring, milliseconds);
        if (r1_structured_log_mode_get() & 2u)
            nrf_log_frontend_std_1(0x001c0003u, plain, milliseconds);
        r1_touch_long_press_clamp(milliseconds);
    }
    return r1_legacy_bounded_reply_send(packet, 7u);
}
