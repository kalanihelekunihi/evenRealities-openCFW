/* Native318988..3189c8: clock accuracy class plus configured offset. */
uint32_t opencfw_em9305_compose_accuracy_318988(void)
{
 uintptr_t configuration=*(volatile uint32_t *)(uintptr_t)0x805c18u;
 uint32_t metric=*(volatile uint16_t *)configuration;
 uint32_t value=metric<21u?7u:metric<31u?6u:metric<51u?5u:metric<76u?4u:metric<101u?3u:metric<151u?2u:metric<251u?1u:0u;
 return (uint8_t)(value+*(volatile uint8_t *)(uintptr_t)0x805aa8u);
}
/* Native324438..324590: full 18-byte auxiliary schedule descriptor. */
uint32_t opencfw_em9305_compose_aux_encode_324438(uintptr_t record,uintptr_t output)
{
 volatile uint8_t *r=(volatile uint8_t *)record,*o=(volatile uint8_t *)output;
 uint32_t enabled=r[2809];uint32_t next=*(volatile uint32_t *)(record+388u);
 if(enabled!=0u){uint32_t slots=r[799];if((slots&127u)!=0u){
  uint32_t stride=*(volatile uint32_t *)(record+792u);
  uint32_t period=*(volatile uint32_t *)(record+700u);
  uint32_t product=opencfw_em9305_native_mpywhl(stride,slots);
  next=next+period-product;
 }}
 uint32_t elapsed;
 for(;;){uint32_t previous=*(volatile uint32_t *)(record+2476u);
  elapsed=opencfw_em9305_auxiliary_elapsed_303f8c(next,previous);
  if(elapsed>=301u)break;
  next+=*(volatile uint32_t *)(record+700u);
 }
 uint32_t previous=*(volatile uint32_t *)(record+2476u);
 elapsed=opencfw_em9305_auxiliary_elapsed_303f8c(next,previous);
 uint32_t quotient,selector;
 if(elapsed<0x3bfc4u){quotient=opencfw_em9305_associated_packet_high_product(elapsed,0x11111112u)>>1;selector=0u;}
 else{selector=elapsed<0x258000u?1u:0u;if(elapsed>0x257fffu)elapsed=0u;
  uint32_t high=opencfw_em9305_associated_packet_high_product(elapsed,0x69d0369eu);
  quotient=((elapsed<<1)+elapsed+high)>>10;
 }
 o[0]=(uint8_t)quotient;o[1]=(uint8_t)((quotient|(selector<<13))>>8);
 uint32_t period=*(volatile uint32_t *)(record+700u);
 struct opencfw_em9305_native_product_pair product=opencfw_em9305_native_mpydu_329154(period,0x1a36e3u);
 o[2]=(uint8_t)((product.high<<1)|(product.low>>31));
 period=*(volatile uint32_t *)(record+700u);
 o[3]=(uint8_t)(opencfw_em9305_associated_packet_high_product(period,0x1a36e3u)>>7);
 uint32_t access=*(volatile uint32_t *)(record+720u);
 uint32_t upper=*(volatile uint32_t *)(record+724u);
 uint32_t accuracy=opencfw_em9305_compose_accuracy_318988();
 o[7]=(uint8_t)(access>>24);o[4]=(uint8_t)access;o[6]=(uint8_t)(access>>16);o[5]=(uint8_t)(access>>8);
 o[8]=(uint8_t)((accuracy<<5)+(upper&31u));
 o[9]=(uint8_t)*(volatile uint32_t *)(record+432u);
 o[10]=(uint8_t)(*(volatile uint32_t *)(record+432u)>>8);
 o[11]=(uint8_t)*(volatile uint16_t *)(record+434u);o[12]=r[435];
 o[13]=(uint8_t)*(volatile uint32_t *)(record+436u);
 o[14]=(uint8_t)(*(volatile uint32_t *)(record+436u)>>8);
 o[15]=(uint8_t)*(volatile uint16_t *)(record+438u);
 uint32_t result;
 if(r[2809]!=0u){uint32_t slots=r[799];if((slots&127u)!=0u){
  o[16]=(uint8_t)(r[376]+1u);
  result=(*(volatile uint16_t *)(record+376u)+1u)>>8;
  o[17]=(uint8_t)result;return result;
 }}
 o[16]=r[376];result=r[377];o[17]=(uint8_t)result;return result;
}
