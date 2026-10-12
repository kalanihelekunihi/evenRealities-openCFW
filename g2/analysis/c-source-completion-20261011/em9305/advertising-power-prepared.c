/* Native310230..310260: signed live upper/lower caps and measured query. */
uint32_t opencfw_em9305_command_radio_power_310230(int32_t requested,uint32_t unused)
{
 (void)unused;
 int32_t measured=(int32_t)opencfw_em9305_radio_status_311a00(1u);
 int32_t upper=(int8_t)*(volatile uint8_t *)(uintptr_t)0x8012b8u;
 if(upper>measured)upper=measured;
 if(upper<requested)return (uint32_t)upper;
 int32_t lower=(int8_t)*(volatile uint8_t *)(uintptr_t)0x8012b9u;
 return (uint32_t)(lower>requested?lower:requested);
}
