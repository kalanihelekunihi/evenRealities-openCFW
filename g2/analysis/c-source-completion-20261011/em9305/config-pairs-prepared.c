extern uint32_t opencfw_em9305_config_pairs_apply_306b80(uint32_t,uintptr_t);
/* Native30b3f8..30b480: capability, duplicate first-array ids, second-array slot state. */
uint32_t opencfw_em9305_command_config_pairs_30b3f8(uint32_t count,uintptr_t arrays)
{
 if((*(volatile uint8_t *)(uintptr_t)0x805a98u&1u)==0u)return 12u;
 uint32_t status=0u;
 for(uint32_t row=0u;status==0u&&row<count;++row){
  for(uint32_t previous=0u;status==0u&&previous<row;++previous){
   uintptr_t first=*(volatile uint32_t *)arrays;
   uint32_t prior=*(volatile uint16_t *)(first+previous*2u);
   uint32_t current=*(volatile uint16_t *)(first+row*2u);
   if(current==prior)status=18u;
  }
  if(status!=0u)continue;
  uintptr_t second=*(volatile uint32_t *)(arrays+4u);
  uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  uint32_t id=*(volatile uint16_t *)(second+row*2u);
  uint32_t capacity=*(volatile uint8_t *)(config+34u);
  status=2u;
  if(id>=capacity)continue;
  if(opencfw_em9305_ll_slot_active_30731c(id)==0u)continue;
  second=*(volatile uint32_t *)(arrays+4u);
  id=*(volatile uint16_t *)(second+row*2u);
  status=opencfw_em9305_ll_slot_state_306fdc(id)!=0u?12u:0u;
 }
 if(status==0u)status=opencfw_em9305_config_pairs_apply_306b80(count,arrays);
 return status&255u;
}
