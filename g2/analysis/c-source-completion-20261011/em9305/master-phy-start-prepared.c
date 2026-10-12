/* Native31b39c..31b3b4: supported PHY mask from stored feature word. */
uint32_t opencfw_em9305_phy_supported_31b39c(void)
{
 uint32_t bits=*(volatile uint32_t *)(uintptr_t)0x805a94u;
 return ((bits&256u)==0u?1u:3u)|((bits>>9u)&4u);
}
/* Native316550..316590 full peer PHY start, preserving fresh flags reload. */
uint32_t opencfw_em9305_phy_action_316550(uintptr_t record)
{
 uint32_t flags=*(volatile uint8_t *)(record+594u);
 uint32_t second=*(volatile uint8_t *)(record+596u),first;
 if((flags&1u)==0u)first=*(volatile uint8_t *)(record+595u);
 else{first=opencfw_em9305_phy_supported_31b39c();flags=*(volatile uint8_t *)(record+594u);}
 if((flags&2u)!=0u)second=opencfw_em9305_phy_supported_31b39c();
 uint32_t four=*(volatile uint8_t *)(record+721u);
 uint32_t three=*(volatile uint8_t *)(record+720u);
 (void)opencfw_em9305_phy_update_packet_326764(record,(uint8_t)first,(uint8_t)second,three,four);
 return opencfw_em9305_phy_complete_32c818(record);
}
extern uint32_t opencfw_em9305_phy_choose_316610(uintptr_t,uint32_t,uintptr_t,uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_phy_apply_327544(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_phy_update_complete_32e220(uintptr_t);
extern uint32_t opencfw_em9305_phy_initiate_packet_326740(uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_phy_timer_start_32c7e4(uintptr_t);
/* Native3164a8..31654e: choose, compare mapped live PHY, initiate or finish. */
uint32_t opencfw_em9305_phy_action_3164a8(uintptr_t record)
{
 uint32_t flags=*(volatile uint8_t *)(record+594u);
 if((flags&3u)!=3u){
  uint8_t first=*(volatile uint8_t *)(record+595u);
  uint8_t second=*(volatile uint8_t *)(record+596u);
  (void)opencfw_em9305_phy_choose_316610(record,flags,(uintptr_t)&first,(uintptr_t)&second,0u);
  uint32_t mode=*(volatile uint8_t *)(record+76u),index=mode-2u;
  uint32_t mapped=index>=3u?1u:(0x00080402u>>(index*8u))&255u;
  if(first==mapped){
   mode=*(volatile uint8_t *)(record+77u);index=mode-2u;
   mapped=index>=3u?1u:(0x00080402u>>(index*8u))&255u;
   if(second==mapped)goto unchanged;
  }
  (void)opencfw_em9305_phy_apply_327544(record,first);
  (void)opencfw_em9305_phy_update_complete_32e220(record);
  (void)opencfw_em9305_phy_initiate_packet_326740(record,first,second);
  return opencfw_em9305_phy_timer_start_32c7e4(record);
 }
 unchanged:
 (void)opencfw_em9305_phy_update_complete_32e220(record);
 return opencfw_em9305_receive_terminate_325c08(record,110u);
}
