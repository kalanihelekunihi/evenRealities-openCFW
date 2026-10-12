/* Native32671c..32673c complete three-byte control packet. */
uint32_t opencfw_em9305_phy_control_packet_32671c(uintptr_t record,uint32_t opcode,uint32_t first,uint32_t second)
{
 uintptr_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(3u);
 if(packet==0u)return 0u;
 *(volatile uint8_t *)(packet+2u)=(uint8_t)second;
 *(volatile uint8_t *)(packet+1u)=(uint8_t)first;
 *(volatile uint8_t *)packet=(uint8_t)opcode;
 return opencfw_em9305_phy_packet_send_32d32c(record,packet);
}
/* Native326740..326754 stores second before first then tail opcode22. */
uint32_t opencfw_em9305_phy_initiate_packet_326740(uintptr_t record,uint32_t first,uint32_t second)
{
 *(volatile uint8_t *)(record+721u)=(uint8_t)second;
 *(volatile uint8_t *)(record+720u)=(uint8_t)first;
 return opencfw_em9305_phy_control_packet_32671c(record,22u,first,second);
}
uint32_t opencfw_em9305_phy_response_packet_326758(uintptr_t record,uint32_t first,uint32_t second)
{ return opencfw_em9305_phy_control_packet_32671c(record,23u,first,second); }
extern uint32_t opencfw_em9305_phy_update_message_326814(uintptr_t,uint32_t,uint32_t);
/* Native326764..326810 full directional PHY negotiation/update parent. */
uint32_t opencfw_em9305_phy_update_packet_326764(uintptr_t record,uint32_t first,uint32_t second,uint32_t third,uint32_t fourth)
{
 uint32_t second_mask=third&second,first_mask=fourth&first;
 uint32_t common=opencfw_em9305_radio_phy_project_3183d4(fourth|third);
 if((fourth!=0u&&common==third&&common==fourth)||(*(volatile uint8_t *)(record+4u)&128u)!=0u){
  second_mask&=first_mask;first_mask=second_mask;
 }
 first=opencfw_em9305_radio_phy_project_3183d4(first_mask);
 second=opencfw_em9305_radio_phy_project_3183d4(second_mask);
 uint32_t old_first=*(volatile uint8_t *)(record+76u),old_second=*(volatile uint8_t *)(record+77u);
 uint32_t a=old_first-2u,b=old_second-2u;
 uint32_t mapped=a>=3u?1u:(0x00080402u>>(a*8u))&255u;
 if(first==mapped)first=0u;
 mapped=b>=3u?1u:(0x00080402u>>(b*8u))&255u;
 if(second==mapped)second=0u;
 (void)opencfw_em9305_phy_update_message_326814(record,first,second);
 if((first|second)==0u)(void)opencfw_em9305_receive_terminate_325c08(record,110u);
 if((uint8_t)first!=0u)(void)opencfw_em9305_phy_apply_327544(record,(uint8_t)first);
 else (void)opencfw_em9305_phy_record_325250(record);
 return opencfw_em9305_phy_update_complete_32e220(record);
}
