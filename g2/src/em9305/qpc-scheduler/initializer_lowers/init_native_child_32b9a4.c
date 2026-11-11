#include <stdint.h>

/* Native 0x32b9a4..0x32bb40: advance a BIG/BIS event after transmission.
 * Reset the session (+224, native 0x3246dc); a terminating group (+698)
 * is cleaned up with action 3. Otherwise refresh the session (native
 * 0x3246c0, +14 from +15 or the default 0x805bed), optionally report the
 * event (0x805bee, native 0x30e89c), then step the subevent counter (+799,
 * 7 bits, wrapping at the subevent count +788 into the event counter +376)
 * and the anchor (+800 / context +8, by the subevent spacing +792) with
 * channel selection (natives 0x327af4, 0x324c98) until the schedule accepts
 * the event; the control subevent (+0xafc +76) is flagged. After the
 * insertion, a missing payload (table at *(+1160): +0xf0c / +0x0) resets
 * the payload state and re-seeds its CRC (distinct from +64 in the low 12
 * bits); at the event boundary, when every subevent slot is still empty
 * (0xff) the group reports LL event 0x35 with the subevent count. */
extern uint32_t opencfw_em9305_init_callback_child_3246dc(uintptr_t);
extern uint32_t opencfw_em9305_init_callback_child_3246c0(uintptr_t);
extern uint32_t opencfw_em9305_associated_cleanup_3266d0(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_associated_report_30e89c(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_associated_channel_pending_327af4(uintptr_t);
extern uint32_t opencfw_em9305_associated_channel_seed_324c98(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_associated_schedule_insert_312da4(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_scan_random_30c478(void);
extern uint32_t opencfw_em9305_crc_update_304678(uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_ll_mask_count_30c414(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_child_30e858(uint32_t,uint32_t,uint32_t);

#define BIG_U8(a) (*(volatile uint8_t *)(a))
#define BIG_U16(a) (*(volatile uint16_t *)(a))
#define BIG_U32(a) (*(volatile uint32_t *)(a))

void opencfw_em9305_child_32b9a4(uintptr_t context)
{
    uintptr_t session = BIG_U32(context + 0x2cu);
    uintptr_t group = BIG_U32(context + 0x24u);
    BIG_U16(session + 224u) = 0u;
    (void)opencfw_em9305_init_callback_child_3246dc(session);
    if (BIG_U8(group + 698u) != 0u) {
        (void)opencfw_em9305_associated_cleanup_3266d0(group, 3u);
        return;
    }
    (void)opencfw_em9305_init_callback_child_3246c0(session);
    uint32_t value = BIG_U8(session + 15u);
    if (value == 0u) value = BIG_U8(0x805bedu);
    BIG_U8(session + 14u) = (uint8_t)value;
    if (BIG_U8(0x805beeu) != 0u)
        (void)opencfw_em9305_associated_report_30e89c(BIG_U8(group + 1u), BIG_U16(group + 376u), 0u,
                                                      BIG_U32(group + 700u), BIG_U32(context + 8u));
    uint32_t subevents = BIG_U8(group + 788u);
    uint32_t spacing = BIG_U32(group + 792u);
    uint32_t anchor = BIG_U32(group + 700u);
    uint32_t base = anchor - spacing * subevents;
    BIG_U32(context + 20u) = anchor;
    do {
        uint32_t next = BIG_U8(group + 799u) + 1u;
        uint32_t count = BIG_U8(group + 788u);
        BIG_U8(group + 799u) = (uint8_t)next;
        uint32_t time, step;
        if ((next & 0x7fu) == count) {
            uint32_t event = BIG_U16(group + 376u);
            uint32_t interval = BIG_U32(group + 792u);
            step = BIG_U32(context + 8u);
            BIG_U8(group + 799u) = 0u;
            time = base + interval;
            BIG_U16(group + 376u) = (uint16_t)(event + 1u);
        } else {
            step = BIG_U32(group + 792u);
            time = BIG_U32(context + 8u);
        }
        time += step;
        BIG_U32(group + 800u) = time;
        BIG_U32(context + 8u) = time;
        (void)opencfw_em9305_associated_channel_pending_327af4(group);
        uint32_t seed = opencfw_em9305_associated_channel_seed_324c98(
            group + 720u, BIG_U8(group + 799u) ^ BIG_U16(group + 376u));
        uintptr_t control = BIG_U32(group + 0xafcu);
        uint32_t subevent = BIG_U8(group + 799u) & 0x7fu;
        uint32_t control_subevent = BIG_U8(control + 76u);
        BIG_U8(group + 697u) = (uint8_t)seed;
        if (subevent == control_subevent) BIG_U8(control + 77u) = 1u;
    } while (opencfw_em9305_associated_schedule_insert_312da4(context, 0u) == 0u);
    uint32_t subevent = BIG_U8(group + 799u);
    uintptr_t payloads = BIG_U32(group + 1160u);
    uint32_t slot = BIG_U8(payloads + (subevent & 0x7fu) + 0xf0cu);
    BIG_U8(session + 261u) = 0u;
    if (slot == 255u || BIG_U8(payloads + (slot << 8)) == 0u) {
        BIG_U16(group + 1144u) = 0u;
        uint32_t crc;
        do {
            uint32_t random = opencfw_em9305_scan_random_30c478();
            crc = opencfw_em9305_crc_update_304678(random, 0u, 0u);
            BIG_U16(group + 706u) = (uint16_t)crc;
        } while (((BIG_U16(group + 64u) ^ crc) & 0xfffu) == 0u);
        subevent = BIG_U8(group + 799u);
    }
    if ((subevent & 0x7fu) != 0u) return;
    payloads = BIG_U32(group + 1160u);
    uint32_t pending = opencfw_em9305_ll_mask_count_30c414(BIG_U32(payloads + 0xf04u), BIG_U32(payloads + 0xf08u));
    uint32_t count = BIG_U8(group + 788u);
    if (pending < count) {
        payloads = BIG_U32(group + 1160u);
        count = opencfw_em9305_ll_mask_count_30c414(BIG_U32(payloads + 0xf04u), BIG_U32(payloads + 0xf08u));
    }
    if (count != 0u) {
        const volatile uint8_t *slots = (const volatile uint8_t *)(BIG_U32(group + 1160u) + 0xf0cu);
        for (uint32_t index = 0u; index < count; ++index)
            if (slots[index] != 255u) return;
    }
    uintptr_t control = BIG_U32(group + 0xafcu);
    BIG_U8(control + 78u) = 0u;
    BIG_U8(control + 79u) = (uint8_t)count;
    (void)opencfw_em9305_child_30e858(BIG_U8(group + 1u), 0u, count);
}
