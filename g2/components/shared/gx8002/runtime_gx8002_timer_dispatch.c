/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <stddef.h>

struct __attribute__((packed, aligned(4))) open_cfw_timer_slot {
    void (*callback)(void *);
    void *argument;
    uint32_t interval_ms;
    uint32_t last_low, last_high;
    uint32_t due_low, due_high;
    uint32_t active;
    uint32_t repeat;
};
_Static_assert(sizeof(struct open_cfw_timer_slot) == 36, "Recovered timer stride");
_Static_assert(offsetof(struct open_cfw_timer_slot, due_low) == 20, "Recovered deadline offset");
volatile struct open_cfw_timer_slot open_cfw_timer_slots[10]
    __attribute__((section(".bss.open_cfw_timer_slots")));
extern uint64_t open_cfw_gx8002_clock_time_us(void);

int open_cfw_gx8002_timer_dispatch(void)
{
    volatile struct open_cfw_timer_slot *slot = open_cfw_timer_slots;
    for (unsigned i = 0; i < 10; ++i, ++slot) {
        if (slot->active) {
            uint64_t now = open_cfw_gx8002_clock_time_us();
            uint32_t high = (uint32_t)(now >> 32);
            uint32_t due_high = slot->due_high;
            if (high >= due_high && (high != due_high || (uint32_t)now >= slot->due_low)) {
                slot->callback(slot->argument);
                /* Callback may change interval/repeat. Stock sign-extends the
                 * low 32-bit product before adding it to the captured time. */
                int32_t interval_us = (int32_t)(slot->interval_ms * 1000u);
                uint32_t repeat = slot->repeat;
                slot->last_low = (uint32_t)now;
                slot->last_high = high;
                uint64_t due = now + (uint64_t)(int64_t)interval_us;
                slot->due_low = (uint32_t)due;
                slot->due_high = (uint32_t)(due >> 32);
                if (!repeat) slot->active = 0;
            }
        }
    }
    *(volatile uint32_t *)0xa0400000u |= 1u;
    return 0;
}
