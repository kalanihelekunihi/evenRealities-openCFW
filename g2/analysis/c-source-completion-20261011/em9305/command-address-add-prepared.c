/* Native303674..3036b2: bounded byte index makes MPYUW stride12 exact in C. */
uint32_t opencfw_em9305_address_append_303674(uint32_t kind,uint32_t low,uint32_t high,uint32_t selector)
{
 uint32_t capacity=*(volatile uint8_t *)(uintptr_t)0x80160bu;
 uint32_t count=*(volatile uint8_t *)(uintptr_t)0x80160au;
 if(count>=capacity)return 0u;
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805bfcu;
 *(volatile uint8_t *)(uintptr_t)0x80160au=(uint8_t)(count+1u);
 uintptr_t row=base+count*12u;
 *(volatile uint32_t *)(row+4u)=high;
 *(volatile uint32_t *)row=low;
 *(volatile uint8_t *)(row+8u)=(uint8_t)kind;
 *(volatile uint8_t *)(row+9u)=(uint8_t)selector;
 return 1u;
}
/* Native3036b4..3036fe: captured count, full-word address comparisons. */
uint32_t opencfw_em9305_address_contains_3036b4(uint32_t kind,uint32_t low,uint32_t high,uint32_t selector)
{
 uint32_t count=*(volatile uint8_t *)(uintptr_t)0x80160au;
 if(count==0u)return 0u;
 uintptr_t row=*(volatile uint32_t *)(uintptr_t)0x805bfcu;
 for(uint32_t i=0u;i<count;++i,row+=12u){
  if(*(volatile uint8_t *)(row+8u)!=kind)continue;
  uint32_t upper=*(volatile uint32_t *)(row+4u),lower=*(volatile uint32_t *)row;
  if(((upper^high)|(lower^low))!=0u)continue;
  if(*(volatile uint8_t *)(row+9u)==selector)return 1u;
 }
 return 0u;
}
/* Native30aed4..30af30: gate/argument/busy/duplicate guards and fresh fields. */
uint32_t opencfw_em9305_command_address_add_30aed4(uintptr_t input)
{
 uint32_t gate=opencfw_em9305_ll_stream_gate_30e510();
 uint32_t flag=*(volatile uint8_t *)(uintptr_t)0x805a77u;
 if(flag!=0u||gate==0u)return 12u;
 if(*(volatile uint8_t *)input>=2u)return 18u;
 if(*(volatile uint8_t *)(input+8u)>=16u)return 18u;
 if(opencfw_em9305_address_busy_307cb8()!=0u)return 12u;
 uintptr_t address=*(volatile uint32_t *)(input+4u);
 uint64_t packed=opencfw_em9305_controller_pack_address(address);
 uint32_t low=(uint32_t)packed,high=(uint32_t)(packed>>32u);
 uint32_t selector=*(volatile uint8_t *)(input+8u),kind=*(volatile uint8_t *)input;
 if(opencfw_em9305_address_contains_3036b4(kind,low,high,selector)!=0u)return 18u;
 selector=*(volatile uint8_t *)(input+8u);kind=*(volatile uint8_t *)input;
 return opencfw_em9305_address_append_303674(kind,low,high,selector)!=0u?0u:7u;
}
