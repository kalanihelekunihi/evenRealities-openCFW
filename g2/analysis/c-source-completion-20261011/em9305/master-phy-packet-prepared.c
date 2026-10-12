/* Native32d2f0..32d328 full packet allocation and segment header construction. */
uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t bytes)
{
 uintptr_t packet=opencfw_em9305_wsf_event_allocate(bytes+6u);
 if(packet==0u)return 0u;
 uint8_t fields[8]={3u,0u,0u,0u,0u,(uint8_t)bytes,0u,0u};
 uintptr_t length=opencfw_em9305_ll_segment_header_323d70(packet,(uintptr_t)fields);
 return (uint32_t)(packet+length);
}
/* Native32d32c..32d37c complete packet enqueue; callback ABI R0..R3. */
uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t record,uintptr_t payload)
{
 uint32_t previous=*(volatile uint8_t *)(record+378u);
 *(volatile uint8_t *)(record+378u)=(uint8_t)(previous+1u);
 uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x8051e0u;
 uint32_t opcode=*(volatile uint8_t *)payload;
 uintptr_t header=payload-(opcode==27u?3u:2u);
 if(callback!=0u){
  uint32_t length=*(volatile uint8_t *)(header+1u);
  (void)((uint32_t (*)(uintptr_t,uintptr_t,uintptr_t,uintptr_t))callback)(record+84u,header,payload,payload+length);
 }
 (void)opencfw_em9305_ll_event_enqueue(record+360u,255u,header);
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 (void)opencfw_em9305_wsf_event_post(handler,4u);
 return opencfw_em9305_ll_segment_notify_3181b4(record);
}
