extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);
/* Native3082dc..308308: event774 with three explicit cleared fields. */
uint32_t opencfw_em9305_command_advertising_notify_3082dc(void)
{
 uintptr_t message=opencfw_em9305_wsf_event_allocate(24u);
 if(message==0u)return 0u;
 *(volatile uint16_t *)(message+2u)=774u;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint8_t *)(message+5u)=0u;
 *(volatile uint32_t *)(message+12u)=0u;
 *(volatile uint32_t *)(message+8u)=0u;
 return opencfw_em9305_wsf_task_message_send(handler,message);
}
/* Native306a7c..306a90: mask mismatch preserves incoming full R0. */
uint32_t opencfw_em9305_command_advertising_data_notify_306a7c(uint32_t mask)
{
 uint32_t configured=*(volatile uint8_t *)(uintptr_t)0x805400u;
 if((configured&mask)!=mask)return mask;
 return opencfw_em9305_command_advertising_notify_3082dc();
}
/* Native30e758..30e774: sparse four-byte error event, actual emitter child. */
uint32_t opencfw_em9305_command_advertising_error_30e758(uint32_t status)
{
 uint8_t event[4] __attribute__((aligned(4)));*(uint16_t *)(void *)event=0u;event[2]=3u;event[3]=(uint8_t)status;
 return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)event);
}
/* Native30aff8..30b094: captured enable and full mode/capability paths. */
void opencfw_em9305_command_advertising_enable_30aff8(uint32_t enable)
{
 uint32_t gate=opencfw_em9305_ll_connection_gate_30e524();
 uintptr_t state=0x805b84u;
 if(gate==0u){(void)opencfw_em9305_command_advertising_error_30e758(12u);return;}
 uint32_t mode=*(volatile uint8_t *)(state+12u);
 if(mode<5u&&(0x13u&(1u<<mode))!=0u){
  uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  uint32_t active=*(volatile uint8_t *)(uintptr_t)0x805a70u,capacity=*(volatile uint8_t *)(config+34u);
  if(active==capacity){(void)opencfw_em9305_command_advertising_error_30e758(12u);return;}
 }
 if(enable!=1u||opencfw_em9305_ll_stream_kind_valid_30e4dc(*(volatile uint8_t *)(state+13u))!=0u){
  uintptr_t message=opencfw_em9305_wsf_event_allocate(4u);if(message==0u)return;
  uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
  *(volatile uint8_t *)(message+3u)=(uint8_t)(1u+(enable==0u));
  *(volatile uint8_t *)(message+2u)=4u;
  (void)opencfw_em9305_wsf_task_message_send(handler,message);return;
 }
 mode=*(volatile uint8_t *)(state+12u);
 if(mode==3u){
  uint32_t high=*(volatile uint32_t *)(state+20u),low=*(volatile uint32_t *)(state+16u),kind=*(volatile uint8_t *)(state+14u);
  if(opencfw_em9305_radio_identity_exists_31445c(kind,low,high)!=0u){
   uintptr_t message=opencfw_em9305_wsf_event_allocate(4u);
   if(message!=0u){*(volatile uint16_t *)(message+2u)=260u;uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;(void)opencfw_em9305_wsf_task_message_send(handler,message);return;}
  }
 }
 (void)opencfw_em9305_command_advertising_error_30e758(18u);
}
