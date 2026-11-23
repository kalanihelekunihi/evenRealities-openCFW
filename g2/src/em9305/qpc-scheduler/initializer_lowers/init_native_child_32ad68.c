#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x32ad68..0x32ae3c: schedule the next periodic-sync receive window.
 * A fully enabled sync (flags +0x20 & 0x1d) with time left (+0x2c) advances
 * the anchor (context +8) by the interval (+0x28) until the scheduler
 * accepts a slot or the timeout runs out, which reports status 0x3c (+826,
 * event 4). Otherwise the window is twice the skew (context +0xc, plus +2480
 * when +2785 is set) but at least +0x24; a pending re-insert (+2787) takes
 * priority, and with feature bit 1 of ((uintptr_t)&em9305_ram_805a6c + 0x1fu) the anchor gets a random
 * 625 us jitter before the window is scheduled. */
extern uint32_t opencfw_em9305_init_schedule_latest_3130d4(uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_auxiliary_elapsed_303f8c(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_child_325a40(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_auxiliary_insert_313220(uintptr_t);
extern uint32_t opencfw_em9305_init_transition_random_317afc(void);
extern uint32_t opencfw_em9305_init_schedule_adjust_312f88(uintptr_t,uint32_t,uint32_t);

void opencfw_em9305_child_32ad68(uintptr_t context)
{
    uintptr_t sync = *(volatile uint32_t *)(context + 0x24u);
    volatile uint32_t *anchor = (volatile uint32_t *)(context + 8u);
    if ((*(volatile uint16_t *)(sync + 0x20u) & 0x1du) == 0x1du) {
        uint32_t remaining = *(volatile uint32_t *)(sync + 0x2cu);
        if (remaining != 0u) {
            uint32_t start = *anchor;
            uint32_t interval = *(volatile uint32_t *)(sync + 40u);
            for (;;) {
                uint32_t accepted = opencfw_em9305_init_schedule_latest_3130d4(
                    context, *(volatile uint32_t *)(sync + 0x24u), interval);
                uint32_t time = *anchor;
                if (accepted != 0u) {
                    uint32_t elapsed = opencfw_em9305_auxiliary_elapsed_303f8c(time, start);
                    uint32_t left = remaining - elapsed;
                    if (elapsed + *(volatile uint32_t *)(sync + 0x28u) >= remaining) left = 0u;
                    *(volatile uint32_t *)(sync + 0x2cu) = left;
                    return;
                }
                time += *(volatile uint32_t *)(sync + 0x28u);
                *anchor = time;
                uint32_t elapsed = opencfw_em9305_auxiliary_elapsed_303f8c(time, start);
                interval = *(volatile uint32_t *)(sync + 0x28u);
                uint32_t left = remaining - elapsed;
                if (elapsed + interval >= remaining) left = 0u;
                *(volatile uint32_t *)(sync + 0x2cu) = left;
                if (left == 0u) break;
            }
        }
        *(volatile uint8_t *)(sync + 826u) = 0x3cu;
        (void)opencfw_em9305_child_325a40(sync, 4u);
        return;
    }
    uint32_t skew_flag = *(volatile uint8_t *)(sync + 0xae1u);
    uint32_t skew = *(volatile uint32_t *)(context + 0xcu);
    if (skew_flag != 0u) skew += *(volatile uint32_t *)(sync + 0x9b0u);
    uint32_t window = *(volatile uint32_t *)(sync + 0x24u);
    skew <<= 1;
    volatile uint8_t *reinsert = (volatile uint8_t *)(sync + 0xae3u);
    if (skew > window) window = skew;
    if (*reinsert != 0u) {
        *reinsert = 0u;
        (void)opencfw_em9305_auxiliary_insert_313220(context);
        return;
    }
    if ((em9305_ram_805a6c.u8_805a8b & 2u) != 0u) {
        uint32_t jitter = opencfw_em9305_init_transition_random_317afc();
        *anchor = jitter * 625u + *anchor;
    }
    (void)opencfw_em9305_init_schedule_adjust_312f88(context, window, 0x80000000u);
}
