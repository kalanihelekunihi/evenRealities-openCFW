/* Native303718..303788: swap last row into match, preserving trailing2 bytes. */
uint32_t opencfw_em9305_address_remove_303718(uint32_t kind,uint32_t low,uint32_t high,uint32_t selector)
{
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805bfcu;
 uint32_t count=*(volatile uint8_t *)(uintptr_t)0x80160au;
 uintptr_t row=base;
 for(uint32_t index=0u;index<count;++index,row+=12u){
  if(*(volatile uint8_t *)(row+8u)!=kind)continue;
  uint32_t upper=*(volatile uint32_t *)(row+4u),lower=*(volatile uint32_t *)row;
  if(((upper^high)|(lower^low))!=0u)continue;
  if(*(volatile uint8_t *)(row+9u)!=selector)continue;
  uint32_t last=count-1u;
  if(count>=2u&&index!=last){
   uintptr_t tail=base+last*12u;
   uint32_t tags=*(volatile uint16_t *)(tail+8u);
   *(volatile uint16_t *)(row+8u)=(uint16_t)tags;
   lower=*(volatile uint32_t *)tail;
   upper=*(volatile uint32_t *)(tail+4u);
   *(volatile uint32_t *)row=lower;
   *(volatile uint32_t *)(row+4u)=upper;
  }
  *(volatile uint8_t *)(uintptr_t)0x80160au=(uint8_t)last;
  return 1u;
 }
 return 0u;
}
/* Native30ca1c..30ca68: full delete command guards and captured address pair. */
uint32_t opencfw_em9305_command_address_remove_30ca1c(uintptr_t input)
{
 uint32_t gate=opencfw_em9305_ll_stream_gate_30e510();
 uint32_t flag=*(volatile uint8_t *)(uintptr_t)0x805a77u;
 if(flag!=0u||gate==0u)return 12u;
 if(*(volatile uint8_t *)input>1u)return 18u;
 if(*(volatile uint8_t *)(input+8u)>=16u)return 18u;
 if(opencfw_em9305_address_busy_307cb8()!=0u)return 12u;
 uintptr_t address=*(volatile uint32_t *)(input+4u);
 uint64_t packed=opencfw_em9305_controller_pack_address(address);
 uint32_t selector=*(volatile uint8_t *)(input+8u),kind=*(volatile uint8_t *)input;
 return opencfw_em9305_address_remove_303718(kind,(uint32_t)packed,(uint32_t)(packed>>32u),selector)!=0u?0u:66u;
}
