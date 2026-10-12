#include <stdint.h>

/* Full native callback-table bodies 0x325f0c and 0x325f50. The packet
 * allocator, serializer, and sender are existing selected source providers. */
extern uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t bytes);
extern uint32_t opencfw_em9305_primary_query_313960(uintptr_t output,
                                                      uint32_t low,
                                                      uint32_t high);
extern uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t context,
                                                        uintptr_t packet);
uint32_t opencfw_em9305_mode_callback_325f0c(uintptr_t context,
                                               uintptr_t table_cell)
{
    (void)table_cell;
    uintptr_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(9u);
    if (packet==0u) return 0u;
    uint8_t mode=*(volatile uint8_t *)(context+2u);
    *(volatile uint8_t *)packet=(mode==0u)?8u:14u;
    uint32_t low=*(volatile uint32_t *)(uintptr_t)0x805a94u;
    uint32_t high=*(volatile uint32_t *)(uintptr_t)0x805a98u;
    (void)opencfw_em9305_primary_query_313960(packet+1u,
                                               low&0xf787cf2fu,
                                               high&0x1befu);
    return opencfw_em9305_phy_packet_send_32d32c(context,packet);
}
uint32_t opencfw_em9305_mode_callback_325f50(uintptr_t context,
                                               uintptr_t table_cell)
{
    (void)table_cell;
    uintptr_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(9u);
    if (packet==0u) return 0u;
    *(volatile uint8_t *)packet=9u;
    uint32_t context_word=*(volatile uint32_t *)(context+544u);
    uint32_t global_low=*(volatile uint32_t *)(uintptr_t)0x805a94u;
    uint32_t global_high=*(volatile uint32_t *)(uintptr_t)0x805a98u;
    uint32_t low=(context_word&0xcf2fu)|(global_low&0xf7870000u);
    uint32_t high=global_high&0x1befu;
    (void)opencfw_em9305_primary_query_313960(packet+1u,low,high);
    return opencfw_em9305_phy_packet_send_32d32c(context,packet);
}
