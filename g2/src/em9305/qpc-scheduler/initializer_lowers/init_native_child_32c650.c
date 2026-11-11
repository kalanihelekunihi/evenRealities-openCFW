#include <stdint.h>

/* Native 0x32c650..0x32c69c: for an associated record (object+0x24) with a
 * pending output (+828) and the sync flag (+0xae1) set, measure the time
 * since the anchor (+0x9ac), run the duration piece for its PHY, and fill
 * the sync info through 323bac. Returns 0 if nothing was pending. */
extern uint32_t opencfw_em9305_auxiliary_elapsed_303f8c(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_radio_duration_piece_312b88(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_child_323bac(uintptr_t,uint32_t,uint32_t,uintptr_t);

uint32_t opencfw_em9305_child_32c650(uintptr_t object,uint32_t now)
{
    uintptr_t record=*(volatile uint32_t *)(object+0x24u);
    if(*(volatile uint32_t *)(record+828u)==0u) return 0u;
    if(*(volatile uint8_t *)(record+0xae1u)==0u) return 0u;
    uint32_t elapsed=opencfw_em9305_auxiliary_elapsed_303f8c(
        *(volatile uint32_t *)(record+0x9acu),now);
    uintptr_t phy=*(volatile uint32_t *)(record+0x904u);
    (void)opencfw_em9305_radio_duration_piece_312b88(*(volatile uint8_t *)(phy+12u),
        *(volatile uint8_t *)(record+0x916u),*(volatile uint8_t *)(phy+124u));
    return opencfw_em9305_child_323bac(record,elapsed,*(volatile uint8_t *)(record+0xae0u),
                                       *(volatile uint32_t *)(record+828u));
}
