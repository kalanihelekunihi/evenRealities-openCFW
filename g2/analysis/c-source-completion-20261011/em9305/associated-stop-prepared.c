/* Native324aa8..324b38: associated stop action. Capture timing source/count
 * before PRNG call, then reload product flags exactly at native point. */
uint32_t opencfw_em9305_associated_action_324aa8(uintptr_t record)
{
 if(*(volatile uint8_t *)(record+2u)==1u&&*(volatile uint8_t *)(record+369u)!=0u){
  uint32_t count=*(volatile uint16_t *)(record+2250u);
  uintptr_t input=*(volatile uint32_t *)(record+1424u);
  uint32_t seed=opencfw_em9305_pal_random_step();
  uint32_t crc=opencfw_em9305_crc_update_304678(seed,count,input);
  *(volatile uint8_t *)(record+2786u)=1u;
  *(volatile uint16_t *)(record+1442u)=(uint16_t)crc;
 }
 uint32_t flag=*(volatile uint8_t *)(record+2809u);
 *(volatile uint8_t *)(record+378u)=0u;
 *(volatile uint8_t *)(record+369u)=0u;
 *(volatile uint8_t *)(record+698u)=1u;
 if(flag!=0u){
  uintptr_t packet=*(volatile uint32_t *)(record+1160u);
  *(volatile uint32_t *)(packet+3844u)=32767u;
  *(volatile uint16_t *)(packet+3840u)=0u;
  *(volatile uint32_t *)(packet+3848u)=0u;
  (void)opencfw_em9305_memset((void *)(packet+3852u),255u,15u);
 }
 return opencfw_em9305_ll_schedule_notify_313354(record+380u);
}
