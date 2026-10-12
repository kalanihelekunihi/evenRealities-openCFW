/* Native324c98..324d6a: three bytewise permutations/MAM steps, native
 * low16 multiplier lanes, reciprocal37 and channel-map remap. */
uint32_t opencfw_em9305_associated_channel_seed_324c98(uintptr_t channels,uint32_t seed)
{
 uint32_t identity=*(volatile uint16_t *)(channels+48u),value=seed^identity;
 for(uint32_t round=0u;round<3u;++round){
  value=(value&0xf0f0u)|((value<<8u)&0xf0f00u);
  value=(value&0xcccc0u)|((value<<4u)&0x333300u);
  value=(value&0x2aaa80u)|((value<<2u)&0x555500u);
  value>>=7u;
  value=(value&65535u)*17u+identity;
 }
 uint32_t pseudo=value^identity;
 uint32_t quotient=((pseudo&65535u)*0xdd68u)>>21u;
 uint32_t choice=pseudo+(uint32_t)((int32_t)(int16_t)quotient*-37);
 uint32_t high=*(volatile uint32_t *)(channels+4u),low=*(volatile uint32_t *)channels;
 uint32_t index=((uint16_t)choice)&63u;
 uint32_t shifted=index==0u?low:index<32u?(low>>index)|(high<<(32u-index)):high>>(index-32u);
 if((shifted&1u)==0u){
  uint32_t count=*(volatile uint8_t *)(channels+45u);
  uint32_t remap=(count*(pseudo&65535u))>>16u;
  choice=*(volatile uint8_t *)(channels+8u+remap);
 }
 return (uint8_t)choice;
}
