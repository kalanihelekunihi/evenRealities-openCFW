/* Native request30455c..304588, pure no-op30fd2c and exact scaled count. */
uint32_t opencfw_em9305_pal_request_noop_30fd2c(uint32_t incoming)
{return incoming;}
uint32_t opencfw_em9305_common_request_30455c(uint32_t index)
{
 uint32_t selected=*(volatile uint8_t *)(uintptr_t)0x8016bdu;
 if(selected==0u){
  (void)opencfw_em9305_pal_request_noop_30fd2c(index);
  (void)opencfw_em9305_auxiliary_select_314d94(index);
 }
 uint32_t offset;
 __asm__ volatile("mpyuw %0,%1,24":"=r"(offset):"r"(index));
 uintptr_t slot=0x801658u+offset;
 uint32_t count=*(volatile uint32_t *)slot;
 *(volatile uint32_t *)slot=count+1u;
 return (uint32_t)slot;
}
