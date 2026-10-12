/* Native325898..325980: three authentic spreading/addition passes,
 * low16 MPYUW, signed16 MPYW correction and channel-mask lookup. */
static uint32_t opencfw_em9305_init_channel_spread(uint32_t value)
{
 value=(value&0xf0f0u)|((value<<8u)&0xf0f00u);
 value=(value&0xcccc0u)|((value<<4u)&0x333300u);
 value=(value&0x2aaa80u)|((value<<2u)&0x555500u);
 return ((uint16_t)(value>>7u))*17u;
}
uint32_t opencfw_em9305_init_callback_325898(uintptr_t record)
{
 uint32_t first=*(volatile uint16_t *)(record+262u);
 uint32_t seed=*(volatile uint16_t *)(record+322u);
 uint32_t value=first^seed;
 value=opencfw_em9305_init_channel_spread(value)+seed;
 value=opencfw_em9305_init_channel_spread(value)+seed;
 value=opencfw_em9305_init_channel_spread(value)+seed;
 value^=seed;
 uint32_t quotient=((uint16_t)value*0xdd68u)>>21u;
 uint32_t channel=value+(uint32_t)((int32_t)(int16_t)quotient*-37);
 *(volatile uint8_t *)(record+270u)=(uint8_t)channel;
 uint32_t low=*(volatile uint32_t *)(record+276u);
 uint32_t high=*(volatile uint32_t *)(record+280u);
 uint32_t result=(uint32_t)((((uint64_t)high<<32u)|low)>>((uint16_t)channel&63u));
 if((result&1u)==0u){
  uint32_t count=*(volatile uint8_t *)(record+272u);
  uint32_t index=((uint16_t)count*(uint16_t)value)>>16u;
  channel=*(volatile uint8_t *)(record+284u+index);
 }
 return (uint8_t)channel;
}
/* Native306ab4..306ade: callback relocation and feature bit14. */
uint32_t opencfw_em9305_init_lower_306ab4(uint32_t incoming)
{
 (void)incoming;
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 *(volatile uint32_t *)(uintptr_t)0x8027e4u=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_325898;
 uint32_t feature=*(volatile uint8_t *)(config+4u);
 if(feature<9u)return feature;
 uint32_t flags=*(volatile uint32_t *)(uintptr_t)0x805b30u;
 *(volatile uint32_t *)(uintptr_t)0x805b30u=flags|(1u<<14u);return 0x805b30u;
}
