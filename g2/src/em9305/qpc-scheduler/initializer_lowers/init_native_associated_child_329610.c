#include <stdint.h>

/* Native 0x329610..0x329840: associated-link start. Clears the schedule
 * node (+16, 0xb8 bytes) and seeds the link from the current
 * configuration (0x805c6c): PHY slot count, intervals, timing words,
 * selector (+321), peer clock accuracy (304868, else +47 -> 317ea4), the
 * 30000 slot adjustment, the supervision timer (+384, 5/4 of the
 * interval rounded up), radio channel/PHY tables and limits, and the
 * anchor/window times (317ebc). Installs the associated callbacks, then
 * repeatedly picks the role from slot table 0x8027e0 (callback receives
 * the link and literal zero) and inserts the node (318b78 compare); each
 * refused insert advances the event counter (+262) by one interval. */
#define U8(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define U16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define U32(a) (*(volatile uint32_t *)(uintptr_t)(a))

extern uintptr_t opencfw_em9305_memset(uintptr_t dst, uint32_t value, uint32_t size);
extern uint32_t opencfw_em9305_associated_child_304868(void);
extern uint32_t opencfw_em9305_mode_callback_child_317ea4(uint32_t selector);
extern uint32_t opencfw_em9305_ll_slot_adjust_317c10(uintptr_t slot, uint32_t value);
extern uint32_t opencfw_em9305_wsf_timer_start_ms(uintptr_t timer, uint32_t milliseconds);
extern uint32_t opencfw_em9305_radio_channels_317ac0(uintptr_t);
extern uint32_t opencfw_em9305_radio_phy_tables_31b6cc(uintptr_t);
extern uint32_t opencfw_em9305_radio_limit_317b10(uintptr_t, uintptr_t);
extern uint32_t opencfw_em9305_init_secondary_time_317ebc(uint32_t, uint32_t);
extern uint32_t opencfw_em9305_associated_schedule_insert_312da4(uintptr_t, uintptr_t);
extern uint32_t opencfw_em9305_init_schedule_compare_318b78(uintptr_t, uintptr_t);
extern void opencfw_em9305_associated_callback_329574(void);
extern void opencfw_em9305_associated_callback_329840(void);
extern void opencfw_em9305_associated_callback_32a47c(void);
extern void opencfw_em9305_associated_callback_32a230(void);
extern void opencfw_em9305_associated_callback_329888(void);
extern void opencfw_em9305_associated_callback_329560(void);

