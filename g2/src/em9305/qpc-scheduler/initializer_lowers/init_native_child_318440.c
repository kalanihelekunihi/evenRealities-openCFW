#include <stdint.h>

/* Native 0x318440..0x3184f2: choose the own address for a connection
 * request. Address type +57 (bit 1 = resolvable) selects the request's
 * random address (+8/+12, type 1 with +4 set) or the public address at
 * 0x805b40, mirrored at 0x805be2 (type) / 0x805be4 (address). A resolvable
 * type tries the peer-pair resolution (native 0x303a40) on +48/+52/+58. The
 * chosen address and peer fields go to the parameter block (+0x54..+96),
 * whose flags +0x50 get bit 0, bit 1 for a random address and bit 3 for a
 * non-zero peer type; the flags are returned. */
extern uint32_t opencfw_em9305_radio_peer_pair_303a40(uint32_t,uint32_t,uint32_t,uintptr_t);

uint32_t opencfw_em9305_child_318440(uintptr_t link, uintptr_t params, uintptr_t request)
{
    volatile uint8_t *own_type = (volatile uint8_t *)(uintptr_t)0x805be2u;
    volatile uint32_t *own_address = (volatile uint32_t *)(uintptr_t)0x805be4u;
    uint32_t type = *(volatile uint8_t *)(request + 57u);
    uint32_t low, high, random;
    own_address[1] = 0u;
    own_address[0] = 0u;
    *own_type = (uint8_t)(type & ~2u);
    if ((type & ~2u) == 1u && *(volatile uint8_t *)(request + 4u) != 0u) {
        high = *(volatile uint32_t *)(request + 12u);
        low = *(volatile uint32_t *)(request + 8u);
        *(volatile uint8_t *)(link + 2u) = 1u;
        *(volatile uint8_t *)(request + 3u) = 0u;
        random = 1u;
    } else {
        high = *(volatile uint32_t *)(uintptr_t)0x805b44u;
        low = *(volatile uint32_t *)(uintptr_t)0x805b40u;
        *(volatile uint8_t *)(link + 2u) = 0u;
        random = 0u;
    }
    *(volatile uint32_t *)(request + 20u) = high;
    *(volatile uint32_t *)(request + 16u) = low;
    if ((type & 2u) != 0u) {
        uint32_t pair[2];
        if (opencfw_em9305_radio_peer_pair_303a40(*(volatile uint8_t *)(request + 58u),
                                                  *(volatile uint32_t *)(request + 48u),
                                                  *(volatile uint32_t *)(request + 52u),
                                                  (uintptr_t)pair) != 0u) {
            high = pair[1];
            low = pair[0];
            uint32_t resolved_type = *(volatile uint8_t *)(request + 57u);
            random = 1u;
            *(volatile uint8_t *)(link + 2u) = 1u;
            *(volatile uint32_t *)(request + 20u) = high;
            *(volatile uint32_t *)(request + 16u) = low;
            own_address[1] = high;
            own_address[0] = low;
            *own_type = (uint8_t)resolved_type;
        } else {
            high = *(volatile uint32_t *)(request + 20u);
            low = *(volatile uint32_t *)(request + 16u);
            random = *(volatile uint8_t *)(link + 2u);
        }
    }
    uint32_t flags = *(volatile uint32_t *)(params + 0x50u);
    uint32_t peer_type = *(volatile uint8_t *)(request + 58u);
    uint32_t peer_high = *(volatile uint32_t *)(request + 52u);
    uint32_t peer_low = *(volatile uint32_t *)(request + 48u);
    if (random != 0u) flags |= 2u;
    *(volatile uint32_t *)(params + 0x54u) = low;
    *(volatile uint32_t *)(params + 0x58u) = high;
    *(volatile uint32_t *)(params + 96u) = peer_high;
    *(volatile uint32_t *)(params + 0x5cu) = peer_low;
    *(volatile uint32_t *)(params + 0x50u) = flags | 1u;
    if (peer_type == 0u) return flags | 1u;
    *(volatile uint32_t *)(params + 0x50u) = flags | 9u;
    return flags | 9u;
}
