/* Native307c5c..307ca8: six active row address/role/kind comparisons. */
uint32_t opencfw_em9305_command_duplicate_307c5c(uint32_t role,uint32_t kind,uint32_t low,uint32_t high)
{
 for(uint32_t i=0u;i<6u;++i){
  uintptr_t offset=i*784u;
  if(*(volatile uint8_t *)(uintptr_t)(0x803d78u+offset)==0u)continue;
  uintptr_t row=0x804044u+offset;
  if(*(volatile uint8_t *)row!=role)continue;
  if(*(volatile uint8_t *)(row+1u)!=kind)continue;
  uint32_t stored_high=*(volatile uint32_t *)(row+8u);
  uint32_t stored_low=*(volatile uint32_t *)(row+4u);
  if(((stored_high^high)|(stored_low^low))==0u)return 1u;
 }
 return 0u;
}
