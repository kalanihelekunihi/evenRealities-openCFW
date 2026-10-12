extern uint32_t opencfw_em9305_init_secondary_start_3213f8(uintptr_t);
/* Complete native30e4ac..30e4b8 byte count helper, native R0 is address. */
uint32_t opencfw_em9305_init_secondary_count_up_30e4ac(void)
{
 uint32_t count=*(volatile uint8_t *)(uintptr_t)0x805a77u;
 *(volatile uint8_t *)(uintptr_t)0x805a77u=(uint8_t)(count+1u);
 return 0x805a77u;
}
/* Complete native318fe8..31907e source creation action. */
uint32_t opencfw_em9305_init_secondary_action_318fe8(uintptr_t incoming,uint32_t offset,uint32_t state)
{
 (void)incoming;(void)offset;(void)state;
 uintptr_t message=*(volatile uint32_t *)(uintptr_t)0x805c80u;
 (void)opencfw_em9305_common_request_30455c(1u);
 uint32_t flag=*(volatile uint8_t *)(message+4u);
 if(flag!=0u){(void)opencfw_em9305_init_secondary_count_up_30e4ac();flag=*(volatile uint8_t *)(message+4u);}
 uint32_t high=*(volatile uint32_t *)(message+12u),low=*(volatile uint32_t *)(message+8u);
 uint32_t b=*(volatile uint8_t *)(message+7u),a=*(volatile uint8_t *)(message+6u),option=*(volatile uint8_t *)(message+21u);
 uintptr_t root=0x8051a4u;
 *(volatile uint8_t *)(root+4u)=(uint8_t)flag;
 *(volatile uint32_t *)(root+12u)=high;*(volatile uint32_t *)(root+8u)=low;
 *(volatile uint8_t *)(root+6u)=(uint8_t)b;*(volatile uint8_t *)(root+5u)=(uint8_t)a;
 *(volatile uint8_t *)(root+16u)=(uint8_t)option;
 uintptr_t record=opencfw_em9305_init_secondary_allocate_316e74();
 if(record!=0u){
  a=*(volatile uint8_t *)(message+6u);uint32_t period=*(volatile uint16_t *)(message+18u);
  *(volatile uint32_t *)(root+20u)=(uint32_t)record;
  high=*(volatile uint32_t *)(message+12u);low=*(volatile uint32_t *)(message+8u);
  flag=*(volatile uint8_t *)(message+4u);b=*(volatile uint8_t *)(message+7u);
  uint32_t half=*(volatile uint16_t *)(message+16u),enabled=*(volatile uint8_t *)(message+5u),other=*(volatile uint8_t *)(message+20u);
  uintptr_t extra=record+624u;
  *(volatile uint8_t *)(extra+1u)=(uint8_t)a;
  period=(uint32_t)(uint16_t)period*10u;
  *(volatile uint8_t *)extra=(uint8_t)flag;
  enabled=enabled!=0u;other=other!=0u;
  *(volatile uint8_t *)(record+9u)=11u;
  *(volatile uint8_t *)(extra+2u)=(uint8_t)b;
  *(volatile uint16_t *)(extra-8u)=(uint16_t)half;
  *(volatile uint32_t *)(record+632u)=high;*(volatile uint32_t *)(record+628u)=low;
  *(volatile uint8_t *)(record+6u)=(uint8_t)enabled;*(volatile uint8_t *)(record+7u)=(uint8_t)other;
  *(volatile uint32_t *)(record+620u)=period;
 }else record=*(volatile uint32_t *)(root+20u);
 (void)opencfw_em9305_init_secondary_start_3213f8(record);
 return opencfw_em9305_command_count_30e4bc();
}
