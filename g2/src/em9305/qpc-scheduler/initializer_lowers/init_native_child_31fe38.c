#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x31fe38..0x31ff2a: schedule the next event of a stream link.
 * Remember the anchor (+4 -> +252) and the deadline (now + 1228 -> +256);
 * while a latency window is open (+8 != +10) and the accumulated delay of
 * the session (+288, +164) fits in it, keep the slot. Otherwise, unless the
 * link is paused (+3), rotate to the next stream enabled in the mask at
 * ((uintptr_t)&em9305_ram_8019e8 + 0x10u) (starting after slot 0 or 2 by link type +16, current slot in
 * ((uintptr_t)&em9305_ram_8019e8 + 0x11u), objects from the ROM table 0x3357b4) and hop its channel. Then
 * either re-insert the node (+244) or step the anchor by +8 * 625 us; the
 * first run of each stream slot is recorded in ((uintptr_t)&em9305_ram_8019e8 + 0x12u), later runs store
 * the anchor slip as the session delay. Clears +3. */
extern uint32_t opencfw_em9305_scan_current_303f80(void);
extern uint32_t opencfw_em9305_init_schedule_adjust_312f88(uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_auxiliary_elapsed_303f8c(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_init_channel_next_325720(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_auxiliary_insert_313220(uintptr_t);
extern const uintptr_t opencfw_em9305_stream_objects_3357b4[3];

void opencfw_em9305_child_31fe38(uintptr_t link)
{
    volatile uint8_t *streams = &em9305_ram_8019e8.u8_8019f8;
    uint32_t type = *(volatile uint8_t *)(link + 16u);
    uintptr_t session = *(volatile uint32_t *)(link + 288u);
    *(volatile uint32_t *)(link + 252u) = *(volatile uint32_t *)(link + 4u);
    uint32_t now = opencfw_em9305_scan_current_303f80();
    uint32_t window = *(volatile uint16_t *)(link + 10u);
    uint32_t interval = *(volatile uint16_t *)(link + 8u);
    uintptr_t node = link + 244u;
    *(volatile uint32_t *)(link + 256u) = now + 1228u;
    if (interval != window) {
        uint32_t delay = *(volatile uint32_t *)(session + 164u);
        uint32_t limit = window * 625u;
        if (now + 1228u + delay < limit &&
            opencfw_em9305_init_schedule_adjust_312f88(node, delay, limit) != 0u) {
            *(volatile uint32_t *)(session + 164u) = opencfw_em9305_auxiliary_elapsed_303f8c(
                *(volatile uint32_t *)(link + 252u), *(volatile uint32_t *)(link + 4u));
            return;
        }
    }
    uint32_t slot = type == 2u ? 2u : 0u;
    if (*(volatile uint8_t *)(link + 3u) == 0u) {
        uint32_t enabled = streams[0];
        for (uint32_t tries = 0u; tries < 3u; ++tries) {
            slot = slot + 1u;
            if ((slot & 0xffu) > 2u) slot = 0u;
            if (((enabled >> (slot & 0xffu)) & 1u) != 0u) {
                link = opencfw_em9305_stream_objects_3357b4[slot & 0xffu];
                streams[1] = (uint8_t)slot;
                node = link + 244u;
                session = *(volatile uint32_t *)(link + 288u);
                break;
            }
        }
        uint32_t mask = *(volatile uint8_t *)(session + 151u);
        *(volatile uint8_t *)(session + 1u) =
            (uint8_t)opencfw_em9305_init_channel_next_325720(*(volatile uint8_t *)(session + 1u), mask);
    }
    interval = *(volatile uint16_t *)(link + 8u);
    window = *(volatile uint16_t *)(link + 10u);
    *(volatile uint32_t *)(session + 164u) = 0u;
    if (interval == window) {
        (void)opencfw_em9305_auxiliary_insert_313220(node);
        *(volatile uint32_t *)(link + 4u) = *(volatile uint32_t *)(node + 8u);
    } else {
        uint32_t anchor = interval * 625u + *(volatile uint32_t *)(node + 8u);
        *(volatile uint32_t *)(link + 4u) = anchor;
        *(volatile uint32_t *)(node + 8u) = anchor;
        (void)opencfw_em9305_init_schedule_adjust_312f88(node, 0u, 0x80000000u);
        uint32_t seen = streams[2];
        uint32_t bit = slot & 0xffu;
        if (((seen >> bit) & 1u) != 0u)
            *(volatile uint32_t *)(session + 164u) =
                *(volatile uint32_t *)(node + 8u) - *(volatile uint32_t *)(link + 4u);
        else
            streams[2] = (uint8_t)((1u << bit) | seen);
    }
    *(volatile uint8_t *)(link + 3u) = 0u;
}
