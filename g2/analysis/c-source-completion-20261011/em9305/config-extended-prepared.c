extern uint32_t opencfw_em9305_config_extended_apply_308a3c(uintptr_t,uintptr_t);
static inline uint32_t opencfw_em9305_config_extended_stride(uint32_t i)
{uint32_t result;__asm__ volatile("mpy %0,%1,14":"=r"(result):"r"(i));return result;}
/* Native30d204..30d35a: complete extended validation. Output is cleared before any rejection. */
uint32_t opencfw_em9305_command_config_extended_30d204(uintptr_t input,uintptr_t output)
{
 uint32_t count=*(volatile uint8_t *)(input+19u);
 (void)opencfw_em9305_memset((void *)output,0u,count*2u);
 uint32_t minimum=(*(volatile uint8_t *)(uintptr_t)0x805a86u&128u)?4u:2u;
 if(*(volatile uint8_t *)input>239u)return 48u;
 if((uint32_t)(*(volatile uint32_t *)(input+4u)+0xfff00000u)<0xfff000ffu)return 48u;
 if((uint32_t)(*(volatile uint32_t *)(input+8u)+0xfff00000u)<0xfff000ffu)return 48u;
 if((uint32_t)(*(volatile uint8_t *)(input+12u)-1u)>=31u)return 48u;
 if((uint32_t)(*(volatile uint8_t *)(input+13u)-1u)>=31u)return 48u;
 uint32_t interval=*(volatile uint16_t *)(input+14u);
 if(interval<minimum||interval>=3201u)return 48u;
 if(*(volatile uint8_t *)(input+16u)>=8u||*(volatile uint8_t *)(input+17u)>=2u||*(volatile uint8_t *)(input+18u)>=2u)return 48u;
 count=*(volatile uint8_t *)(input+19u);
 if(count-1u>=16u)return 48u;
 uintptr_t rows=*(volatile uint32_t *)(input+20u);
 for(uint32_t i=0u;i<count;++i){uintptr_t row=rows+opencfw_em9305_config_extended_stride(i);
  if(*(volatile uint8_t *)row>239u)return 48u;
  if(*(volatile uint16_t *)(row+2u)>4095u||*(volatile uint16_t *)(row+4u)>4095u)return 48u;
  if(*(volatile uint16_t *)(row+6u)>4091u||*(volatile uint16_t *)(row+8u)>4091u)return 48u;
  if(*(volatile uint8_t *)(row+10u)==0u||*(volatile uint8_t *)(row+11u)==0u)return 48u;
  if(*(volatile uint8_t *)(row+12u)>=16u||*(volatile uint8_t *)(row+13u)>=16u)return 48u;
 }
 uint32_t limit=*(volatile uint8_t *)(rows+1u);
 if(limit<*(volatile uint8_t *)(rows+12u)||limit<*(volatile uint8_t *)(rows+13u))return 48u;
 uint32_t i=0u;
 do {rows=*(volatile uint32_t *)(input+20u);uintptr_t row=rows+i*14u;
  uint32_t second=*(volatile uint8_t *)(row+11u),first=*(volatile uint8_t *)(row+10u);
  if(opencfw_em9305_config_phy_pair_valid_332f80(first,second)==0u)return 17u;
  if(*(volatile uint8_t *)(row+10u)>=8u||*(volatile uint8_t *)(row+11u)>=8u)return 17u;
  ++i;count=*(volatile uint8_t *)(input+19u);
 }while(i<count);
 if(count){rows=*(volatile uint32_t *)(input+20u);
  for(i=0u;i<count;++i){uintptr_t row=rows+opencfw_em9305_config_extended_stride(i);
   if(*(volatile uint8_t *)(row+12u)&&*(volatile uint16_t *)(row+2u)==0u)return 18u;
   if(*(volatile uint8_t *)(row+13u)&&*(volatile uint16_t *)(row+4u)==0u)return 18u;
  }
 }
 return opencfw_em9305_config_extended_apply_308a3c(input,output);
}
