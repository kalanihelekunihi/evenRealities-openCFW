#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x317ca8..0x317ea4: connection subrating bookkeeping, returns the
 * number of connection events that may be skipped. The subrate block lives
 * at +846: factor +0, base event +2, latency +4, timeout +6, counter +8,
 * pending factor/base/latency +30/+32/+34, continuation counter +36,
 * continuation +38, timeout +40, update flag +42. An active pending update
 * (no host hold +378) is applied, restarting the supervision timer (+384,
 * timeout * 10 ms); a flagged change (+636 bit 29) is reported through
 * native 0x3234c4. With subrating enabled (+11 bit 6) the skip count is the
 * distance to the next subrated anchor (with 16-bit event counter wrap
 * correction of the base event), limited by the latency/continuation rules
 * of the current and pending parameters and by a pending procedure instant
 * (+635 kind 1/0x15/0x11 at +716/+724/+682). */
extern uint32_t opencfw_em9305_wsf_timer_start_ms(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_child_3234c4(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);

#define SR_U8(a) (*(volatile uint8_t *)(a))
#define SR_U16(a) (*(volatile uint16_t *)(a))
#define SR_U32(a) (*(volatile uint32_t *)(a))

static int32_t subrate_min_signed(int32_t a, int32_t b) { return a < b ? a : b; }

uint32_t opencfw_em9305_callback_317ca8(uintptr_t record, uint32_t continuing, uint32_t active)
{
    uintptr_t block = record + 846u;
    uint32_t skip_from_update = 1u;
    if (SR_U8(block + 42u) != 0u) {
        skip_from_update = 0u;
        if (SR_U8(record + 378u) == 0u && active != 0u) {
            uint32_t latency = SR_U16(block + 34u);
            uint32_t timeout = SR_U16(block + 40u);
            uint32_t factor = SR_U16(block + 30u);
            SR_U16(block + 4u) = (uint16_t)latency;
            uint32_t supervision = timeout * 10u;
            uint32_t base = SR_U16(block + 32u);
            uint32_t continuation = SR_U16(block + 38u);
            SR_U16(block + 6u) = (uint16_t)timeout;
            SR_U16(record + 382u) = (uint16_t)supervision;
            SR_U8(block + 42u) = 0u;
            SR_U16(block + 0u) = (uint16_t)factor;
            SR_U16(block + 2u) = (uint16_t)base;
            SR_U16(record + 260u) = (uint16_t)continuation;
            (void)opencfw_em9305_wsf_timer_start_ms(record + 384u, (uint16_t)supervision);
            skip_from_update = SR_U8(block + 42u) == 0u;
        }
    }
    if (skip_from_update != 0u) {
        uint32_t flags = SR_U32(record + 636u);
        if ((flags & (1u << 29)) != 0u && active != 0u) {
            uintptr_t table = SR_U32(((uintptr_t)&em9305_ram_805c5c + 0x14u));
            uint32_t timeout = SR_U16(block + 6u);
            uint32_t latency = SR_U16(block + 4u);
            int32_t index = (int32_t)(record - table) / 912;
            uint32_t factor = SR_U16(block + 0u);
            uint32_t continuation = SR_U16(record + 260u);
            SR_U32(record + 636u) = flags & ~(1u << 29);
            SR_U32(record + 640u) = 0u;
            (void)opencfw_em9305_child_3234c4((uint8_t)index, factor, continuation, latency, timeout);
        }
    }
    uint32_t factor = SR_U16(block + 0u);
    if (factor < 2u && SR_U16(block + 30u) < 2u) return 0u;
    if ((SR_U8(record + 11u) & 0x40u) == 0u) return 0u;
    uint32_t counter = SR_U16(record + 262u);
    uint32_t base = SR_U16(block + 2u);
    uint32_t next = counter + 1u;
    int32_t phase = (int32_t)(int16_t)(next - base) % (int32_t)factor;
    uint32_t aligned = (uint16_t)(counter - base) % factor;
    if ((int32_t)(int16_t)(next - base) < 0) phase = -phase;
    uint32_t offset = (uint16_t)phase;
    uint32_t event = (uint16_t)next;
    uint32_t skip = event > base ? factor - offset : offset;
    if ((base & 0xc000u) == 0xc000u && (counter & 0xc000u) == 0u) {
        uint32_t span = counter - base + factor - 1u;
        SR_U16(block + 2u) = (uint16_t)(span - span % factor + base);
    }
    uint32_t boundary = aligned | continuing;
    uint32_t result;
    if (boundary == 0u) {
        skip = factor - 1u;
        SR_U16(block + 8u) = 0u;
    }
    if (offset == 0u && boundary != 0u) {
        result = 0u;
        SR_U16(block + 8u) = 0u;
    } else {
        result = skip;
        if (boundary != 0u) {
            if (continuing != 0u) SR_U16(block + 8u) = 0u;
            uint32_t update = SR_U8(block + 42u);
            uint32_t check_pending = 1u;
            if (update == 0u || SR_U16(block + 34u) != 0u) {
                uint32_t count = SR_U16(block + 8u);
                uint32_t latency = SR_U16(block + 4u);
                SR_U16(block + 8u) = (uint16_t)(count + 1u);
                if (count < latency) {
                    result = 0u;
                    check_pending = 0u;
                } else if (update == 0u) {
                    check_pending = 0u;
                }
            }
            if (check_pending != 0u) {
                uint32_t new_base = SR_U16(block + 32u);
                uint32_t new_factor = SR_U16(block + 30u);
                int32_t pending_phase = (int32_t)(int16_t)(next - new_base) % (int32_t)new_factor;
                if ((new_base & 0xc000u) == 0xc000u && (counter & 0xc000u) == 0u) {
                    uint32_t span = counter - new_base + new_factor - 1u;
                    SR_U16(block + 32u) = (uint16_t)(new_base + (span - span % new_factor));
                }
                uint32_t pending_offset = (uint16_t)pending_phase;
                result = 0u;
                if (pending_offset == 0u) {
                    SR_U16(block + 36u) = 0u;
                } else {
                    uint32_t count = continuing < 2u ? SR_U16(block + 36u) : 0u;
                    uint32_t latency = SR_U16(block + 34u);
                    SR_U16(block + 36u) = (uint16_t)(count + 1u);
                    if (count >= latency)
                        result = (uint32_t)subrate_min_signed((int32_t)(uint16_t)skip,
                                                              (int32_t)(new_factor - pending_offset));
                }
            }
        }
    }
    uint32_t kind = SR_U8(record + 635u);
    if (kind == 1u || kind == 0x15u) {
        uint32_t instant = SR_U16(record + (kind == 1u ? 716u : 724u));
        result = (uint32_t)subrate_min_signed((int32_t)(uint16_t)result, (int32_t)(uint16_t)(instant - next));
    } else if (kind == 0x11u) {
        uint32_t distance = SR_U16(record + 682u) - next;
        uint32_t distance16 = (uint16_t)distance;
        if ((uint16_t)result >= distance16) {
            uint32_t interval = SR_U16(record + 676u);
            result = distance - (distance16 != 0u ? 1u : 0u);
            if (interval != SR_U16(record + 266u)) {
                SR_U16(block + 0u) = 1u;
                SR_U16(record + 850u) = 0u;
            }
        }
    }
    uint32_t anchor = (uint16_t)result + event;
    if (anchor >= 0x10000u) SR_U16(block + 2u) = (uint16_t)anchor;
    return (uint16_t)result;
}
