extern uint32_t opencfw_em9305_associated_schedule_drop_3136ac(uint32_t);
/* Native324a60..324a88 release, signed2824B row index, schedule removal and count. */
uint32_t opencfw_em9305_associated_release_324a60(uintptr_t record)
{
 (void)opencfw_em9305_common_release_304588(1u);
 int32_t delta=(int32_t)((uint32_t)record-*(volatile uint32_t *)(uintptr_t)0x805c38u),index;
 __asm__ volatile("div %0,%1,2824":"=r"(index):"r"(delta));
 (void)opencfw_em9305_associated_schedule_drop_3136ac((uint8_t)(index+4));
 return opencfw_em9305_command_count_down_30e48c();
}
uint32_t opencfw_em9305_associated_action_324a8c(uintptr_t record)
{
 (void)opencfw_em9305_associated_release_324a60(record);
 return opencfw_em9305_command_periodic_status_30e878(*(volatile uint8_t *)(record+1u),0u);
}
uint32_t opencfw_em9305_associated_action_324aa0(uintptr_t record)
{ return opencfw_em9305_command_periodic_status_30e878(*(volatile uint8_t *)(record+1u),12u); }
uint32_t opencfw_em9305_associated_action_324c60(uintptr_t record)
{ return opencfw_em9305_command_periodic_status_30e878(*(volatile uint8_t *)(record+1u),0u); }
