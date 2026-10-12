/* Native31b3b8..31b4a0: complete state report constructor and cleanup.
 * Unwritten allocation bytes48..51/55..59/85 are retained, not invented zeroes. */
uint32_t opencfw_em9305_init_state_action_31b3b8(uintptr_t incoming,uint32_t state)
{
 (void)incoming;(void)state;
 if(*(volatile uint8_t *)(uintptr_t)0x805a74u==0u)return opencfw_em9305_init_state_action_31b6b0(0u,0u);
 uintptr_t message=opencfw_em9305_wsf_event_allocate(88u);
 uintptr_t record=0x803b94u;
 if(message!=0u){
  uintptr_t input=record+68u;
  uint32_t index=*(volatile uint16_t *)(input+52u);
  *(volatile uint16_t *)(message+2u)=0x3f01u;
  uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
  *(volatile uint16_t *)message=(uint8_t)index;
  *(volatile uint8_t *)(base+(uint16_t)index*912u+2u)=0u;
  (void)opencfw_em9305_memcpy((void *)(message+4u),(const void *)input,44u);
  uintptr_t addresses=0x803d04u;
  uint32_t original=*(volatile uint8_t *)(addresses+19u);
  *(volatile uint8_t *)(message+52u)=(uint8_t)original;
  uint32_t current=*(volatile uint8_t *)(addresses+19u);
  uint32_t previous=*(volatile uint8_t *)(addresses+18u);
  uint32_t low_second,high_second;
  uint32_t changed=current!=previous?1u:0u;
  if(changed==0u){
   uint32_t high_first=*(volatile uint32_t *)(addresses+4u);
   high_second=*(volatile uint32_t *)(addresses+12u);
   uint32_t low_first=*(volatile uint32_t *)addresses;
   low_second=*(volatile uint32_t *)(addresses+8u);
   changed=((high_first^high_second)|(low_first^low_second))!=0u?1u:0u;
  }
  if(changed!=0u){
   *(volatile uint8_t *)(message+52u)=(uint8_t)(original|2u);
   high_second=*(volatile uint32_t *)(addresses+12u);
   low_second=*(volatile uint32_t *)(addresses+8u);
   previous=*(volatile uint8_t *)(addresses+18u);
   current=*(volatile uint8_t *)(addresses+19u);
  }
  *(volatile uint32_t *)(message+72u)=0u;*(volatile uint32_t *)(message+68u)=0u;
  *(volatile uint32_t *)(message+60u)=low_second;*(volatile uint32_t *)(message+64u)=high_second;
  uint32_t high_first=*(volatile uint32_t *)(addresses+4u);
  uint32_t low_first=*(volatile uint32_t *)addresses;
  changed=current!=previous?1u:0u;
  if(changed==0u){uint32_t high_other=*(volatile uint32_t *)(addresses+12u);
   uint32_t low_other=*(volatile uint32_t *)(addresses+8u);
   changed=((high_other^high_first)|(low_other^low_first))!=0u?1u:0u;
  }
  if(changed!=0u){*(volatile uint32_t *)(message+68u)=low_first;*(volatile uint32_t *)(message+72u)=high_first;}
  uintptr_t parameters=0x803c04u;
  uint32_t high=*(volatile uint32_t *)(parameters+4u);
  uint32_t low=*(volatile uint32_t *)parameters;
  *(volatile uint32_t *)(message+80u)=high;*(volatile uint32_t *)(message+76u)=low;
  uint32_t flags=*(volatile uint8_t *)(parameters+13u);
  uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
  *(volatile uint16_t *)(message+86u)=0xffffu;
  *(volatile uint8_t *)(message+53u)=(uint8_t)flags;
  *(volatile uint8_t *)(message+84u)=0xffu;
  *(volatile uint8_t *)(message+54u)=1u;
  (void)opencfw_em9305_wsf_task_message_send(handler,message);
 }
 (void)opencfw_em9305_common_release_304588(1u);
 return opencfw_em9305_init_state_cleanup_325740(record);
}
