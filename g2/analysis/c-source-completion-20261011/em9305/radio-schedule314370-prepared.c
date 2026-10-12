/* Native314370..3143f4: captured parent/now, guard addition in the call
 * delay slot, mode overhead and sparse accumulator update. */
uint32_t opencfw_em9305_radio_schedule_314370(uintptr_t object,uintptr_t record,uint32_t now,uint32_t guard)
{
 uint32_t initial=*(volatile uint32_t *)(object+12u);
 uintptr_t parent=*(volatile uint32_t *)(object+44u);
 uintptr_t accumulator=record+164u;
 uint32_t overhead=initial+guard;
 overhead+=opencfw_em9305_auxiliary_guard_interval();
 uint32_t mode=*(volatile uint8_t *)(parent+13u);
 if(mode==3u)overhead+=336u;else if(mode==2u)overhead+=24u;else if(mode==1u)overhead+=40u;
 uint32_t used=*(volatile uint32_t *)accumulator;
 uint32_t available=*(volatile uint32_t *)(object+16u);
 if(available<used+overhead){*(volatile uint32_t *)accumulator=available;return 0u;}
 uintptr_t next=*(volatile uint32_t *)(object+4u);
 uint32_t remaining=available-used;
 if(next!=0u){
  uint32_t elapsed=opencfw_em9305_auxiliary_elapsed_303f8c(*(volatile uint32_t *)(next+8u),now);
  if(remaining<elapsed)elapsed=remaining;
  if(elapsed<overhead){*(volatile uint32_t *)accumulator=*(volatile uint32_t *)accumulator+elapsed;return 0u;}
  remaining=elapsed;
 }
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805c18u;
 uint32_t cap=opencfw_em9305_config_limit_mpyuw(*(volatile uint16_t *)(config+4u),1000u);
 uint32_t room=remaining-overhead;
 return room<cap?room:cap;
}
