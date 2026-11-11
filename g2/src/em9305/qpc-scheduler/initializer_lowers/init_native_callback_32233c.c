#include <stdint.h>

/* Native 0x32233c..0x322582: periodic-advertising sync event-end callback
 * (owner). A pending sync-lost (+3, reason 5) or terminate (+2: 326108
 * reason 3, stop timer +700) ends the event. Otherwise it reports a sync
 * timeout (reason 3) when +5 is clear and the event counter (+248) is
 * 5 (6 with +8) past the last received event (+278), latches a received
 * AUX_SYNC (0x803d71: anchor 0x803d74 -> +272, restart the supervision
 * timer, derive the skip step +616 or limit / interval), works out the
 * missed events and the sub-event channel position, optionally reports
 * the window widening (0x805bee, 30e89c), then for each scheduled event:
 * notifies the three periodic-advertising slots (+312, +408, +504;
 * 324904), advances the channel position (+18 of the report at +780,
 * wrapping to a new event every +512 sub-events), recomputes anchor (+8),
 * window (+12) and widening (+204) and the channel seed (+97), and
 * reinserts the schedule node, retrying until the insert succeeds.
 * The stock body accumulates the anchor offsets with mpywhul / macwhul /
 * macwhl in the DSP accumulator; only the low 32 bits are used, which is
 * what the plain 32-bit products and sums below compute (16-bit operands
 * truncated as the halfword forms do). */
#define U8(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define U16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define U32(a) (*(volatile uint32_t *)(uintptr_t)(a))

struct periodic_slot_event {
    uint16_t event;
    uint16_t window;
    uint8_t kind;
    uint8_t reserved;
    uint16_t slot;
};

extern uint32_t opencfw_em9305_init_secondary_message_325d50(uintptr_t record, uint32_t reason);
extern uint32_t opencfw_em9305_child_326108(uintptr_t record, uint32_t value);
extern uint32_t opencfw_em9305_wsf_timer_stop(uintptr_t timer);
extern uint32_t opencfw_em9305_wsf_timer_start_ms(uintptr_t timer, uint32_t milliseconds);
extern uint32_t opencfw_em9305_mode_callback_child_317ea4(uint32_t selector);
extern uint32_t opencfw_em9305_init_secondary_time_317ebc(uint32_t, uint32_t);
extern uint32_t opencfw_em9305_associated_report_30e89c(uint32_t, uint32_t, uint32_t, uint32_t,
                                                        uint32_t);
extern void opencfw_em9305_child_324904(uintptr_t event);
extern uint32_t opencfw_em9305_associated_channel_seed_324c98(uintptr_t, uint32_t);
extern uint32_t opencfw_em9305_associated_schedule_insert_312da4(uintptr_t, uintptr_t);
extern uintptr_t opencfw_em9305_init_secondary_compare_3249e8(uintptr_t, uintptr_t);

#define SYNC_TABLE 0x803d78u /* 784-byte sync records */

