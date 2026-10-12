/* Full native31b4e0..31b612. Genuine new child imports remain explicit. */
extern uintptr_t opencfw_em9305_init_connection_allocate_316c58(void);
extern uint32_t opencfw_em9305_init_connection_release_31ad90(uintptr_t);
extern uint32_t opencfw_em9305_init_connection_parameters_32074c(uintptr_t,uint32_t,uint32_t,uint32_t);
uint32_t opencfw_em9305_init_connection_query_31b21c(uint32_t id,uintptr_t output)
{
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uintptr_t record=base+(uint16_t)id*912u;
 if(*(volatile uint8_t *)record==0u)return 0u;
 if(*(volatile uint8_t *)(record+64u)!=4u)return 0u;
 uint32_t value=*(volatile uint32_t *)(record+24u);
 if(output!=0u)*(volatile uint32_t *)output=*(volatile uint32_t *)(record+28u);
 return value;
}
uint32_t opencfw_em9305_init_secondary_count_up_30e4cc(void)
{uint32_t value=*(volatile uint8_t *)(uintptr_t)0x805a76u;*(volatile uint8_t *)(uintptr_t)0x805a76u=(uint8_t)(value+1u);return 0x805a76u;}
uint32_t opencfw_em9305_init_schedule_start_320b08(void)
{
 uint32_t guard=opencfw_em9305_auxiliary_guard_interval();uintptr_t record=0x803b94u;
 uint32_t period=*(volatile uint16_t *)(record+62u);
 *(volatile uint32_t *)(record+164u)=guard+1228u;
 period=(uint16_t)period*625u;
 *(volatile uint16_t *)(record+148u)=0u;
 *(volatile uint32_t *)(record+168u)=period;
 (void)opencfw_em9305_auxiliary_insert_313220(record+152u);
 uint32_t value=*(volatile uint32_t *)(record+160u);
 *(volatile uint32_t *)(record+56u)=value;return value;
}
uint32_t opencfw_em9305_init_state_action_31b4e0(uintptr_t incoming,uint32_t state)
{
 (void)incoming;(void)state;
 uintptr_t request=*(volatile uint32_t *)(uintptr_t)0x805c78u;
 uintptr_t connection=opencfw_em9305_init_connection_allocate_316c58();
 uint32_t status;
 if(connection==0u)status=9u;
 else {
  uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
  uint32_t minimum=*(volatile uint16_t *)(request+4u)*1250u;
  uint32_t maximum=*(volatile uint16_t *)(request+6u)*1250u;
  uint32_t extent=*(volatile uint16_t *)(connection+592u);
  uint32_t id=(uint8_t)opencfw_em9305_associated_slot_sdiv((uint32_t)(connection-base),912u);
  uint32_t allocation;
  uint32_t ok=opencfw_em9305_associated_slot_allocate_3133b4(id,0u,minimum,maximum,extent,(uintptr_t)&allocation,(uintptr_t)opencfw_em9305_init_connection_query_31b21c);
  if(ok!=0u){
   base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
   struct opencfw_em9305_native_product_pair product=opencfw_em9305_native_mpydu_329154(allocation,0x1a36e3u);
   uintptr_t record=0x803bd0u;
   id=(uint8_t)opencfw_em9305_associated_slot_sdiv((uint32_t)(connection-base),912u);
   *(volatile uint16_t *)(record+62u)=(uint16_t)((product.low>>31)|(product.high<<1));
   *(volatile uint16_t *)(record+60u)=(uint8_t)id;
   uint32_t low=*(volatile uint32_t *)(request+16u),high=*(volatile uint32_t *)(request+20u);
   *(volatile uint32_t *)record=low;*(volatile uint32_t *)(record+4u)=high;
   (void)opencfw_em9305_common_request_30455c(1u);
   (void)opencfw_em9305_command_count_30e4bc();
   uint32_t flags=*(volatile uint8_t *)(record+6u);
   *(volatile uint8_t *)(uintptr_t)0x805a74u=1u;
   if((flags&1u)!=0u)(void)opencfw_em9305_init_secondary_count_up_30e4cc();
   high=*(volatile uint32_t *)(request+28u);low=*(volatile uint32_t *)(request+24u);
   uint32_t kind=*(volatile uint8_t *)(request+32u);
   *(volatile uint8_t *)(uintptr_t)0x803d24u=1u;*(volatile uint16_t *)(uintptr_t)0x803d22u=1u;
   (void)opencfw_em9305_init_connection_parameters_32074c(request+4u,kind,low,high);
   (void)opencfw_em9305_radio_transfer_31dd88(connection,record+8u,0u);
   high=*(volatile uint32_t *)(request+28u);low=*(volatile uint32_t *)(request+24u);kind=*(volatile uint8_t *)(request+32u);
   *(volatile uint16_t *)(connection+892u)=0xffffu;*(volatile uint8_t *)(connection+890u)=0xffu;
   *(volatile uint32_t *)(connection+520u)=high;*(volatile uint32_t *)(connection+516u)=low;
   *(volatile uint8_t *)(connection+524u)=(uint8_t)kind;
   uint32_t result=opencfw_em9305_init_schedule_start_320b08();
   *(volatile uint8_t *)(uintptr_t)0x805a75u=1u;return result;
  }
  (void)opencfw_em9305_init_connection_release_31ad90(connection);status=13u;
 }
 uint32_t high=*(volatile uint32_t *)(request+28u),low=*(volatile uint32_t *)(request+24u),kind=*(volatile uint8_t *)(request+32u);
 (void)opencfw_em9305_init_state_status_send_3257a4(status,kind,low,high);
 uintptr_t message=opencfw_em9305_wsf_event_allocate(4u);
 if(message==0u)return 0u;
 *(volatile uint16_t *)(message+2u)=771u;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 return opencfw_em9305_wsf_task_message_send(handler,message);
}
