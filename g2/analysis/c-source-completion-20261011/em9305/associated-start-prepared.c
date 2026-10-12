extern uint32_t opencfw_em9305_associated_channel_seed_324c98(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_associated_validate_32b2d4(uintptr_t);
extern uint32_t opencfw_em9305_associated_cleanup_3266d0(uintptr_t,uint32_t);
static uint32_t opencfw_em9305_associated_timing_crc(uintptr_t record)
{
 uint32_t count=*(volatile uint16_t *)(record+2250u);
 uintptr_t input=*(volatile uint32_t *)(record+1424u);
 uint32_t seed=opencfw_em9305_pal_random_step();
 return opencfw_em9305_crc_update_304678(seed,count,input);
}
/* Native324b3c..324c5c complete associated start action. */
uint32_t opencfw_em9305_associated_action_324b3c(uintptr_t record)
{
 (void)opencfw_em9305_common_request_30455c(1u);
 *(volatile uint8_t *)(record+698u)=0u;
 uint32_t access=opencfw_em9305_radio_access_raw_318878();
 *(volatile uint32_t *)(record+372u)=access;
 uint32_t second=*(volatile uint32_t *)(uintptr_t)0x805aa4u;
 uint32_t first=*(volatile uint32_t *)(uintptr_t)0x805aa0u;
 *(volatile uint32_t *)(record+720u)=first;
 *(volatile uint8_t *)(record+799u)=0u;
 *(volatile uint16_t *)(record+752u)=0u;
 *(volatile uint32_t *)(record+724u)=second;
 (void)opencfw_em9305_radio_channel_transform_30e3fc(record+720u);
 access=*(volatile uint32_t *)(record+372u);
 uint32_t flag=*(volatile uint8_t *)(record+2809u);
 uint32_t seed=*(volatile uint16_t *)(record+752u);
 *(volatile uint8_t *)(record+766u)=1u;
 *(volatile uint16_t *)(record+768u)=(uint16_t)(access^(access>>16u));
 if(flag!=0u)seed^=*(volatile uint8_t *)(record+799u);
 uint32_t channel=opencfw_em9305_associated_channel_seed_324c98(record+720u,seed);
 *(volatile uint8_t *)(record+697u)=(uint8_t)channel;
 uint32_t status;
 flag=*(volatile uint8_t *)(record+2809u);
 uintptr_t callback=0u;
 if(flag!=0u)callback=*(volatile uint32_t *)(uintptr_t)0x805cc4u;
 if(callback!=0u)status=((uint32_t (*)(uintptr_t))callback)(record);
 else status=opencfw_em9305_associated_validate_32b2d4(record);
 if(status!=0u){
  (void)opencfw_em9305_associated_cleanup_3266d0(record,3u);
  return opencfw_em9305_command_periodic_status_30e878(*(volatile uint8_t *)(record+1u),status);
 }
 uint32_t kind=*(volatile uint8_t *)(record+2u);
 *(volatile uint8_t *)(record+369u)=1u;
 if(kind==1u){
  if(*(volatile uint8_t *)(record+2785u)==0u)*(volatile uint8_t *)(record+378u)=1u;
  uint32_t crc=opencfw_em9305_associated_timing_crc(record);
  *(volatile uint8_t *)(record+2786u)=1u;
  *(volatile uint16_t *)(record+1442u)=(uint16_t)crc;
 }
 if(*(volatile uint8_t *)(record+704u)!=0u){
  uint32_t crc=opencfw_em9305_associated_timing_crc(record);
  *(volatile uint16_t *)(record+706u)=(uint16_t)crc;
 }
 (void)opencfw_em9305_command_periodic_status_30e878(*(volatile uint8_t *)(record+1u),0u);
 return opencfw_em9305_command_count_30e4bc();
}
