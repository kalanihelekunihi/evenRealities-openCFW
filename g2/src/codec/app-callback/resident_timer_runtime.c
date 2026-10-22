/* SPDX-License-Identifier: MIT
 * Image-A SRAM native timer runtime: dispatch 0x100258c4, microsecond
 * delay 0x10025944, and millisecond delay 0x1002598c.
 */
#include <stdint.h>

extern uint64_t gx8002_resident_clock_time_us_2585c(void);

typedef void (*gx8002_timer_callback)(uint32_t);
struct gx8002_timer_record {
    uint32_t callback;
    uint32_t context;
    uint32_t interval_ms;
    uint32_t last_low;
    uint32_t last_high;
    uint32_t deadline_low;
    uint32_t deadline_high;
    uint32_t enabled;
    uint32_t repeat;
};
_Static_assert(sizeof(struct gx8002_timer_record) == 36,
               "native timer record ABI");

/* Stock 0x100258C4 (gx8002_timer_dispatch) */
uint32_t gx8002_resident_timer_dispatch_258c4(void)
{
    volatile struct gx8002_timer_record *const records =
        (volatile struct gx8002_timer_record *)(uintptr_t)
        UINT32_C(0x20026d84);
    for (uint32_t i = 0; i != 10u; ++i) {
        volatile struct gx8002_timer_record *const rec = &records[i];
        if (rec->enabled == 0u) continue;
        uint64_t now = gx8002_resident_clock_time_us_2585c();
        uint32_t low = (uint32_t)now;
        uint32_t high = (uint32_t)(now >> 32);
        if (high < rec->deadline_high ||
            (high == rec->deadline_high && low < rec->deadline_low))
            continue;
        gx8002_timer_callback callback =
            (gx8002_timer_callback)(uintptr_t)rec->callback;
        callback(rec->context);
        uint32_t interval_word = rec->interval_ms * 1000u;
        int64_t signed_interval = (int32_t)interval_word;
        uint64_t next = now + (uint64_t)signed_interval;
        uint32_t repeat = rec->repeat;
        rec->last_low = low;
        rec->last_high = high;
        rec->deadline_low = (uint32_t)next;
        rec->deadline_high = (uint32_t)(next >> 32);
        if (repeat == 0u) rec->enabled = 0u;
    }
    volatile uint32_t *const irq =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0400000);
    *irq |= 1u;
    return 0u;
}

/* Stock 0x10025944 (gx8002_delay_us) */
void gx8002_resident_delay_us_25944(uint32_t duration)
{
    uint64_t target = gx8002_resident_clock_time_us_2585c() +
                      (uint64_t)duration + 1u;
    while (gx8002_resident_clock_time_us_2585c() < target) {
        volatile uint32_t spins = 50u;
        do { --spins; } while (spins != 0u);
    }
}

/* Stock 0x1002598C (gx8002_delay_ms) */
void gx8002_resident_delay_ms_2598c(uint32_t duration)
{
    gx8002_resident_delay_us_25944(duration * 1000u);
}
