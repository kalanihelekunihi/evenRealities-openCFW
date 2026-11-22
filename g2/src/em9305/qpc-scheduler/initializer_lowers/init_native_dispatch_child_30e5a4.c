#include <stdint.h>

/* Native 0x30e5a4..0x30e6b0: LE Channel Selection Algorithm #2. From the
 * event counter and the channel identifier (+0x30) compute prn_e with three
 * rounds of byte-wise bit reversal and MAM (x * 17 + id), store prn_s at
 * +0x32 and take the unmapped channel prn_e mod 37. A channel that is used
 * in the 37-bit map (+0/+4, tested with native 0x3027f4) is kept, and with
 * remap set its position in the used-channel list (+8) is stored at +52;
 * an unused channel is remapped to list entry (prn_e * count(+45)) >> 16,
 * whose index is stored at +52 with remap set. Returns the channel. */
extern uint64_t opencfw_em9305_child_3027f4(uint32_t,uint32_t,uint32_t);

static uint32_t csa2_permute(uint32_t value)
{
    value = (value & 0xf0f0u) | ((value << 8) & 0xf0f00u);
    value = (value & 0xcccc0u) | ((value << 4) & 0x333300u);
    value = (value & 0x2aaa80u) | ((value << 2) & 0x555500u);
    return value >> 7;
}

uint32_t opencfw_em9305_dispatch_child_30e5a4(uintptr_t context, uint32_t counter, uint32_t unused,
                                              uint32_t remap)
{
    (void)unused;
    uint32_t id = *(volatile uint16_t *)(context + 0x30u);
    uint32_t prn = counter ^ id;
    for (uint32_t round = 0u; round < 3u; ++round)
        prn = (csa2_permute(prn) & 0xffffu) * 17u + id;
    uint32_t prn_e = prn ^ id;
    *(volatile uint16_t *)(context + 0x32u) = (uint16_t)prn;
    uint32_t quotient = ((prn_e & 0xffffu) * 0xdd68u) >> 21;
    uint32_t channel = (uint16_t)(prn_e + (uint32_t)((int32_t)quotient * -37));
    uint64_t map = opencfw_em9305_child_3027f4(*(volatile uint32_t *)context,
                                                     *(volatile uint32_t *)(context + 4u), channel);
    if (((uint32_t)map & 1u) != 0u) {
        if (remap != 0u) {
            const volatile uint8_t *used = (const volatile uint8_t *)(context + 8u);
            for (uint32_t index = 0u; index < 37u; ++index) {
                if (used[index] == channel) {
                    *(volatile uint8_t *)(context + 52u) = (uint8_t)index;
                    break;
                }
            }
        }
        return (uint8_t)channel;
    }
    uint32_t index = ((prn_e & 0xffffu) * *(volatile uint8_t *)(context + 45u)) >> 16;
    if (remap != 0u) *(volatile uint8_t *)(context + 52u) = (uint8_t)index;
    return *(volatile uint8_t *)(context + 8u + index);
}
