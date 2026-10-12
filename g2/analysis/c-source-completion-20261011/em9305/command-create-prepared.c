/* Native307ca8..307cb8: product state equals0. */
uint32_t opencfw_em9305_command_idle_307ca8(void)
{return *(volatile uint8_t *)(uintptr_t)0x8051a4u==0u;}
/* Native3213b0..3213d0: six byte rows summed, low8 return. */
uint32_t opencfw_em9305_command_count_3213b0(void)
{
 uint32_t sum=0u;
 for(uint32_t i=0u;i<6u;++i)sum+=*(volatile uint8_t *)(uintptr_t)(0x803d78u+i*784u);
 return sum&255u;
}
extern uint32_t opencfw_em9305_command_duplicate_307c5c(uint32_t,uint32_t,uint32_t,uint32_t);
/* Native30c488..30c54c: full create guards and24-byte command projection. */
uint32_t opencfw_em9305_command_create_30c488(uintptr_t input)
{
 if(opencfw_em9305_ll_stream_gate_30e510()==0u)return 12u;
 if(*(volatile uint8_t *)(input+2u)>=2u)return 18u;
 if(*(volatile uint8_t *)(input+1u)>=16u)return 18u;
 if(*(volatile uint16_t *)(input+8u)>499u)return 18u;
 if(*(volatile uint8_t *)input>=8u)return 18u;
 uint32_t timing=*(volatile uint16_t *)(input+10u);
 if((uint16_t)(timing-16385u)<49161u)return 18u;
 if(*(volatile uint8_t *)(input+12u)==31u)return 12u;
 if(opencfw_em9305_command_idle_307ca8()==0u)return 12u;
 uintptr_t address=*(volatile uint32_t *)(input+4u);
 uint32_t kind=*(volatile uint8_t *)(input+2u),role=*(volatile uint8_t *)(input+1u);
 uint64_t packed=opencfw_em9305_controller_pack_address(address);
 if(opencfw_em9305_command_duplicate_307c5c(role,kind,(uint32_t)packed,(uint32_t)(packed>>32u))!=0u)return 11u;
 if(opencfw_em9305_command_count_3213b0()>=6u)return 7u;
 uintptr_t message=opencfw_em9305_wsf_event_allocate(24u);
 if(message==0u)return 0u;
 *(volatile uint16_t *)(message+2u)=267u;
 address=*(volatile uint32_t *)(input+4u);
 packed=opencfw_em9305_controller_pack_address(address);
 kind=*(volatile uint8_t *)(input+2u);role=*(volatile uint8_t *)(input+1u);
 *(volatile uint32_t *)(message+12u)=(uint32_t)(packed>>32u);
 *(volatile uint32_t *)(message+8u)=(uint32_t)packed;
 *(volatile uint8_t *)(message+7u)=(uint8_t)kind;
 *(volatile uint8_t *)(message+6u)=(uint8_t)role;
 *(volatile uint32_t *)(message+16u)=*(volatile uint32_t *)(input+8u);
 uint32_t flags=*(volatile uint8_t *)input,last=*(volatile uint8_t *)(input+12u);
 *(volatile uint8_t *)(message+21u)=(uint8_t)last;
 uint32_t bit1=(flags>>1u)&1u;
 *(volatile uint8_t *)(message+5u)=(uint8_t)bit1;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint8_t *)(message+20u)=(uint8_t)(bit1?0u:(flags>>2u)&1u);
 *(volatile uint8_t *)(message+4u)=(uint8_t)(flags&1u);
 (void)opencfw_em9305_wsf_task_message_send(handler,message);
 return 0u;
}
