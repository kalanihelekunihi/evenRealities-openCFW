/* Native3133a0..3133b0: exact scheduler root clear and retained R0. */
uint32_t opencfw_em9305_init_scheduler_clear_3133a0(void)
{
 *(volatile uint16_t *)(uintptr_t)0x805f1cu=0u;
 *(volatile uint32_t *)(uintptr_t)0x805f18u=0u;
 *(volatile uint32_t *)(uintptr_t)0x805f14u=0u;
 *(volatile uint8_t *)(uintptr_t)0x805f04u=0u;
 return 0x805f04u;
}
/* Native3075cc..307660: direct versus22-entry broadcast dispatch, captured
 * message published before callbacks; reset runs22 registered initializers,
 * emits exact4-byte event with latch clear before event provider. */
uint32_t opencfw_em9305_init_message_3075cc(uintptr_t message)
{
 uint32_t type=*(volatile uint8_t *)(message+2u);
 *(volatile uint32_t *)(uintptr_t)0x805c78u=(uint32_t)message;
 if(type!=255u){
  uintptr_t callback=*(volatile uint32_t *)(uintptr_t)(0x802950u+type*4u);
  if(callback!=0u)(void)((uint32_t (*)(uintptr_t,uintptr_t))callback)(message,callback);
 }else{
  if(*(volatile uint8_t *)(message+3u)==0u)*(volatile uint8_t *)(uintptr_t)0x8051f8u=1u;
  for(uint32_t i=1u;i<=22u;i++){
   uintptr_t callback=*(volatile uint32_t *)(uintptr_t)(0x802950u+i*4u);
   if(callback!=0u)(void)((uint32_t (*)(uintptr_t,uintptr_t))callback)(message,callback);
  }
 }
 uint32_t pending=*(volatile uint8_t *)(uintptr_t)0x8051f8u;
 if(pending==0u)return 0u;
 uint32_t busy=*(volatile uint8_t *)(uintptr_t)0x805a79u;
 if(busy!=0u)return busy;
 (void)opencfw_em9305_radio_address_reset_303e38();
 (void)opencfw_em9305_radio_reset_30390c();
 (void)opencfw_em9305_address_count_clear_303700();
 uint32_t value=opencfw_em9305_init_scheduler_clear_3133a0();
 (void)opencfw_em9305_init_state_30e9a4(value);
 for(uint32_t i=1u;i<=22u;i++){
  uintptr_t callback=*(volatile uint32_t *)(uintptr_t)(0x805200u+i*4u);
  if(callback!=0u)(void)((uint32_t (*)(uintptr_t))callback)(callback);
 }
 _Alignas(4) uint32_t event=1u<<16u;
 *(volatile uint8_t *)(uintptr_t)0x8051f8u=0u;
 return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)&event);
}
