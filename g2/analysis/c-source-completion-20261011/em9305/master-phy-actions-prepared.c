extern uint32_t opencfw_em9305_phy_start_324680(uintptr_t);
extern uint32_t opencfw_em9305_phy_schedule_318278(uintptr_t);
extern uint32_t opencfw_em9305_phy_update_packet_326764(uintptr_t,uint32_t,uint32_t,uint32_t,uint32_t);
/* Native31592c..31593a, retains incoming record across both calls. */
uint32_t opencfw_em9305_phy_action_31592c(uintptr_t record)
{
 (void)opencfw_em9305_phy_start_324680(record);
 return opencfw_em9305_phy_schedule_318278(record);
}
/* Native315a0c..315a26. */
uint32_t opencfw_em9305_phy_action_315a0c(uintptr_t record)
{
 uint32_t bits=*(volatile uint32_t *)(record+636u);
 *(volatile uint32_t *)(record+636u)=bits|(1u<<21u);
 (void)opencfw_em9305_phy_defer_32caa0(record);
 return opencfw_em9305_phy_action_31592c(record);
}
/* Native315e60..315e6e. */
uint32_t opencfw_em9305_phy_action_315e60(uintptr_t record)
{
 (void)opencfw_em9305_phy_defer_32cb48(record);
 return opencfw_em9305_phy_action_31592c(record);
}
/* Native315e84..315eaa: exact byte capture sequence before packet child. */
uint32_t opencfw_em9305_phy_action_315e84(uintptr_t record)
{
 uint32_t one=*(volatile uint8_t *)(record+720u);
 uint32_t four=*(volatile uint8_t *)(uintptr_t)0x80281du;
 uint32_t three=*(volatile uint8_t *)(uintptr_t)0x80281cu;
 uint32_t two=*(volatile uint8_t *)(record+721u);
 (void)opencfw_em9305_phy_update_packet_326764(record,one,two,three,four);
 return opencfw_em9305_phy_complete_32c818(record);
}
/* Native315f0c..315f46: incidental R0 flags retained on no-notify paths. */
uint32_t opencfw_em9305_phy_action_315f0c(uintptr_t record)
{
 (void)opencfw_em9305_phy_complete_32c818(record);
 uint32_t bits=*(volatile uint32_t *)(record+636u);
 if((bits&(1u<<21u))==0u)return bits;
 bits&=~(1u<<21u);
 uint32_t operation=*(volatile uint8_t *)(uintptr_t)0x802818u;
 *(volatile uint32_t *)(record+640u)=0u;
 *(volatile uint32_t *)(record+636u)=bits;
 uint32_t reason;
 if(operation==7u)reason=26u;
 else if(operation==17u||operation==13u)reason=*(volatile uint8_t *)(uintptr_t)0x80281du;
 else return bits;
 return opencfw_em9305_phy_response_3232dc(record,reason);
}
