static inline uint32_t opencfw_em9305_config_ready_mpyuw(uint32_t a)
{uint32_t r;__asm__ volatile("mpyuw %0,%1,1250":"=r"(r):"r"(a));return r;}
/* Native3186a0..318708: captured policy overhead, preceding active channels and unsigned readiness. */
uint32_t opencfw_em9305_config_channel_ready_3186a0(uintptr_t channel)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t overhead=*(volatile uint16_t *)(config+50u);
 overhead+=opencfw_em9305_auxiliary_guard_interval();
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c64u;
 int32_t difference=(int32_t)((uint32_t)channel-(uint32_t)base);
 uint32_t index=(uint8_t)(difference/140);
 for(uint32_t i=0u;i<index;++i){
  if(*(volatile uint8_t *)(base+4u+i*140u)){
   uint32_t unused=*(volatile uint32_t *)(base+52u+i*140u);(void)unused;
   uint32_t guard=opencfw_em9305_auxiliary_guard_interval();
   overhead+=guard;
   base=*(volatile uint32_t *)(uintptr_t)0x805c64u;
   overhead+=guard;
  }
 }
 uint32_t guard=opencfw_em9305_auxiliary_guard_interval();
 uint32_t baseline=*(volatile uint32_t *)(channel+12u);
 uint32_t interval=*(volatile uint16_t *)(channel+20u);
 uint32_t required=guard+baseline;
 uint32_t available=opencfw_em9305_config_ready_mpyuw(interval)-overhead;
 return available>=required;
}
