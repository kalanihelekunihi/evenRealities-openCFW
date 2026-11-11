#include <stdint.h>

/* Native 0x31f86c..0x31f904: build the advertising address header for a
 * link. Requires session data (+0x68), state 0 or 6 (+184) and an enabled
 * address (+188). Writes the advertiser address (+168/+172) to link +120 and
 * +104/+108 with the channel byte +186 at +195; when the link uses a peer
 * address (flag +13 bit 1) the paired address (native 0x303a40, seeded from
 * +0x54/+0x58) goes to +114 and +194 records whether it is resolvable. The
 * header +192 is encoded into +112 and native 0x325660 finishes the link. */
extern uintptr_t opencfw_em9305_radio_address_write_3045e8(uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_radio_peer_pair_303a40(uint32_t,uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_radio_encode_3239d4(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_child_325660(uintptr_t);

uint32_t opencfw_em9305_child_31f86c(uintptr_t context)
{
    uintptr_t session = *(volatile uint32_t *)(context + 0x2cu);
    if (*(volatile uint32_t *)(session + 0x68u) == 0u) return 0u;
    uintptr_t link = *(volatile uint32_t *)(context + 0x24u);
    uint32_t state = *(volatile uint8_t *)(session + 184u);
    if (state != 6u && state != 0u) return 0u;
    if (*(volatile uint8_t *)(session + 188u) == 0u) return 0u;
    (void)opencfw_em9305_radio_address_write_3045e8(link + 120u,
                                                    *(volatile uint32_t *)(session + 168u),
                                                    *(volatile uint32_t *)(session + 172u));
    uint32_t flags = *(volatile uint8_t *)(link + 13u);
    uint32_t channel = *(volatile uint8_t *)(session + 186u);
    uint32_t low = *(volatile uint32_t *)(session + 168u);
    uint32_t high = *(volatile uint32_t *)(session + 172u);
    *(volatile uint32_t *)(link + 108u) = high;
    *(volatile uint32_t *)(link + 104u) = low;
    *(volatile uint8_t *)(link + 195u) = (uint8_t)channel;
    if ((flags & 2u) != 0u) {
        uint32_t pair[2];
        pair[0] = *(volatile uint32_t *)(session + 0x54u);
        pair[1] = *(volatile uint32_t *)(session + 0x58u);
        uint32_t resolvable = (*(volatile uint8_t *)(session + 80u) >> 1) & 1u;
        uint32_t paired = opencfw_em9305_radio_peer_pair_303a40(
            *(volatile uint8_t *)(session + 187u), *(volatile uint32_t *)(session + 176u),
            *(volatile uint32_t *)(session + 180u), (uintptr_t)pair);
        (void)opencfw_em9305_radio_address_write_3045e8(link + 114u, pair[0], pair[1]);
        *(volatile uint8_t *)(link + 194u) = paired != 0u ? 1u : (uint8_t)resolvable;
    }
    (void)opencfw_em9305_radio_encode_3239d4(link + 112u, link + 192u);
    return opencfw_em9305_child_325660(link);
}
