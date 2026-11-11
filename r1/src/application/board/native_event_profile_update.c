/* Stock 0x425b0 profile-update behavior. The public two-argument event
 * callback branches here with its ambient R2/R3 fallback words intact. */
#include <stdint.h>

extern void r1_event_service_000735e0(void *, uint32_t, uint32_t, uint32_t);
extern void r1_event_service_0006c66c(const volatile uint8_t *,
                                       const volatile uint8_t *);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t, const char *, const char *, ...);
extern void nrf_log_frontend_std_3(uint32_t, const char *, uint32_t,
                                    uint32_t, uint32_t);
extern void nrf_log_frontend_std_4(uint32_t, const char *, uint32_t,
                                    uint32_t, uint32_t, uint32_t);
extern const char r1_event_text_42710[], r1_event_text_42738[];
extern const char r1_event_text_42750[], r1_event_text_42760[], r1_event_text_42778[];

static uint32_t ring_enabled(void)
{
    if (r1_structured_log_mode_get() & 1u) return 1u;
    return (r1_structured_log_mode_get() & 4u) != 0u;
}
struct __attribute__((packed,may_alias)) signed_halfword_view {
    int16_t value;
};
static int32_t signed_halfword(const volatile uint8_t *p)
{
    return ((const volatile struct signed_halfword_view *)p)->value;
}

__attribute__((noinline,used))
void r1_event_profile_update_body(uint32_t payload, uint32_t length,
                                  uint32_t fallback2, uint32_t fallback3)
{
    if (length != 12u) return;
    uint8_t previous[12];
    r1_event_service_000735e0(previous, length, fallback2, fallback3);
    const volatile uint8_t *updated=(const volatile uint8_t *)(uintptr_t)payload;

    if (ring_enabled()) {
        uint32_t b1=previous[1],b3=previous[3],b2=previous[2],b0=previous[0];
        (void)r1_structured_log_format(0x0d000000u,
            r1_event_text_42710,r1_event_text_42710,b0,b1,b2,b3);
    }
    if (r1_structured_log_mode_get() & 2u) {
        uint32_t b2=previous[2],b3=previous[3],b1=previous[1],b0=previous[0];
        nrf_log_frontend_std_4(0x001c0003u,r1_event_text_42738,b0,b1,b2,b3);
    }
    if (ring_enabled()) {
        int32_t c=signed_halfword(previous+8);
        int32_t b=signed_halfword(previous+6);
        int32_t a=signed_halfword(previous+4);
        (void)r1_structured_log_format(0x0cc00000u,
            r1_event_text_42750,r1_event_text_42750,a,b,c);
    }
    if (r1_structured_log_mode_get() & 2u) {
        int32_t c=signed_halfword(previous+8);
        int32_t b=signed_halfword(previous+6);
        int32_t a=signed_halfword(previous+4);
        nrf_log_frontend_std_3(0x001c0003u,r1_event_text_42710+20,
                               (uint32_t)a,(uint32_t)b,(uint32_t)c);
    }
    if (ring_enabled()) {
        uint32_t b1=updated[1],b3=updated[3],b2=updated[2],b0=updated[0];
        (void)r1_structured_log_format(0x0d000000u,
            r1_event_text_42760,r1_event_text_42760,b0,b1,b2,b3);
    }
    if (r1_structured_log_mode_get() & 2u) {
        uint32_t b3=updated[3],b2=updated[2],b1=updated[1],b0=updated[0];
        nrf_log_frontend_std_4(0x001c0003u,r1_event_text_42778,b0,b1,b2,b3);
    }
    if (ring_enabled()) {
        int32_t c=signed_halfword(updated+8);
        int32_t b=signed_halfword(updated+6);
        int32_t a=signed_halfword(updated+4);
        (void)r1_structured_log_format(0x0cc00000u,
            r1_event_text_42750,r1_event_text_42750,a,b,c);
    }
    if (r1_structured_log_mode_get() & 2u) {
        int32_t c=signed_halfword(updated+8);
        int32_t b=signed_halfword(updated+6);
        int32_t a=signed_halfword(updated+4);
        nrf_log_frontend_std_3(0x001c0003u,r1_event_text_42710+20,
                               (uint32_t)a,(uint32_t)b,(uint32_t)c);
    }
    r1_event_service_0006c66c(previous,updated);
}
