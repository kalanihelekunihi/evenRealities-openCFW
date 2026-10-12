/* Native30c54c..30c57e: disable allowed only in product state1. */
uint32_t opencfw_em9305_command_disable_30c54c(void)
{
 if(opencfw_em9305_ll_stream_gate_30e510()==0u)return 12u;
 if(opencfw_em9305_address_busy_307cb8()==0u)return 12u;
 uintptr_t message=opencfw_em9305_wsf_event_allocate(56u);
 if(message!=0u){
  *(volatile uint16_t *)(message+2u)=523u;
  uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
  (void)opencfw_em9305_wsf_task_message_send(handler,message);
 }
 return 0u;
}
/* Native30c600..30c64e: original full-width timeout guards, then halfword message. */
uint32_t opencfw_em9305_command_timeout_30c600(uint32_t timeout)
{
 if(opencfw_em9305_ll_stream_gate_30e510()==0u)return 12u;
 if(timeout>=3840u)return 18u;
 if(opencfw_em9305_command_ready_3213d0(timeout)==0u)return 66u;
 if(opencfw_em9305_address_busy_307cb8()!=0u)return 12u;
 uintptr_t message=opencfw_em9305_wsf_event_allocate(56u);
 if(message!=0u){
  *(volatile uint16_t *)message=(uint16_t)timeout;
  *(volatile uint16_t *)(message+2u)=525u;
  uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
  (void)opencfw_em9305_wsf_task_message_send(handler,message);
 }
 return 0u;
}