uint32_t opencfw_em9305_associated_child_329610(uintptr_t link)
{
    uintptr_t config = U32(0x805c6cu);
    (void)opencfw_em9305_memset(link + 16u, 0u, 0xb8u);

    uint32_t slots = 1u;
    if (U8(config + 57u) != 0u)
        slots = (U8(config + 54u) == 3u) + 2u;
    slots += U16(config + 44u);
    U16(link + 202u) = 1u;
    U32(link + 280u) = U32(config + 32u);
    U32(link + 276u) = U32(config + 28u);
    uint32_t accuracy = U8(config + 47u);
    U8(link + 321u) = U8(config + 53u);
    U8(link + 271u) = U8(config + 46u);
    U16(link + 266u) = U16(config + 36u);
    uint32_t peer = opencfw_em9305_associated_child_304868();
    if (peer != 255u)
        accuracy = peer;
    U16(link + 200u) = (uint16_t)opencfw_em9305_mode_callback_child_317ea4((uint8_t)accuracy);

    U32(link + 492u) = 30000u;
    U16(link + 260u) = U16(config + 38u);
    U16(link + 382u) = (uint16_t)(U16(config + 40u) * 10u);
    uint32_t adjusted = opencfw_em9305_ll_slot_adjust_317c10(link, 30000u);

    slots = (uint16_t)slots;
    uint32_t interval = (uint32_t)U16(config + 36u) * 6u + U8(config + 42u) + slots;
    uint32_t timeout = interval + (interval >> 2) + ((interval & 3u) != 0u);
    uint32_t window = U32(config + 24u);
    U32(link + 472u) = adjusted;
    U8(link + 635u) = 0xffu;
    U32(link + 324u) = window;
    (void)opencfw_em9305_wsf_timer_start_ms(link + 384u, timeout);
    (void)opencfw_em9305_radio_channels_317ac0(link);

    uintptr_t peer_cfg = U32(0x805cacu);
    uint32_t access = U32(config + 20u);
    uintptr_t current = U32(0x805c6cu);
    U32(link + 72u) = U32(config + 24u);
    U32(link + 68u) = access;
    U8(link + 64u) = 5u;
    U16(link + 322u) = (uint16_t)(access ^ (access >> 16));
    U8(link + 66u) = U8(peer_cfg + 40u);
    uint32_t phy = U8(current + 54u);
    U8(link + 77u) = (uint8_t)phy;
    U8(link + 76u) = (uint8_t)phy;
    (void)opencfw_em9305_radio_phy_tables_31b6cc(link);

    U8(link + 336u) = 0xffu;
    U8(link + 110u) = 1u;
    U16(link + 592u) = (uint16_t)opencfw_em9305_radio_limit_317b10(link, link + 574u);
    uint32_t limit = opencfw_em9305_radio_limit_317b10(link, link + 566u);

    uint32_t base = U8(config + 42u) * 1250u;
    uint32_t extra = slots * 1250u;
    uint32_t sca = U16(link + 200u);
    U16(link + 590u) = (uint16_t)limit;
    uint32_t widening = opencfw_em9305_init_secondary_time_317ebc(base + extra, sca);

    uint32_t anchor = U32(U32(0x805c6cu) + 48u);
    uint32_t period = (uint32_t)U16(link + 266u) * 1250u;
    uint32_t t0 = U32(0x805cb4u);
    uint32_t t1 = U32(0x805cb8u);
    uint32_t start = base + (widening << 1);
    uint32_t next = start + 1u;
    uint32_t end = start + 806u;
    anchor += extra;
    uint32_t offset = anchor - widening;

    U32(link + 168u) = (uint32_t)(uintptr_t)opencfw_em9305_associated_callback_329574;
    U32(link + 172u) = (uint32_t)(uintptr_t)opencfw_em9305_associated_callback_329840;
    U32(link + 176u) = (uint32_t)(uintptr_t)opencfw_em9305_associated_callback_32a47c;
    U32(link + 180u) = (uint32_t)(uintptr_t)opencfw_em9305_associated_callback_32a230;
    U32(link + 44u) = (uint32_t)(uintptr_t)opencfw_em9305_associated_callback_329888;
    U32(link + 48u) = (uint32_t)(uintptr_t)opencfw_em9305_associated_callback_329560;
    U8(link + 42u) = 1u;
    U32(link + 60u) = link + 64u;
    U16(link + 40u) = 1u;
    U32(link + 204u) = base;
    U32(link + 164u) = next;
    U32(link + 28u) = end;
    U32(link + 52u) = link;
    U32(link + 184u) = t0;
    U32(link + 188u) = t1;
    U32(link + 36u) = period;
    U32(link + 208u) = anchor;

    for (;;) {
        U32(link + 24u) = offset;
        uintptr_t role = U32(0x8027e0u + 4u * U8(link + 321u));
        U8(link + 65u) = (uint8_t)((uint32_t (*)(uintptr_t, uint32_t))role)(link, 0u);
        uint32_t done = opencfw_em9305_associated_schedule_insert_312da4(
            link + 16u, (uintptr_t)opencfw_em9305_init_schedule_compare_318b78);
        if (done != 0u)
            return done;
        uint32_t events = (uint32_t)U16(link + 262u) + 1u;
        uint32_t step = (uint32_t)U16(link + 266u) * (uint16_t)events * 1250u;
        U16(link + 262u) = (uint16_t)events;
        uint32_t w = opencfw_em9305_init_secondary_time_317ebc(step, U16(link + 200u));
        U32(link + 28u) = w + end;
        U32(link + 164u) = next + (w << 1);
        offset = step - w + U32(link + 208u);
    }
}
