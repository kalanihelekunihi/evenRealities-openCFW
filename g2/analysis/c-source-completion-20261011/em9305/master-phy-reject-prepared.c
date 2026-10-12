extern uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t);
extern uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_phy_response_3232dc(uintptr_t,uint32_t);
/* Native32698c..3269ea, complete reject packet constructor/submit. */
uint32_t opencfw_em9305_phy_reject_32698c(uintptr_t record,uint32_t reason,uint32_t extended)
{
 uint32_t use_extended=1u;
 if(extended==0u){
  use_extended=0u;
  if((*(volatile uint8_t *)(record+544u)&4u)!=0u)
   use_extended=*(volatile uint8_t *)(record+534u)!=0u;
 }
 if(*(volatile uint8_t *)(record+834u)!=0u)reason=68u;
 uintptr_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(use_extended!=0u?3u:2u);
 if(packet==0u)return 0u;
 if(use_extended!=0u){
  *(volatile uint8_t *)packet=17u;
  uint32_t operation=*(volatile uint8_t *)(uintptr_t)0x802818u;
  *(volatile uint8_t *)(packet+2u)=(uint8_t)reason;
  *(volatile uint8_t *)(packet+1u)=(uint8_t)operation;
 }else{
  *(volatile uint8_t *)(packet+1u)=(uint8_t)reason;
  *(volatile uint8_t *)packet=13u;
 }
 return opencfw_em9305_phy_packet_send_32d32c(record,packet);
}
/* Native31634c and3163a4 actual action tails. */
uint32_t opencfw_em9305_phy_action_31634c(uintptr_t record)
{ return opencfw_em9305_phy_response_3232dc(record,12u); }
uint32_t opencfw_em9305_phy_action_3163a4(uintptr_t record)
{ return opencfw_em9305_phy_reject_32698c(record,35u,1u); }
