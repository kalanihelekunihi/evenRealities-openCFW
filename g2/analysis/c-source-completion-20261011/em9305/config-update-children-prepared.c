/* Native3185e8..318670: two PHY contributions, feature reads remain separately live. */
uint32_t opencfw_em9305_config_link_time_3185e8(uint32_t first_phy,uint32_t second_phy,uint32_t first_length,uint32_t second_length)
{
 uint32_t sum=0u;
 if(first_phy==1u)sum=(first_length<<3u)+112u;
 else if(first_phy==2u)sum=60u+(first_length<<2u);
 else if(first_phy==3u){uint32_t n=first_length+4u;
  sum=(*(volatile uint8_t *)(uintptr_t)0x805a86u&16u)?(n<<4u)+462u:(n<<6u)+720u;
 }
 sum+=150u;
 if(second_phy==1u)sum+=(second_length<<3u)+112u;
 else if(second_phy==2u)sum+=(second_length<<2u)+60u;
 else if(second_phy==3u){uint32_t n=second_length+4u;
  sum+=(*(volatile uint8_t *)(uintptr_t)0x805a86u&16u)?(n<<4u)+462u:(n<<6u)+720u;
 }
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 return sum+*(volatile uint16_t *)(config+54u)+150u;
}
/* Native318670..31869e: early second-slot gate, equality and first empty attachment. R1 preserved by native routine. */
uint32_t opencfw_em9305_config_attach_link_318670(uintptr_t channel,uintptr_t link)
{
 if(*(volatile uint32_t *)(channel+92u))return 0u;
 for(uint32_t i=0u;i<2u;++i){uintptr_t cell=channel+88u+i*4u;uint32_t value=*(volatile uint32_t *)cell;
  if(value==(uint32_t)link)return 1u;
  if(value==0u){*(volatile uint32_t *)cell=(uint32_t)link;return 1u;}
 }
 return 0u;
}
