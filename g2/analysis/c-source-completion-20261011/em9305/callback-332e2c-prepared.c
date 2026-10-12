/* Native continuation332e2c..332efc: prepared complete body.
 * Packet pointer and policy kind survive duration332be4's exact register set. */
uint32_t opencfw_em9305_command_callback_332e2c(uintptr_t object)
{
 uintptr_t state=0x8058dcu;
 uint32_t count=*(volatile uint16_t *)(state+4u);
 uint32_t limit=*(volatile uint16_t *)(state+2u);
 uintptr_t record=*(volatile uint32_t *)(object+44u);
 uint32_t next=count+1u;
 *(volatile uint16_t *)(state+4u)=(uint16_t)next;
 if(limit!=0u&&(uint16_t)next>=limit)(void)opencfw_em9305_command_stop_30b654(0u);
 uint32_t fresh=*(volatile uint8_t *)state;
 uintptr_t packet=*(volatile uint32_t *)(record+104u);
 if(fresh==1u){
  uintptr_t policy=0x805994u;
  uint32_t recorded_channel=*(volatile uint8_t *)(record+1u);
  uint32_t channel=*(volatile uint8_t *)(policy+2u);
  uint32_t kind=*(volatile uint8_t *)(policy+1u);
  if(channel==recorded_channel){
   uint32_t header=*(volatile uint8_t *)packet;
   if(kind==(header&~32u)){
    uint32_t packet_pattern=*(volatile uint8_t *)(packet+1u);
    uint32_t pattern=*(volatile uint8_t *)policy;
    if(pattern==packet_pattern){
     uint32_t recorded_mode=*(volatile uint8_t *)(record+12u);
     uint32_t mode=*(volatile uint8_t *)(policy+3u);
     if(mode==recorded_mode){
      uint32_t recorded_encoding=*(volatile uint8_t *)(record+14u);
      uint32_t encoding=*(volatile uint16_t *)(policy+4u);
      if(encoding==recorded_encoding)return opencfw_em9305_auxiliary_insert_313220(object);
     }
    }
   }
  }
  uint32_t mode=*(volatile uint8_t *)(policy+3u);
  uint32_t encoding=*(volatile uint8_t *)(policy+4u);
  uint32_t pattern=*(volatile uint8_t *)policy;
  *(volatile uint8_t *)(record+1u)=(uint8_t)channel;
  *(volatile uint8_t *)(record+15u)=0u;
  *(volatile uint16_t *)(record+108u)=(uint16_t)(pattern+2u);
  *(volatile uint8_t *)(record+13u)=(uint8_t)mode;
  *(volatile uint8_t *)(record+12u)=(uint8_t)mode;
  *(volatile uint8_t *)(record+14u)=(uint8_t)encoding;
  uint32_t duration=opencfw_em9305_command_duration_332be4(pattern,mode,encoding);
  *(volatile uint16_t *)(record+110u)=(uint16_t)duration;
  (void)opencfw_em9305_command_pattern_332b94(pattern,kind,packet);
  return opencfw_em9305_auxiliary_insert_313220(object);
 }
 (void)opencfw_em9305_wsf_pool_release(packet);
 (void)opencfw_em9305_common_release_304588(2u);
 if(*(volatile uint8_t *)state==4u){
  uintptr_t response=opencfw_em9305_wsf_event_allocate(4u);
  if(response==0u)return 0u;
  *(volatile uint16_t *)(response+2u)=261u;
  uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
  return opencfw_em9305_wsf_task_message_send(handler,response);
 }
 *(volatile uint8_t *)state=0u;
 *(volatile uint8_t *)(uintptr_t)0x805a78u=0u;
 return opencfw_em9305_command_count_down_30e48c();
}
