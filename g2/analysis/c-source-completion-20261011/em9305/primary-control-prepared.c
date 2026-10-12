/* Native30d528..30d548: fullword input, wrapped halfword validation. */
extern uint32_t opencfw_em9305_radio_primary_value_313744(uint32_t);
uint32_t opencfw_em9305_command_primary_30d528(uint32_t value)
{
 if((uint16_t)(value-0x7df1u)<0x8211u)return 18u;
 (void)opencfw_em9305_radio_primary_value_313744(value);
 return 0u;
}
/* Native30e3ec..30e3fa: child zero/nonzero projected to18/0. */
extern uint32_t opencfw_em9305_radio_primary_pair_310664(int32_t,int32_t);
uint32_t opencfw_em9305_command_primary_30e3ec(int32_t first,int32_t second)
{
 return opencfw_em9305_radio_primary_pair_310664(first,second)==0u?18u:0u;
}
/* Native30d8a0..30d8f8, authenticated 3027c8 six-bit shift semantics.
 * Capability loaded before busy gate; fullword enable shifted unchanged. */
uint32_t opencfw_em9305_command_primary_30d8a0(uint32_t index,uint32_t enable)
{
 uint32_t shift=index&63u;
 uint64_t bit=UINT64_C(1)<<shift;
 uint32_t low=(uint32_t)bit,high=(uint32_t)(bit>>32u);
 uint32_t supported_high=*(volatile uint32_t *)(uintptr_t)0x805b54u;
 uint32_t supported_low=*(volatile uint32_t *)(uintptr_t)0x805b50u;
 if(((high&supported_high)|(low&supported_low))==0u)return 17u;
 if(*(volatile uint8_t *)(uintptr_t)0x805a70u!=0u)return 12u;
 uint64_t value=(uint64_t)enable<<shift;
 uint32_t old_low=*(volatile uint32_t *)(uintptr_t)0x805a94u;
 uint32_t old_high=*(volatile uint32_t *)(uintptr_t)0x805a98u;
 low=(old_low&~low)|(uint32_t)value;
 high=(old_high&~high)|(uint32_t)(value>>32u);
 *(volatile uint32_t *)(uintptr_t)0x805a94u=low;
 *(volatile uint32_t *)(uintptr_t)0x805a98u=high;
 return 0u;
}

/* Native310664..310676: two halfword controls, first/second addresses reversed. */
uint32_t opencfw_em9305_radio_primary_pair_310664(int32_t first,int32_t second)
{
 *(volatile uint16_t *)(uintptr_t)0x8012eeu=(uint16_t)first;
 *(volatile uint16_t *)(uintptr_t)0x8012ecu=(uint16_t)second;
 return 1u;
}
