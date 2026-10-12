/* Native ROM3357e0/335800: eight exact paired words, reader333bec
 * establishes extent through lp_count8. Source/table SHA in evidence receipt. */
static const uint32_t opencfw_em9305_primary_timer_thresholds[8]={2000000u,1000000u,500000u,160000u,80000u,40000u,5000u,0u};
static const uint32_t opencfw_em9305_primary_timer_quanta[8]={1000000u,100000u,50000u,10000u,5000u,2500u,1250u,625u};
/* Native333bec..333c20: strict unsigned threshold, first hit, no-hit R0 unchanged. */
uint32_t opencfw_em9305_radio_primary_timer_333bec(uint32_t value)
{
 if(*(volatile uint8_t *)(uintptr_t)0x805f34u!=0u)return value;
 *(volatile uint32_t *)(uintptr_t)0x805f30u=value;
 for(uint32_t i=0u;i<8u;i++){
  if(opencfw_em9305_primary_timer_thresholds[i]<value){
   uint32_t quantum=opencfw_em9305_primary_timer_quanta[i];
   *(volatile uint32_t *)(uintptr_t)0x805f2cu=quantum;
   return quantum;
  }
 }
 return value;
}
/* Native313744..31375c: authentic 16x16 unsigned DSP multiply, flag clear
 * in call delay slot, flag publish after child; R0 is child result. */
uint32_t opencfw_em9305_radio_primary_value_313744(uint32_t value)
{
 uint32_t scaled=opencfw_em9305_config_limit_mpyuw(value,1250u);
 *(volatile uint8_t *)(uintptr_t)0x805f34u=0u;
 uint32_t result=opencfw_em9305_radio_primary_timer_333bec(scaled);
 *(volatile uint8_t *)(uintptr_t)0x805f34u=1u;
 return result;
}
