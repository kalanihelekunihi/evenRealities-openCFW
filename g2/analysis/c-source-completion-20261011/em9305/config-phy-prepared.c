/* Native332f80..332fa8: combined PHY2/PHY4 capability guard; full-width args retained. */
uint32_t opencfw_em9305_config_phy_pair_valid_332f80(uint32_t first,uint32_t second)
{
 uint32_t capability=*(volatile uint32_t *)(uintptr_t)0x805a94u;
 uint32_t combined=first|second;
 if((capability&256u)==0u&&(combined&2u)!=0u)return 0u;
 if((capability&2048u)==0u&&(combined&4u)!=0u)return 0u;
 return 1u;
}
