#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x3160d4..0x31628e: answer an LL_SUBRATE_REQ (parameters at
 * ((uintptr_t)&em9305_ram_8027e0 + 0x30u): min +0xc, max +0xe, latency +0x10, continuation +0x12, timeout
 * +0x14). Without the subrating feature (((uintptr_t)&em9305_ram_805a6c + 0x2cu) bit 6) reject with 0x1a.
 * Reject with 0x11 when the request is malformed (factor 1..500, max >= min,
 * latency < 500, continuation < 500, timeout 10..3200), outside the host
 * limits at +836..+844, or when the timeout does not cover the subrated
 * interval; a rejection also terminates with 0x6f. Otherwise send
 * LL_SUBRATE_IND (0x27) with the negotiated factor, base event (+262),
 * latency, continuation and timeout, remember them at +876..+886 and flag
 * a parameter change (+636 bit 29) when they differ from the current ones.
 * Without a packet buffer terminate (0x6f) and report status 13. */
extern uint32_t opencfw_em9305_phy_reject_32698c(uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t);
extern uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_dispatch_child_323498(uint32_t,uint32_t);

#define SUB_U16(a) (*(volatile uint16_t *)(uintptr_t)(a))

static int32_t subrate_min(int32_t a, int32_t b) { return a < b ? a : b; }
static int32_t subrate_max(int32_t a, int32_t b) { return a > b ? a : b; }

void opencfw_em9305_subrate_action_3160d4(uintptr_t record)
{
    const uintptr_t request = ((uintptr_t)&em9305_ram_8027e0 + 0x30u);
    uint32_t reason = 0x1au;
    if ((em9305_ram_805a6c.u8_805a98 & 0x40u) != 0u) {
        uint32_t latency = SUB_U16(request + 0x10u);
        uint32_t factor_min = SUB_U16(request + 0xcu);
        uint32_t factor_max = SUB_U16(request + 0xeu);
        uint32_t valid = 0u;
        if (latency < 500u)
            valid = (uint16_t)(factor_max - 1u) < 500u && (int32_t)factor_max >= (int32_t)factor_min &&
                    (uint16_t)(factor_min - 1u) < 500u;
        uint32_t timeout = SUB_U16(request + 0x14u);
        uint32_t invalid = 1u;
        if (SUB_U16(record + 838u) >= factor_min && factor_max >= SUB_U16(record + 836u)) {
            uint32_t continuation = SUB_U16(request + 0x12u);
            invalid = ((uint16_t)(timeout - 3201u) < 0xf389u) | ((int32_t)continuation >= 500) | (valid ^ 1u);
        }
        reason = 0x11u;
        if (invalid == 0u && latency <= SUB_U16(record + 840u)) {
            uint32_t interval = SUB_U16(record + 266u);
            uint32_t span = (latency + 1u) * factor_min;
            uint32_t units = (interval >> 2) + interval + ((interval & 3u) != 0u ? 1u : 0u);
            if (timeout * 10u >= units * span * 2u && SUB_U16(record + 844u) >= timeout) {
                uintptr_t packet = opencfw_em9305_phy_packet_alloc_32d2f0(0xbu);
                if (packet == 0u) {
                    (void)opencfw_em9305_receive_terminate_325c08(record, 0x6fu);
                    uintptr_t base = em9305_ram_805c5c.u32_805c70;
                    (void)opencfw_em9305_dispatch_child_323498((uint8_t)((int32_t)(record - base) / 912), 0xdu);
                    return;
                }
                int32_t factor = subrate_min(subrate_max((int32_t)SUB_U16(request + 0xcu), (int32_t)SUB_U16(record + 836u)),
                                             subrate_min((int32_t)SUB_U16(request + 0xeu), (int32_t)SUB_U16(record + 838u)));
                int32_t continuation = subrate_min(subrate_max((int32_t)SUB_U16(request + 0x12u), (int32_t)SUB_U16(record + 842u)),
                                                   factor - 1);
                int32_t new_timeout = subrate_min((int32_t)SUB_U16(request + 0x14u), (int32_t)SUB_U16(record + 844u));
                int32_t new_latency = subrate_min((int32_t)SUB_U16(request + 0x10u), (int32_t)SUB_U16(record + 840u));
                uint32_t base_event = SUB_U16(record + 262u);
                uint32_t changed = 1u;
                *(volatile uint8_t *)(record + 888u) = 1u;
                if ((uint32_t)factor == SUB_U16(record + 846u) &&
                    SUB_U16(record + 850u) == (uint16_t)continuation &&
                    (uint32_t)new_latency == SUB_U16(record + 260u) &&
                    (uint32_t)new_timeout == SUB_U16(record + 852u))
                    changed = 0u;
                SUB_U16(record + 886u) = (uint16_t)new_timeout;
                SUB_U16(record + 884u) = (uint16_t)new_latency;
                SUB_U16(record + 880u) = (uint16_t)continuation;
                SUB_U16(record + 878u) = (uint16_t)base_event;
                SUB_U16(record + 876u) = (uint16_t)factor;
                volatile uint8_t *pdu = (volatile uint8_t *)packet;
                pdu[7] = (uint8_t)continuation;
                pdu[9] = (uint8_t)new_timeout;
                pdu[1] = (uint8_t)factor;
                pdu[6] = (uint8_t)((uint32_t)new_latency >> 8);
                pdu[5] = (uint8_t)new_latency;
                pdu[3] = (uint8_t)base_event;
                pdu[10] = (uint8_t)((uint32_t)new_timeout >> 8);
                pdu[8] = (uint8_t)((uint32_t)continuation >> 8);
                pdu[4] = (uint8_t)(base_event >> 8);
                pdu[2] = (uint8_t)((uint32_t)factor >> 8);
                pdu[0] = 0x27u;
                (void)opencfw_em9305_phy_packet_send_32d32c(record, packet);
                if (changed != 0u) {
                    volatile uint32_t *flags = (volatile uint32_t *)(record + 636u);
                    *flags = *flags | (1u << 29);
                }
                return;
            }
        }
    }
    (void)opencfw_em9305_phy_reject_32698c(record, reason, 1u);
    (void)opencfw_em9305_receive_terminate_325c08(record, 0x6fu);
}
