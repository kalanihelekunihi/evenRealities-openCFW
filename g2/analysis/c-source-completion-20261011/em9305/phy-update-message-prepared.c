/* Native314114..314130 full locked linked-queue count, 16-bit return. */
uint32_t opencfw_em9305_phy_queue_count_314114(uintptr_t queue)
{
 (void)opencfw_em9305_wsf_critical_enter();
 uintptr_t node=*(volatile uint32_t *)queue;uint32_t count=0u;
 while(node!=0u){node=*(volatile uint32_t *)node;++count;}
 (void)opencfw_em9305_wsf_critical_exit();
 return (uint16_t)count;
}
/* Native326814..3268c8, full update instant calculation and five-byte packet.
 * Native32684a/32686c are MPYWHUL; exact assembly identity is recorded. */
uint32_t opencfw_em9305_phy_update_message_326814(uintptr_t record,uint32_t first,uint32_t second)
{
 uintptr_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(5u);
 if(packet==0u)return 0u;
 uintptr_t queue=record+360u;
 *(volatile uint8_t *)(record+723u)=(uint8_t)second;
 *(volatile uint8_t *)(record+722u)=(uint8_t)first;
 uint32_t count=opencfw_em9305_phy_queue_count_314114(queue);
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t unit=*(volatile uint16_t *)(config+76u);
 uint32_t scaled=opencfw_em9305_config_link_mpywhul(count,unit);
 uint32_t capacity=opencfw_em9305_ll_event_mode_32d4b0(record);
 uint32_t timing=opencfw_em9305_radio_record_timing_30c40c(scaled,capacity);
 if(timing<6u)timing=6u;
 else{
  count=opencfw_em9305_phy_queue_count_314114(queue);
  config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  unit=*(volatile uint16_t *)(config+76u);
  scaled=opencfw_em9305_config_link_mpywhul(count,unit);
  capacity=opencfw_em9305_ll_event_mode_32d4b0(record);
  timing=opencfw_em9305_radio_record_timing_30c40c(scaled,capacity);
 }
 if((first|second)!=0u){
  uint32_t latency=*(volatile uint16_t *)(record+260u);
  uint32_t interval=*(volatile uint16_t *)(record+846u);
  uint32_t product=timing*(latency+1u);
  uint32_t anchor=*(volatile uint16_t *)(record+262u);
  product=opencfw_em9305_native_mpyw_309f62(product,interval);
  *(volatile uint16_t *)(record+724u)=(uint16_t)(product+anchor);
 }else{
  *(volatile uint16_t *)(record+724u)=0u;
  (void)opencfw_em9305_receive_terminate_325c08(record,110u);
 }
 *(volatile uint8_t *)(packet+2u)=(uint8_t)second;
 *(volatile uint8_t *)(packet+1u)=(uint8_t)first;
 *(volatile uint8_t *)packet=24u;
 *(volatile uint8_t *)(packet+3u)=*(volatile uint8_t *)(record+724u);
 *(volatile uint8_t *)(packet+4u)=*(volatile uint8_t *)(record+725u);
 return opencfw_em9305_phy_packet_send_32d32c(record,packet);
}
