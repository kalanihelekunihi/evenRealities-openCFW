extern uint32_t opencfw_em9305_associated_channel_pending_327af4(uintptr_t);
/* Native32b538..32b5e8 full registered callback including retry loop. */
uint32_t opencfw_em9305_associated_radio_callback_32b538(uintptr_t object)
{
 uintptr_t record=*(volatile uint32_t *)(object+36u);
 if(*(volatile uint8_t *)(record+698u)!=0u)return opencfw_em9305_associated_cleanup_3266d0(record,3u);
 uintptr_t packet=*(volatile uint32_t *)(object+44u);
 uint32_t power=*(volatile uint8_t *)(packet+15u);
 if(power==0u)power=*(volatile uint8_t *)(uintptr_t)0x805bedu;
 *(volatile uint8_t *)(packet+14u)=(uint8_t)power;
 if(*(volatile uint8_t *)(record+1164u)!=0u){
  uintptr_t destination=*(volatile uint32_t *)(record+1148u);
  uint32_t bytes=*(volatile uint8_t *)(record+1165u);
  *(volatile uint8_t *)(record+1164u)=0u;
  (void)opencfw_em9305_memcpy((void *)destination,(const void *)(record+1168u),bytes);
  bytes=*(volatile uint8_t *)(record+1165u);
  uint32_t extent=*(volatile uint16_t *)(record+1166u);
  *(volatile uint16_t *)(record+1144u)=(uint16_t)bytes;
  *(volatile uint16_t *)(record+706u)=(uint16_t)extent;
 }
 if(*(volatile uint8_t *)(uintptr_t)0x805beeu!=0u){
  uint32_t timestamp=*(volatile uint32_t *)(object+8u),spacing=*(volatile uint32_t *)(record+700u);
  uint32_t count=*(volatile uint16_t *)(record+752u),id=*(volatile uint8_t *)(record+1u);
  (void)opencfw_em9305_associated_report_30e89c(id,count,0u,spacing,timestamp);
 }
 *(volatile uint32_t *)(object+20u)=*(volatile uint32_t *)(record+700u);
 for(;;){
  uint32_t spacing=*(volatile uint32_t *)(record+700u),timestamp=*(volatile uint32_t *)(object+8u);
  uint32_t count=*(volatile uint16_t *)(record+752u);
  *(volatile uint16_t *)(record+752u)=(uint16_t)(count+1u);
  *(volatile uint32_t *)(object+8u)=timestamp+spacing;
  (void)opencfw_em9305_associated_channel_pending_327af4(record);
  count=*(volatile uint16_t *)(record+752u);
  uint32_t channel=opencfw_em9305_associated_channel_seed_324c98(record+720u,count);
  *(volatile uint8_t *)(record+697u)=(uint8_t)channel;
  uint32_t result=opencfw_em9305_associated_schedule_insert_312da4(object,0u);
  if(result!=0u)return result;
 }
}
