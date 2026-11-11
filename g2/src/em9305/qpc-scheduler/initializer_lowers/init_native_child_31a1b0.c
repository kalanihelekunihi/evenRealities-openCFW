#include <stdint.h>

/* Native 0x31a1b0..0x31a1fe: PAwR report filter. For an active sync record
 * (byte 0 == 1) build the match key from the report (address at +7, type +6,
 * bytes +4/+15) and the record halfword +174, then look it up in the PAwR
 * table at 0x80356c. A miss sets *missed = 1. Returns the lookup result with
 * bit 0 inverted, or 0 for an inactive record. */
extern uint64_t opencfw_em9305_controller_pack_address(uintptr_t);
extern uint32_t opencfw_em9305_child_316a68(uintptr_t key, uint32_t type,
                                            uint32_t address_low, uint32_t address_high,
                                            uint32_t b4, uint32_t b15, uint32_t interval);
extern uint32_t opencfw_em9305_pawr_match_3169b4(uintptr_t,uint32_t,uint32_t);

uint32_t opencfw_em9305_child_31a1b0(uintptr_t record, uintptr_t report, uintptr_t missed)
{
    uint32_t key[2];
    if (*(volatile uint8_t *)record != 1u) return 0u;
    uint32_t type = *(volatile uint8_t *)(report + 6u);
    uint64_t address = opencfw_em9305_controller_pack_address(report + 7u);
    (void)opencfw_em9305_child_316a68((uintptr_t)key, type, (uint32_t)address,
                                      (uint32_t)(address >> 32),
                                      *(volatile uint8_t *)(report + 4u),
                                      *(volatile uint8_t *)(report + 15u),
                                      *(volatile uint16_t *)(record + 174u));
    uint32_t match = opencfw_em9305_pawr_match_3169b4(0x80356cu, key[0], key[1]);
    if (match == 0u) *(volatile uint8_t *)missed = 1u;
    return match ^ 1u;
}
