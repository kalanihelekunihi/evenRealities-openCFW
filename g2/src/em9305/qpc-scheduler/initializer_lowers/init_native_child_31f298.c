#include <stdint.h>

/* Native 0x31f298..0x31f400: process a received periodic/extended
 * advertising report for a scanner link (+0x24, session +44) while the
 * scanner (0x803b68) is not paused. Without data (more == 0) only a
 * pending chain (state +56 == 1) is marked complete (+24 bit 6); state 2
 * is ignored. For a fresh report (state 0) the advertiser type (+163, bit 1
 * when it differs from the identity) and address (+152/+156) are checked
 * against the filter (native 0x319ee8) for the target (+60, when filter
 * flag bit 1 at 0x803b90 is set) and the report (+20), with the
 * report filters (natives 0x31a1b0, 0x31a1fc). Accepted data from the
 * buffer at 0x803b6c (length 0x803b70) is appended to the link's report
 * (+148, offset +48) unless it would exceed the configured maximum
 * (config +0x20), which marks it truncated. Returns 1 when data was
 * appended, else 0. */
extern uint32_t opencfw_em9305_child_319ee8(uintptr_t link, uint32_t mode, uintptr_t header,
                                            uint32_t low, uint32_t high, uint32_t type,
                                            int32_t power, uint32_t zero, uintptr_t report);
extern uint32_t opencfw_em9305_child_31a1b0(uintptr_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_child_31a1fc(uintptr_t,uintptr_t,uintptr_t);
extern void *opencfw_em9305_memcpy(void *destination, const void *source, uint32_t bytes);

uint32_t opencfw_em9305_child_31f298(uintptr_t context, uint32_t more)
{
    const uintptr_t scanner = 0x803b68u;
    if (*(volatile uint8_t *)(scanner + 1u) != 0u) return 0u;
    uintptr_t link = *(volatile uint32_t *)(context + 0x24u);
    uintptr_t state = link + 0x38u;
    uintptr_t report = link + 0x14u;
    uint32_t mode = *(volatile uint8_t *)(link + 56u);
    if (more == 0u) {
        if (mode != 1u) {
            *(volatile uint8_t *)(link + 96u) = 0u;
            return 0u;
        }
        *(volatile uint16_t *)(link + 0x18u) = (uint16_t)(*(volatile uint16_t *)(link + 0x18u) | 0x40u);
        opencfw_em9305_child_31a1fc(link, report, state);
        return 0u;
    }
    if (mode == 2u) return 0u;
    uintptr_t session = *(volatile uint32_t *)(context + 44u);
    if (mode == 0u) {
        uint32_t type = *(volatile uint8_t *)(session + 163u);
        uint32_t identity_type = *(volatile uint8_t *)(session + 162u);
        uint32_t filter = *(volatile uint8_t *)(uintptr_t)0x803b90u;
        uint32_t high = *(volatile uint32_t *)(session + 156u);
        uint32_t low = *(volatile uint32_t *)(session + 152u);
        *(volatile uint8_t *)(link + 153u) = (uint8_t)filter;
        if (type != identity_type ||
            ((*(volatile uint32_t *)(session + 148u) ^ high) | (*(volatile uint32_t *)(session + 144u) ^ low)) != 0u)
            type |= 2u;
        uintptr_t target = link + 0x3cu;
        if ((filter & 2u) != 0u) {
            if (opencfw_em9305_child_319ee8(link, *(volatile uint16_t *)(link + 64u), scanner + 0xcu,
                                            low, high, type, *(volatile int8_t *)(link + 77u), 0u,
                                            target) == 0u) {
                *(volatile uint8_t *)(link + 96u) = 0u;
                opencfw_em9305_child_31a1fc(link, report, state);
                return 0u;
            }
            uintptr_t target_state = link + 0x60u;
            *(volatile uint16_t *)(link + 64u) = (uint16_t)(*(volatile uint16_t *)(link + 64u) & ~8u);
            *(volatile uint32_t *)(link + 92u) = 0u;
            *(volatile uint16_t *)(link + 88u) = 0u;
            if (opencfw_em9305_child_31a1b0(link, target, target_state) != 0u)
                opencfw_em9305_child_31a1fc(link, target, target_state);
        }
        if (opencfw_em9305_child_319ee8(link, *(volatile uint16_t *)(scanner + 0xcu + 0x1eu),
                                        scanner + 0xcu, low, high, type,
                                        *(volatile int8_t *)(session + 133u), 0u, report) == 0u ||
            opencfw_em9305_child_31a1b0(link, report, state) == 0u) {
            opencfw_em9305_child_31a1fc(link, report, state);
            return 0u;
        }
    }
    uintptr_t config = *(volatile uint32_t *)(uintptr_t)0x805cacu;
    uint32_t used = *(volatile uint16_t *)(link + 0x30u);
    uint32_t length = *(volatile uint8_t *)(scanner + 8u);
    if ((uint16_t)(*(volatile uint16_t *)(config + 0x20u) - used) < length) {
        *(volatile uint16_t *)(link + 0x18u) = (uint16_t)(*(volatile uint16_t *)(link + 0x18u) | 0x40u);
        opencfw_em9305_child_31a1fc(link, report, state);
        return 0u;
    }
    uint32_t channel = *(volatile uint8_t *)(session + 133u);
    (void)opencfw_em9305_memcpy((void *)(*(volatile uint32_t *)(link + 148u) + used),
                                (const void *)*(volatile uint32_t *)(scanner + 4u), length);
    used = *(volatile uint16_t *)(link + 0x30u);
    uint32_t flags = *(volatile uint8_t *)(link + 154u);
    *(volatile uint8_t *)(link + 37u) = (uint8_t)channel;
    *(volatile uint16_t *)(link + 0x30u) = (uint16_t)(length + used);
    if ((flags & 0x40u) != 0u)
        *(volatile uint8_t *)(link + 36u) = *(volatile uint8_t *)(link + 177u);
    if ((*(volatile uint8_t *)(scanner + 0xau) & 0x10u) == 0u)
        opencfw_em9305_child_31a1fc(link, report, state);
    return 1u;
}
