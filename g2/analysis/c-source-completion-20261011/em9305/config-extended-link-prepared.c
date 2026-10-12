static const uint8_t opencfw_em9305_config_phy_values_33449d[7]={2u,1u,3u,1u,1u,1u,4u};
static inline uint32_t opencfw_em9305_config_extended_slot_stride(uint32_t i)
{uint32_t r;__asm__ volatile("mpyuw %0,%1,912":"=r"(r):"r"(i));return r;}
/* Native3272d8..32739c: full extended link projection, PHY mapping, seed and slot metadata. */
void opencfw_em9305_config_extended_link_update_3272d8(uintptr_t link,uintptr_t input,uintptr_t row)
{
 uint32_t policy=*(volatile uint16_t *)(input+16u);
 *(volatile uint16_t *)(link+482u)=(uint16_t)policy;
 uint32_t modeword=*(volatile uint32_t *)(input+12u);
 *(volatile uint32_t *)(link+500u)=(modeword>>16u)|(modeword<<16u);
 uint32_t mode=*(volatile uint8_t *)(input+18u),multiplier=*(volatile uint8_t *)(row+1u);
 *(volatile uint8_t *)(link+484u)=(uint8_t)mode;
 *(volatile uint8_t *)(link+504u)=(uint8_t)multiplier;
 uint32_t first_length=*(volatile uint16_t *)(row+2u),second_length=*(volatile uint16_t *)(row+4u);
 uint32_t id=*(volatile uint8_t *)row;
 *(volatile uint16_t *)(link+486u)=(uint16_t)first_length;
 *(volatile uint16_t *)(link+488u)=(uint16_t)second_length;
 uint32_t first_time=*(volatile uint32_t *)(input+4u),second_time=*(volatile uint32_t *)(input+8u);
 uint32_t first_phy=*(volatile uint8_t *)(row+10u);
 *(volatile uint8_t *)(link+12u)=(uint8_t)id;
 *(volatile uint32_t *)(link+492u)=first_time;
 *(volatile uint32_t *)(link+496u)=second_time;
 uint32_t mapped=opencfw_em9305_radio_phy_project_3183d4(first_phy)-2u;
 uint32_t value=1u;if((uint8_t)mapped<=6u)value=opencfw_em9305_config_phy_values_33449d[(int8_t)mapped];
 uint32_t second_phy=*(volatile uint8_t *)(row+11u);
 *(volatile uint8_t *)(link+480u)=(uint8_t)value;
 mapped=opencfw_em9305_radio_phy_project_3183d4(second_phy)-2u;
 value=1u;if((uint8_t)mapped<7u)value=opencfw_em9305_config_phy_values_33449d[(int8_t)mapped];
 *(volatile uint8_t *)(link+481u)=(uint8_t)value;
 uint32_t retries=*(volatile uint16_t *)(row+12u);
 *(volatile uint16_t *)(link+512u)=(uint16_t)retries;
 uint32_t seed=opencfw_em9305_radio_access_raw_318878();
 uint32_t slot=*(volatile uint16_t *)(link+6u);
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uint32_t offset=opencfw_em9305_config_extended_slot_stride(slot);
 *(volatile uint32_t *)(link+372u)=seed;
 uint32_t a=*(volatile uint16_t *)(row+6u),b=*(volatile uint16_t *)(row+8u);
 uint32_t metadata=*(volatile uint32_t *)(base+offset+324u);
 uint32_t kind=*(volatile uint16_t *)(base+offset+382u);
 *(volatile uint16_t *)(link+448u)=(uint16_t)a;
 *(volatile uint16_t *)(link+444u)=(uint16_t)b;
 *(volatile uint32_t *)(link+376u)=metadata;
 *(volatile uint16_t *)(link+468u)=(uint16_t)kind;
}
