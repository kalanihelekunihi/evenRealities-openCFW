/* Native324680..324686 and325250..325256 complete state leaves. */
uint32_t opencfw_em9305_phy_start_324680(uintptr_t record)
{ *(volatile uint8_t *)(record+404u)=1u;return (uint32_t)(record+404u); }
uintptr_t opencfw_em9305_phy_record_325250(uintptr_t record)
{ *(volatile uint8_t *)(record+597u)=0u;return record+597u; }
/* Native318278..31828e checks actual queue and dispatches only if empty. */
uint32_t opencfw_em9305_phy_schedule_318278(uintptr_t record)
{
 uint32_t empty=opencfw_em9305_wsf_queue_empty(record+360u);
 if(empty==0u)return empty;
 return opencfw_em9305_receive_terminate_325c08(record,62u);
}
/* Native32c7e4..32c80e; retains original record return when flag clear. */
uint32_t opencfw_em9305_phy_timer_start_32c7e4(uintptr_t record)
{
 if((*(volatile uint8_t *)(record+11u)&32u)==0u)return (uint32_t)record;
 uintptr_t timer=record+728u;
 if((*(volatile uint8_t *)(record+636u)&1u)==0u)
  return opencfw_em9305_wsf_timer_start_seconds(timer,40u);
 uint32_t timeout=*(volatile uint16_t *)(record+764u);
 return opencfw_em9305_wsf_timer_start_ms(timer,timeout);
}
