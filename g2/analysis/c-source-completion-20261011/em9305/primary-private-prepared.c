/* Native304838/304850/304880/304898: each provider reloads the table after
 * authentic MPYUW index*912; exact halfword field and native word return. */
static uint32_t opencfw_em9305_private_counter_field(uint32_t index,uint32_t field)
{
 uint32_t offset=opencfw_em9305_config_limit_mpyuw(index,912u);
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 return *(volatile uint16_t *)(base+offset+field);
}
uint32_t opencfw_em9305_private_counter_304838(uint32_t index){return opencfw_em9305_private_counter_field(index,908u);}
uint32_t opencfw_em9305_private_counter_304850(uint32_t index){return opencfw_em9305_private_counter_field(index,906u);}
uint32_t opencfw_em9305_private_counter_304880(uint32_t index){return opencfw_em9305_private_counter_field(index,910u);}
uint32_t opencfw_em9305_private_counter_304898(uint32_t index){return opencfw_em9305_private_counter_field(index,904u);}
/* Native304994..3049a8: ST.AS227/226 are words at908/904, in that order. */
uint32_t opencfw_em9305_private_counter_reset_304994(uint32_t index)
{
 uint32_t offset=opencfw_em9305_config_limit_mpyuw(index,912u);
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uintptr_t record=base+offset;
 *(volatile uint32_t *)(record+908u)=0u;
 *(volatile uint32_t *)(record+904u)=0u;
 return (uint32_t)record;
}
/* Native3049ac..3049c8: fullword count<=7, publish enable then count. */
uint32_t opencfw_em9305_private_mode_3049ac(uint32_t count,uint32_t enable)
{
 if(count>7u)return 18u;
 *(volatile uint8_t *)(uintptr_t)0x805f00u=(uint8_t)enable;
 *(volatile uint8_t *)(uintptr_t)0x8012fcu=(uint8_t)count;
 return 0u;
}
/* Native3049cc..3049fc: mark busy before64-byte copy; store operation3
 * before the existing wake provider, then return zero. */
uint32_t opencfw_em9305_private_data_3049cc(uintptr_t input)
{
 if(*(volatile uint8_t *)(uintptr_t)0x805b80u!=0u)return 12u;
 *(volatile uint8_t *)(uintptr_t)0x805b80u=1u;
 (void)opencfw_em9305_memcpy((void *)(uintptr_t)0x80527cu,(const void *)input,64u);
 *(volatile uint8_t *)(uintptr_t)0x805258u=3u;
 (void)opencfw_em9305_wsf_wake_cell_313fc0(0x805258u);
 return 0u;
}
/* Native304a00..304a60: critical capture and fourth output before exit.
 * Invalid slots zero all four halfwords; fourth store occurs before exit. */
uint32_t opencfw_em9305_private_stats_304a00(uint32_t index,uintptr_t first,uintptr_t second,uintptr_t third,uintptr_t fourth)
{
 (void)opencfw_em9305_wsf_critical_enter();
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(config+34u),status=2u,value=0u;
 if(index<count&&opencfw_em9305_ll_slot_active_30731c(index)!=0u){
  *(volatile uint16_t *)first=(uint16_t)opencfw_em9305_private_counter_304898(index);
  *(volatile uint16_t *)second=(uint16_t)opencfw_em9305_private_counter_304850(index);
  *(volatile uint16_t *)third=(uint16_t)opencfw_em9305_private_counter_304838(index);
  value=opencfw_em9305_private_counter_304880(index);
  status=0u;
 }else{
  *(volatile uint16_t *)first=0u;
  *(volatile uint16_t *)second=0u;
  *(volatile uint16_t *)third=0u;
 }
 *(volatile uint16_t *)fourth=(uint16_t)value;
 (void)opencfw_em9305_wsf_critical_exit();
 return status;
}
/* Native304a64..304a94: validated counter reset inside critical region. */
uint32_t opencfw_em9305_private_reset_304a64(uint32_t index)
{
 (void)opencfw_em9305_wsf_critical_enter();
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t status=2u;
 if(index<*(volatile uint8_t *)(config+34u)&&opencfw_em9305_ll_slot_active_30731c(index)!=0u){
  (void)opencfw_em9305_private_counter_reset_304994(index);status=0u;
 }
 (void)opencfw_em9305_wsf_critical_exit();
 return status;
}
/* Native304afc..304bb0: all four vendor-private opcodes; allocation uses
 * command captured at native points, subsequent query tests fresh request. */
uint32_t opencfw_em9305_primary_private_304afc(uintptr_t request,uintptr_t input)
{
 uint32_t command=*(volatile uint16_t *)request;
 if(command==0xfe84u){
  uint32_t status=opencfw_em9305_private_reset_304a64(*(volatile uint8_t *)input);
  (void)opencfw_em9305_ll_status_event_331bf8(request,(uint8_t)status);return 1u;
 }
 if(command==0xfe82u){
  uint32_t status=opencfw_em9305_private_data_3049cc(input);
  (void)opencfw_em9305_ll_status_event_331bf8(request,(uint8_t)status);return 1u;
 }
 uint32_t id=0u,length=1u;
 if(command==0xfe81u){
  uint32_t count=*(volatile uint8_t *)input,enabled=*(volatile uint8_t *)(input+1u);
  (void)opencfw_em9305_private_mode_3049ac(count,enabled!=0u);
  command=*(volatile uint16_t *)request;
 }else if(command==0xfe83u){id=*(volatile uint8_t *)input;length=9u;}
 else return 0u;
 uintptr_t packet=opencfw_em9305_ll_response_allocate_32e428(length,command);
 if(packet==0u)return 1u;
 _Alignas(4) uint8_t scratch[8];
 if(*(volatile uint16_t *)request==0xfe83u){
  uint32_t result=opencfw_em9305_private_stats_304a00(id,(uintptr_t)scratch,(uintptr_t)(scratch+6u),(uintptr_t)(scratch+4u),(uintptr_t)(scratch+2u));
  *(volatile uint8_t *)packet=(uint8_t)result;
  *(volatile uint8_t *)(packet+1u)=*(volatile uint8_t *)scratch;
  uint32_t first=*(volatile uint16_t *)(scratch+6u),second=*(volatile uint16_t *)(scratch+4u),third=*(volatile uint16_t *)(scratch+2u),high=*(volatile uint8_t *)(scratch+1u);
  *(volatile uint8_t *)(packet+3u)=(uint8_t)first;
  *(volatile uint8_t *)(packet+5u)=(uint8_t)second;
  *(volatile uint8_t *)(packet+7u)=(uint8_t)third;
  *(volatile uint8_t *)(packet+2u)=(uint8_t)high;
  *(volatile uint8_t *)(packet+4u)=(uint8_t)(first>>8u);
  *(volatile uint8_t *)(packet+6u)=(uint8_t)(second>>8u);
  *(volatile uint8_t *)(packet+8u)=(uint8_t)(third>>8u);
 }
 (void)opencfw_em9305_ll_event_send(packet-5u);
 return 1u;
}
