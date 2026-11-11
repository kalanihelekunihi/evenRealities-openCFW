#include <stdint.h>

/* Native 0x320354..0x3203ee: reschedule a link's next connection event.
 * Store the scan-time deadline (now + 1228) at +256 and the previous anchor
 * (+0x5c) at +252. While a latency window is open (+0x14 != +0x16) and the
 * accumulated delay (session +164) still fits in it (+0x16 * 625 us), try to
 * keep the slot. Otherwise clear the delay, hop the channel (session +1,
 * mask +151) and either re-insert the node (+244) or step the anchor by the
 * interval (+0x14 * 625 us) until the schedule accepts it. The elapsed time
 * since the anchor becomes the new session delay. */
extern uint32_t opencfw_em9305_scan_current_303f80(void);
extern uint32_t opencfw_em9305_init_schedule_adjust_312f88(uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_auxiliary_elapsed_303f8c(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_init_channel_next_325720(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_auxiliary_insert_313220(uintptr_t);

uint32_t opencfw_em9305_child_320354(uintptr_t link)
{
    volatile uint32_t *previous = (volatile uint32_t *)(link + 252u);
    volatile uint32_t *anchor = (volatile uint32_t *)(link + 0x5cu);
    uintptr_t session = *(volatile uint32_t *)(link + 288u);
    uintptr_t node = link + 244u;
    uint32_t now = opencfw_em9305_scan_current_303f80();
    uint32_t window = *(volatile uint16_t *)(link + 0x16u);
    uint32_t interval = *(volatile uint16_t *)(link + 0x14u);
    uint32_t last = *anchor;
    *(volatile uint32_t *)(link + 256u) = now + 1228u;
    *previous = last;
    if (interval != window) {
        uint32_t delay = *(volatile uint32_t *)(session + 164u);
        uint32_t limit = window * 625u;
        if (now + 1228u + delay < limit &&
            opencfw_em9305_init_schedule_adjust_312f88(node, delay, limit) != 0u) {
            uint32_t elapsed = opencfw_em9305_auxiliary_elapsed_303f8c(*previous, *anchor);
            *(volatile uint32_t *)(session + 164u) = elapsed;
            return elapsed;
        }
    }
    uint32_t mask = *(volatile uint8_t *)(session + 151u);
    *(volatile uint32_t *)(session + 164u) = 0u;
    *(volatile uint8_t *)(session + 1u) =
        (uint8_t)opencfw_em9305_init_channel_next_325720(*(volatile uint8_t *)(session + 1u), mask);
    window = *(volatile uint16_t *)(link + 0x16u);
    interval = *(volatile uint16_t *)(link + 0x14u);
    if (interval == window) {
        (void)opencfw_em9305_auxiliary_insert_313220(node);
        uint32_t value = *previous;
        *anchor = value;
        return value;
    }
    uint32_t step = interval * 625u;
    uint32_t span = window * 625u + step;
    uint32_t time = *previous;
    for (;;) {
        time += step;
        *anchor = time;
        uint32_t accepted = opencfw_em9305_init_schedule_adjust_312f88(node, step, span);
        time = *anchor;
        if (accepted != 0u) {
            uint32_t elapsed = opencfw_em9305_auxiliary_elapsed_303f8c(*previous, time);
            *(volatile uint32_t *)(session + 164u) = elapsed;
            return elapsed;
        }
        *previous = time;
    }
}
