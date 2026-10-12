extern uint32_t opencfw_em9305_config_phy_pair_valid_332f80(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_config_basic_apply_3087ec(uintptr_t,uintptr_t);
static inline uint32_t opencfw_em9305_config_basic_stride(uint32_t i)
{uint32_t result;__asm__ volatile("mpy %0,%1,10":"=r"(result):"r"(i));return result;}
static uint32_t opencfw_em9305_config_basic_time(uint32_t length,uint32_t phy)
{
 if(!length)return 0u;
 if(phy==1u)return length*8u+80u;
 if(phy==4u)return length*64u+720u;
 if(phy==2u)return 44u+length*4u;
 return 0u;
}
/* Native30d00c..30d204: complete basic configuration validation, clamp and apply. */
uint32_t opencfw_em9305_command_config_basic_30d00c(uintptr_t input,uintptr_t output)
{
 uint32_t count=*(volatile uint8_t *)(input+20u);
 if(count-1u>=16u)return 18u;
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 if(*(volatile uint8_t *)(config+53u)<count)return 9u;
 uintptr_t rows=*(volatile uint32_t *)(input+24u);
 uint32_t first_length=0u,second_length=0u;
 for(uint32_t i=0u;i<count;++i){first_length=*(volatile uint16_t *)(rows+2u+i*10u);if(first_length)break;}
 for(uint32_t i=0u;i<count;++i){second_length=*(volatile uint16_t *)(rows+4u+i*10u);if(second_length)break;}
 if(*(volatile uint8_t *)input>239u)return 18u;
 uint32_t first_time=*(volatile uint32_t *)(input+4u);
 if((first_length&&first_time<255u)||first_time>0xfffffu)return 18u;
 uint32_t second_time=*(volatile uint32_t *)(input+8u);
 if((second_length&&second_time<255u)||second_time>0xfffffu)return 18u;
 if(*(volatile uint8_t *)(input+12u)>=8u)return 18u;
 if(*(volatile uint8_t *)(input+13u)>=2u)return 18u;
 if(*(volatile uint8_t *)(input+14u)>=2u)return 18u;
 for(uint32_t i=0u;i<count;++i){
  uintptr_t row=rows+opencfw_em9305_config_basic_stride(i);
  if(*(volatile uint8_t *)row>239u)return 18u;
  uint32_t a=*(volatile uint16_t *)(row+2u);if(a>4095u)return 18u;
  uint32_t b=*(volatile uint16_t *)(row+4u);if(b>4095u||(a|b)==0u)return 18u;
  if(*(volatile uint8_t *)(row+6u)==0u)return 17u;
  if(*(volatile uint8_t *)(row+7u)==0u)return 17u;
  if(*(volatile uint8_t *)(row+8u)>=16u)*(volatile uint8_t *)(row+8u)=15u;
  else if(*(volatile uint8_t *)(row+9u)>=16u)*(volatile uint8_t *)(row+9u)=15u;
 }
 uint32_t live_count,i=0u;
 for(;;){
  live_count=*(volatile uint8_t *)(input+20u);
  if(i>=live_count)break;
  rows=*(volatile uint32_t *)(input+24u);
  uintptr_t row=rows+i*10u;
  uint32_t second=*(volatile uint8_t *)(row+7u),first=*(volatile uint8_t *)(row+6u);
  if(opencfw_em9305_config_phy_pair_valid_332f80(first,second)==0u)return 17u;
  first=*(volatile uint8_t *)(row+6u);if(first&~7u)return 17u;
  second=*(volatile uint8_t *)(row+7u);if(second&~7u)return 17u;
  if(((first-1u)&first)!=0u||((second-1u)&second)!=0u)return 17u;
  ++i;
 }
 if(live_count){
  first_time=*(volatile uint32_t *)(input+4u);
  rows=*(volatile uint32_t *)(input+24u);
  for(uint32_t j=0u;j<live_count;++j){uintptr_t row=rows+opencfw_em9305_config_basic_stride(j);
   uint32_t a=*(volatile uint16_t *)(row+2u),ta=0u;
   if(a)ta=opencfw_em9305_config_basic_time(a,*(volatile uint8_t *)(row+6u));
   uint32_t b=*(volatile uint16_t *)(row+4u),tb=0u;
   if(b)tb=opencfw_em9305_config_basic_time(b,*(volatile uint8_t *)(row+7u));
   if(ta>first_time)return 18u;
   if(tb>*(volatile uint32_t *)(input+8u))return 18u;
  }
 }
 if((uint16_t)(*(volatile uint16_t *)(input+16u)-4001u)<61540u)return 18u;
 if((uint16_t)(*(volatile uint16_t *)(input+18u)-4001u)<61540u)return 18u;
 (void)opencfw_em9305_memset((void *)output,0u,live_count*2u);
 return opencfw_em9305_config_basic_apply_3087ec(input,output)&255u;
}
