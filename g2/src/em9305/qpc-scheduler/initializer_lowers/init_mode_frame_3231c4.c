#include <stdint.h>

/* Native 0x3231c4..0x32323e: report LL event 6 (reason byte +12, or 22 when
 * flag +636 bit 0 is set) for a 912-byte connection entry. When the optional
 * filter hook at 0x8028c4 accepts the connection index, the 10-byte event
 * is parked at +800 with +798 set instead of being reported. No event is
 * produced when the reason is 255. */
extern void *opencfw_em9305_memcpy(void *destination, const void *source, uint32_t bytes);
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);

struct ll_event_6 {
    uint16_t handle;
    uint16_t code;
    uint8_t zero;
    uint8_t reserved;
    uint16_t handle_again;
    uint8_t reason;
} __attribute__((aligned(4)));

uint32_t opencfw_em9305_mode_event_3231c4(uintptr_t context)
{
    struct ll_event_6 event;
    uint32_t reason = *(volatile uint8_t *)(context + 12u);
    if (reason == 255u) return (uint32_t)context;
    uintptr_t base = *(volatile uint32_t *)(uintptr_t)0x805c70u;
    event.reason = (uint8_t)reason;
    uint32_t flags = *(volatile uint8_t *)(context + 636u);
    event.zero = 0u;
    event.code = 6u;
    uint8_t index = (uint8_t)((int32_t)(context - base) / 912);
    event.handle_again = index;
    event.handle = index;
    if ((flags & 1u) != 0u) event.reason = 22u;
    uintptr_t hook = *(volatile uint32_t *)(uintptr_t)0x8028c4u;
    if (hook != 0u && ((uint32_t (*)(uint32_t, uintptr_t))hook)(index, hook) != 0u) {
        void *parked = opencfw_em9305_memcpy((void *)(context + 800u), &event, 10u);
        *(volatile uint8_t *)(context + 798u) = 1u;
        return (uint32_t)(uintptr_t)parked;
    }
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)&event);
}
