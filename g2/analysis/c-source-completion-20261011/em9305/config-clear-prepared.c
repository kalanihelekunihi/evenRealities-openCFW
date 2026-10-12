extern uint32_t opencfw_em9305_config_channel_busy_31b2f8(uintptr_t);
extern uint32_t opencfw_em9305_config_link_clear_31ad88(uintptr_t);
extern uint32_t opencfw_em9305_config_channel_clear_31ad64(uintptr_t);
static inline uint32_t opencfw_em9305_config_clear_stride(uint32_t i)
{uint32_t result;__asm__ volatile("mpywhl %0,%1,656":"=r"(result):"r"(i));return result;}
/* Native3083a4..30843c and30ca18 tail: channel guard, live link release and final clear. */
uint32_t opencfw_em9305_command_config_clear_30ca18(uint32_t id)
{
 uintptr_t channel=opencfw_em9305_ll_test_channel_find_31ab50(id);
 if(!channel)return 2u;
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(config+53u);
 if(count){uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c68u;
  for(uint32_t i=0u;i<count;++i){uintptr_t row=base+opencfw_em9305_config_clear_stride(i);
   if(*(volatile uint8_t *)row==0u)continue;
   if(*(volatile uint8_t *)(row+11u)!=id)continue;
   if(*(volatile uint8_t *)(row+10u)==1u)return 12u;
   if(*(volatile uint8_t *)(row+67u)!=0u)return 12u;
  }
 }
 if(opencfw_em9305_config_channel_busy_31b2f8(channel)!=0u)return 12u;
 config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t i=0u;
 while(i<*(volatile uint8_t *)(config+53u)){
  uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c68u;
  uintptr_t row=base+opencfw_em9305_config_clear_stride(i);
  if(*(volatile uint8_t *)row!=0u&&*(volatile uint8_t *)(row+11u)==id&&*(volatile uint8_t *)(row+10u)==0u){
   (void)opencfw_em9305_config_link_clear_31ad88(row);
   config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  }++i;
 }
 (void)opencfw_em9305_config_channel_clear_31ad64(channel);
 return 0u;
}
