/* Native321150 and32b04c entries capture record R0 and event R1; genuine
 * state-machine bodies remain imports. Native executable literals replaced
 * with source symbols, never published as linked stock code addresses. */
extern uint32_t opencfw_em9305_init_phy_state_321150(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_init_slave_phy_state_32b04c(uintptr_t,uint32_t);
/* Native329534..329550: short circuit635==21 then wrapped32-bit byte-1
 * unsigned comparison<2, so only625field values1 or2 succeed. */
uint32_t opencfw_em9305_init_slave_phy_predicate_329534(uintptr_t record)
{
 if(*(volatile uint8_t *)(record+635u)!=21u)return 0u;
 uint32_t value=*(volatile uint8_t *)(record+625u);
 return value-1u<2u;
}
uint32_t opencfw_em9305_init_lower_307d64(uint32_t incoming)
{
 (void)incoming;*(volatile uint32_t *)(uintptr_t)0x803d38u=(uint32_t)(uintptr_t)&opencfw_em9305_init_phy_state_321150;
 return 0x803d38u;
}
uint32_t opencfw_em9305_init_lower_30a37c(uint32_t incoming)
{
 (void)incoming;
 *(volatile uint32_t *)(uintptr_t)0x805688u=(uint32_t)(uintptr_t)&opencfw_em9305_init_slave_phy_predicate_329534;
 *(volatile uint32_t *)(uintptr_t)0x8056acu=(uint32_t)(uintptr_t)&opencfw_em9305_init_slave_phy_state_32b04c;
 return 0x8056acu;
}
