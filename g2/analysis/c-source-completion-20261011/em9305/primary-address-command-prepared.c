/* Native310718: no instruction modifies incoming R0. */
uint32_t opencfw_em9305_primary_reset_mode_310718(uint32_t incoming){return incoming;}
uint32_t opencfw_em9305_primary_busy_307dd8(void){return *(volatile uint8_t *)(uintptr_t)0x804ffcu!=0u;}
uint32_t opencfw_em9305_primary_busy_307c08(void){return *(volatile uint8_t *)(uintptr_t)0x803bb8u!=0u;}
/* Native30de38..30dee8: callback address is reloaded on every one of
 * three calls; input packing occurs only after all busy/callback gates. */
uint32_t opencfw_em9305_command_primary_30de38(uintptr_t input)
{
 if(*(volatile uint8_t *)(uintptr_t)0x805a71u!=0u&&(*(volatile uint8_t *)(uintptr_t)0x805b91u&1u)!=0u)return 12u;
 if(*(volatile uint8_t *)(uintptr_t)0x805a73u!=0u){
  if(opencfw_em9305_primary_busy_307dd8()!=0u)return 12u;
  if(*(volatile uint32_t *)(uintptr_t)0x801308u!=0u){
   for(uint32_t i=0u;i<3u;i++){
    uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x801308u;
    if(((uint32_t (*)(uint32_t))callback)((uint8_t)i)!=0u)return 12u;
   }
  }
 }
 if(*(volatile uint8_t *)(uintptr_t)0x805a74u!=0u){
  if(opencfw_em9305_primary_busy_307c08()!=0u)return 12u;
  if(*(volatile uint32_t *)(uintptr_t)0x801304u!=0u){
   for(uint32_t i=0u;i<3u;i++){
    uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x801304u;
    if(((uint32_t (*)(uint32_t))callback)((uint8_t)i)!=0u)return 12u;
   }
  }
 }
 uint64_t packed=opencfw_em9305_controller_pack_address(input);
 uint32_t low=(uint32_t)packed,high=(uint32_t)(packed>>32u),kind=high&0xc000u;
 if(kind!=0xc000u&&kind!=0x4000u&&kind!=0u)return 18u;
 (void)opencfw_em9305_wsf_critical_enter();
 *(volatile uint32_t *)(uintptr_t)0x805a90u=high;
 *(volatile uint32_t *)(uintptr_t)0x805a8cu=low;
 *(volatile uint8_t *)(uintptr_t)0x805a7fu=1u;
 *(volatile uint16_t *)(uintptr_t)0x805a80u=257u;
 (void)opencfw_em9305_wsf_critical_exit();
 return 0u;
}
