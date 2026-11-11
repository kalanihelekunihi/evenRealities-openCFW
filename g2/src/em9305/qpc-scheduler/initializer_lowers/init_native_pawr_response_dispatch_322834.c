#include <stdint.h>

/* Native 0x322834..0x322884: match a decoded PAwR response against the
 * eight-slot ring at 0x80501c by its packed address (+12) tagged with the
 * PHY (+11, two bits at 16) and the flags (+10, three bits at 18). A new
 * address is committed to the ring and, while reporting is enabled
 * (0x804ffc == 1), the response is reported with header 0x20000. Stock
 * relies on 3169b4 preserving R2, R4 and R7; the C passes them explicitly. */
extern uint64_t opencfw_em9305_controller_pack_address(uintptr_t address);
extern uint32_t opencfw_em9305_pawr_match_3169b4(uintptr_t ring,uint32_t first,
                                                 uint32_t second);
extern uintptr_t opencfw_em9305_pawr_match_commit_316984(uintptr_t record,
                                                         uint32_t first,
                                                         uint32_t second);
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t event);

uint32_t opencfw_em9305_pawr_response_dispatch_322834(uintptr_t response)
{
    uint32_t phy=*(volatile uint8_t *)(response+11u);
    uint64_t address=opencfw_em9305_controller_pack_address(response+12u);
    uint32_t flags=*(volatile uint8_t *)(response+10u);
    uint32_t first=(uint32_t)address;
    uint32_t second=(uint32_t)(address>>32)|((phy&3u)<<16)|((flags&7u)<<18);
    uint32_t matched=opencfw_em9305_pawr_match_3169b4(0x80501cu,first,second);
    if(matched!=0u)return matched;
    (void)opencfw_em9305_pawr_match_commit_316984(0x80501cu,first,second);
    if(*(volatile uint8_t *)0x804ffcu!=1u)return 0u;
    *(volatile uint32_t *)response=0x20000u;
    return opencfw_em9305_ll_event_callback_30e79c(response);
}
