extern uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_wsf_timer_stop(uintptr_t);
/* Native32c810 complete tail, event112. */
uint32_t opencfw_em9305_phy_finish_32c810(uintptr_t record)
{ return opencfw_em9305_receive_terminate_325c08(record,112u); }
/* Native32c818..32c822: timer address derived only when record flag permits. */
uint32_t opencfw_em9305_phy_complete_32c818(uintptr_t record)
{
 if((*(volatile uint8_t *)(record+11u)&32u)==0u)return (uint32_t)record;
 return opencfw_em9305_wsf_timer_stop(record+728u);
}
/* Native32caa0..32cabe: copy four fields from captured runtime message. */
uint32_t opencfw_em9305_phy_defer_32caa0(uintptr_t record)
{
 uintptr_t message=*(volatile uint32_t *)(uintptr_t)0x805c6cu;
 *(volatile uint8_t *)(record+594u)=*(volatile uint8_t *)(message+4u);
 *(volatile uint8_t *)(record+595u)=*(volatile uint8_t *)(message+5u);
 *(volatile uint8_t *)(record+596u)=*(volatile uint8_t *)(message+6u);
 *(volatile uint8_t *)(record+79u)=*(volatile uint8_t *)(message+8u);
 return (uint32_t)record;
}
/* Native32cb48..32cb56 retains adjusted R0 return after halfword store. */
uint32_t opencfw_em9305_phy_defer_32cb48(uintptr_t record)
{
 uint32_t value=*(volatile uint16_t *)(uintptr_t)0x80281cu;
 *(volatile uint16_t *)(record+720u)=(uint16_t)value;
 return (uint32_t)(record+720u);
}
