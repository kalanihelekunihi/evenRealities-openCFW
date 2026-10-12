extern uint32_t opencfw_em9305_slave_phy_apply_32cb58(uintptr_t);
/* Native315a28..315a42 full pending action, same authenticated shared path. */
uint32_t opencfw_em9305_phy_action_315a28(uintptr_t record)
{
 uint32_t bits=*(volatile uint32_t *)(record+636u);
 *(volatile uint32_t *)(record+636u)=bits|(1u<<21u);
 (void)opencfw_em9305_phy_defer_32caa0(record);
 return opencfw_em9305_phy_action_31592c(record);
}
/* Native315c30..315c60, preserves incidental pointer/byte return. */
uint32_t opencfw_em9305_phy_action_315c30(uintptr_t record)
{
 (void)opencfw_em9305_phy_record_325250(record);
 uint32_t bits=*(volatile uint32_t *)(record+636u);
 uint32_t result=(uint32_t)(record+400u);
 if((bits&(1u<<21u))==0u)return result;
 uint32_t enabled=*(volatile uint8_t *)(record+400u);
 *(volatile uint32_t *)(record+640u)=0u;
 *(volatile uint32_t *)(record+636u)=bits&~(1u<<21u);
 if(enabled==0u)return result;
 result=*(volatile uint8_t *)(record+1u);
 if(result==3u)return result;
 return opencfw_em9305_phy_response_3232dc(record,0u);
}
/* Native315e70..315e7e and315e80 real branch tail. */
uint32_t opencfw_em9305_phy_action_315e70(uintptr_t record)
{
 (void)opencfw_em9305_phy_defer_32cb48(record);
 return opencfw_em9305_phy_action_31592c(record);
}
uint32_t opencfw_em9305_phy_action_315e80(uintptr_t record)
{ return opencfw_em9305_phy_action_315e70(record); }
/* Native315eac..315ed4 after timer completion reads global direction bytes. */
uint32_t opencfw_em9305_phy_action_315eac(uintptr_t record)
{
 (void)opencfw_em9305_phy_complete_32c818(record);
 uint32_t second=*(volatile uint8_t *)(uintptr_t)0x80281du;
 uint32_t first=*(volatile uint8_t *)(uintptr_t)0x80281cu;
 if((first|second)==0u)return opencfw_em9305_receive_terminate_325c08(record,110u);
 return opencfw_em9305_slave_phy_apply_32cb58(record);
}
uint32_t opencfw_em9305_phy_action_316354(uintptr_t record)
{ return opencfw_em9305_phy_response_3232dc(record,12u); }
/* Native31644c..3164a6 full slave preference/response/timer action. */
uint32_t opencfw_em9305_phy_action_31644c(uintptr_t record)
{
 volatile uint8_t first=*(volatile uint8_t *)(record+595u);
 volatile uint8_t second=*(volatile uint8_t *)(record+596u);
 uint32_t direction_a=*(volatile uint8_t *)(record+720u);
 uint32_t direction_b=*(volatile uint8_t *)(record+721u);
 uint32_t flags=*(volatile uint8_t *)(record+594u);
 (void)opencfw_em9305_phy_choose_316610(record,flags,(uintptr_t)&first,(uintptr_t)&second,direction_a&direction_b);
 uint32_t chosen_first=first;
 (void)opencfw_em9305_phy_apply_327544(record,chosen_first);
 (void)opencfw_em9305_phy_update_complete_32e220(record);
 uint32_t chosen_second=second;
 (void)opencfw_em9305_phy_response_packet_326758(record,chosen_first,chosen_second);
 return opencfw_em9305_phy_timer_start_32c7e4(record);
}
