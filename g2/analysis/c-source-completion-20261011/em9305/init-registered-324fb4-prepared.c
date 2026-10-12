/* Native334496: seven consumer-classified response data-type bytes. */
const uint8_t opencfw_em9305_init_response_types_334496[7]={2u,1u,3u,1u,1u,1u,4u};
/* Complete native326a84..326aa6. */
uint32_t opencfw_em9305_init_response_packet_326a84(uintptr_t record)
{
 uintptr_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(2u);
 if(packet==0u)return 0u;
 *(volatile uint8_t *)packet=7u;
 *(volatile uint8_t *)(packet+1u)=*(volatile uint8_t *)(uintptr_t)0x802818u;
 return opencfw_em9305_phy_packet_send_32d32c(record,packet);
}
/* Complete native324fb4..3250f2. Holes in allocated event remain unwritten. */
uint32_t opencfw_em9305_init_registered_324fb4(uintptr_t record)
{
 uintptr_t root=0x802818u;
 uint32_t high=*(volatile uint32_t *)(root+36u),low=*(volatile uint32_t *)(root+32u);
 uint32_t kind=*(volatile uint8_t *)(root+29u),role=*(volatile uint8_t *)(root+28u);
 uint32_t duplicate=opencfw_em9305_command_duplicate_307c5c(role,kind,low,high);
 if(duplicate!=0u)return duplicate;
 uint32_t capacity=*(volatile uint8_t *)(record+614u),type=*(volatile uint8_t *)root;
 if(capacity==0u)goto reject;
 uint32_t features=*(volatile uint32_t *)(uintptr_t)0x805a94u;
 uint32_t requested=*(volatile uint8_t *)(root+31u);
 uint32_t allowed=((features>>9u)&4u)|((features&(1u<<8u))!=0u?3u:1u);
 if((requested&~allowed)!=0u||requested>=5u||(0x16u&(1u<<requested))==0u)goto reject;
 if(type==42u){
  uintptr_t config=0x802848u;
  uint32_t a=*(volatile uint8_t *)config;
  if(a>=16u)goto packet_reject;
  uint32_t b=*(volatile uint8_t *)(config+1u);
  if(b<6u)goto packet_reject;
  a=*(volatile uint8_t *)(config+2u);
  if(a==0u||a==255u||a>=b)goto packet_reject;
  a=*(volatile uint8_t *)(config+3u);
  if(a<2u)goto packet_reject;
 }
 uintptr_t event=opencfw_em9305_wsf_event_allocate(56u);
 if(event==0u)goto terminate;
 *(volatile uint16_t *)(event+2u)=268u;
 uint32_t half=*(volatile uint16_t *)(root+4u);
 *(volatile uint16_t *)(event+4u)=(uint16_t)half;
 (void)opencfw_em9305_memcpy((void *)(event+6u),(const void *)(root+6u),18u);
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 half=*(volatile uint16_t *)(record+262u);
 uint32_t id=opencfw_em9305_associated_slot_sdiv((uint32_t)(record-base),912u);
 *(volatile uint16_t *)(event+24u)=(uint8_t)id;
 uint32_t value=*(volatile uint16_t *)(root+24u);
 *(volatile uint16_t *)(event+28u)=(uint16_t)half;
 *(volatile uint16_t *)(event+26u)=(uint16_t)value;
 value=*(volatile uint16_t *)(root+26u);*(volatile uint16_t *)(event+30u)=(uint16_t)value;
 value=*(volatile uint8_t *)(root+28u);*(volatile uint8_t *)(event+32u)=(uint8_t)value;
 value=*(volatile uint8_t *)(root+29u);*(volatile uint8_t *)(event+33u)=(uint8_t)value;
 value=*(volatile uint8_t *)(root+30u);*(volatile uint8_t *)(event+34u)=(uint8_t)value;
 value=*(volatile uint8_t *)(root+31u);uint32_t index=value-2u;
 value=index<7u?opencfw_em9305_init_response_types_334496[(int8_t)index]:1u;
 *(volatile uint8_t *)(event+35u)=(uint8_t)value;
 high=*(volatile uint32_t *)(root+36u);low=*(volatile uint32_t *)(root+32u);type=*(volatile uint8_t *)root;
 *(volatile uint32_t *)(event+40u)=high;*(volatile uint32_t *)(event+36u)=low;
 value=*(volatile uint16_t *)(root+40u);*(volatile uint16_t *)(event+44u)=(uint16_t)value;
 value=*(volatile uint32_t *)(root+44u);*(volatile uint32_t *)(event+48u)=value;
 value=*(volatile uint8_t *)(root+48u);*(volatile uint8_t *)(event+52u)=(uint8_t)value;
 value=*(volatile uint8_t *)(root+49u);*(volatile uint8_t *)(event+53u)=(uint8_t)value;
 value=*(volatile uint8_t *)(root+50u);uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint8_t *)(event+54u)=(uint8_t)value;
 value=*(volatile uint8_t *)(root+51u);
 *(volatile uint8_t *)(event+46u)=type==42u;
 *(volatile uint8_t *)(event+55u)=(uint8_t)value;
 (void)opencfw_em9305_wsf_task_message_send(handler,event);
 goto terminate;
packet_reject:
 (void)opencfw_em9305_init_response_packet_326a84(record);goto terminate;
reject:
 if(type==42u)(void)opencfw_em9305_init_response_packet_326a84(record);
terminate:
 return opencfw_em9305_receive_terminate_325c08(record,110u);
}
