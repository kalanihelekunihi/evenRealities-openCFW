/* Native3259fc..325a3c: rejection-sample next channel from global mask.
 * Function name follows the prior parent contract; this is channel selection,
 * not allocation/refill. Empty mask intentionally has no invented exit. */
uint32_t opencfw_em9305_associated_packet_refill_3259fc(uintptr_t record)
{
 for(;;){
  uint32_t random=opencfw_em9305_associated_random_31896c();
  uint32_t previous=*(volatile uint8_t *)(record+697u);
  *(volatile uint8_t *)(record+696u)=(uint8_t)random;
  uint32_t sum=previous+random;
  uint32_t quotient=opencfw_em9305_config_link_mpywhul(sum,0xdd68u)>>21u;
  uint32_t correction=(uint32_t)((int32_t)(int16_t)quotient*-37);
  uint32_t channel=sum+correction;
  *(volatile uint8_t *)(record+697u)=(uint8_t)channel;
  uint32_t low=*(volatile uint32_t *)(uintptr_t)0x805aa0u;
  uint32_t high=*(volatile uint32_t *)(uintptr_t)0x805aa4u;
  uint64_t mask=((uint64_t)high<<32u)|low;
  uint32_t result=(uint32_t)(mask>>((uint8_t)channel&63u));
  if((result&1u)!=0u)return result;
 }
}