uint32_t opencfw_em9305_callback_32233c(uintptr_t owner)
{
    uintptr_t link = U32(owner + 36u);
    if (U8(link + 3u) != 0u) {
        U8(link + 3u) = 0u;
        return opencfw_em9305_init_secondary_message_325d50(link, 5u);
    }
    if (U8(link + 2u) != 0u) {
        U8(link + 2u) = 0u;
        (void)opencfw_em9305_child_326108(link, 3u);
        return opencfw_em9305_wsf_timer_stop(link + 700u);
    }
    if (U8(link + 5u) == 0u) {
        uint32_t limit = (U8(link + 8u) != 0u) + 5u;
        uint32_t last = U16(link + 278u);
        if ((uint32_t)U16(link + 248u) - last == limit)
            (void)opencfw_em9305_init_secondary_message_325d50(link, 3u);
    }

    uint32_t step = 1u;
    uint32_t wraps = 0u;
    U8(link + 8u) = 0u;
    if (U8(0x803d71u) != 0u) {
        uintptr_t report = U32(link + 780u);
        uint32_t anchor = U32(0x803d74u);
        U8(0x803d71u) = 0u;
        uint32_t event = U16(link + 248u);
        uint32_t channel = U8(report + 18u);
        uint32_t timeout = U32(link + 620u);
        U32(link + 272u) = anchor;
        U16(report + 364u) = (uint16_t)channel;
        U16(link + 276u) = (uint16_t)event;
        (void)opencfw_em9305_wsf_timer_start_ms(link + 700u, timeout);
        uint32_t window = U32(link + 260u);
        if (window != 0u) {
            uint32_t limit = U32(link + 620u) * 1000u;
            if (window < limit) {
                step = U16(link + 616u);
            } else {
                uint32_t interval = U32(link + 252u);
                if (interval != 0u)
                    step = limit / interval;
            }
        }
    }

    uint32_t last = U16(link + 276u);
    uint32_t event = U16(link + 248u);
    uintptr_t report = U32(link + 780u);
    uint32_t per_event = U8(link + 512u);
    int32_t gap = (int32_t)(event - last);
    uint32_t lost = gap <= 1 ? 0u : (uint32_t)gap - 1u;
    uint32_t first = U16(report + 364u);
    uint32_t position = U8(report + 18u);
    if (event == last) {
        position -= first;
    } else {
        position += per_event - first;
        wraps = 1u;
    }

    uint32_t spacing = U8(link + 513u) * 1250u;
    uint32_t interval = U32(link + 252u);
    uint32_t remainder = interval - spacing * per_event;
    uint32_t index;
    if (U8(0x805beeu) != 0u) {
        uint32_t offset = interval * (uint16_t)lost + spacing * (uint16_t)position +
                          remainder * (uint32_t)(int32_t)(int16_t)wraps;
        uint32_t widening = opencfw_em9305_init_secondary_time_317ebc(
            offset, opencfw_em9305_mode_callback_child_317ea4(U8(link + 256u)));
        index = (uint32_t)((int32_t)(link - SYNC_TABLE) / 784);
        (void)opencfw_em9305_associated_report_30e89c((uint8_t)index, U16(link + 248u),
                                                      (uint16_t)widening, U32(link + 252u),
                                                      U32(owner + 8u));
    } else {
        index = (uint32_t)((int32_t)(link - SYNC_TABLE) / 784);
    }

    struct periodic_slot_event slot_event;
    uint32_t stride = step - 1u;
    uint32_t insert;
    do {
        slot_event.slot = (uint8_t)index;
        slot_event.window = (uint16_t)step;
        slot_event.event = U16(link + 248u);
        for (uint32_t i = 0u; i < 3u; i++) {
            if (U8(link + 312u + 96u * i) != 0u) {
                slot_event.kind = (uint8_t)i;
                opencfw_em9305_child_324904((uintptr_t)&slot_event);
            }
        }
        report = U32(link + 780u);
        uint32_t channel = U8(report + 18u) + 1u;
        U8(report + 18u) = (uint8_t)channel;
        if ((channel & 0x7fu) == U8(link + 512u)) {
            uint32_t counter = U16(link + 248u);
            U8(report + 18u) = 0u;
            wraps += 1u;
            U16(link + 248u) = (uint16_t)(counter + step);
            lost += stride;
        }
        position += 1u;
        uint32_t offset = U8(link + 513u) * (uint16_t)position * 1250u +
                          (wraps * remainder + U32(link + 252u) * (uint16_t)lost);
        uint32_t widening = opencfw_em9305_init_secondary_time_317ebc(
            offset, opencfw_em9305_mode_callback_child_317ea4(U8(link + 256u)));
        report = U32(link + 780u);
        uint32_t period = U32(link + 252u);
        uint32_t window_base = U32(link + 264u);
        uint32_t widening_base = U32(link + 268u);
        uint32_t anchor = U32(link + 272u);
        uint32_t counter = U16(link + 248u);
        U32(owner + 20u) = period;
        uint32_t channel_now = U8(report + 18u);
        U32(owner + 8u) = anchor + (offset - widening);
        U32(owner + 12u) = window_base + widening;
        U32(link + 204u) = widening_base + (widening << 1);
        U8(link + 97u) = (uint8_t)opencfw_em9305_associated_channel_seed_324c98(
            link + 644u, counter ^ channel_now);
        insert = opencfw_em9305_associated_schedule_insert_312da4(
            owner, (uintptr_t)opencfw_em9305_init_secondary_compare_3249e8);
    } while (insert == 0u);
    return insert;
}
