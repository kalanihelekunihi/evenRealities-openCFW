extern uint32_t opencfw_em9305_command_advertising_data_notify_306a7c(uint32_t);
extern uint32_t opencfw_em9305_command_radio_power_310230(int32_t,uint32_t);
/* Native30cee4..30ceee: caller input R0 survives the byte store. */
uint32_t opencfw_em9305_command_vendor_byte_30cee4(int32_t value)
{*(volatile uint8_t *)(uintptr_t)0x805a9cu=(uint8_t)value;return (uint32_t)value;}
/* Native303258..303264: live 32-byte product version, same copy provider. */
void opencfw_em9305_command_product_version_303258(uintptr_t output)
{(void)opencfw_em9305_memcpy((void *)output,(const void *)(uintptr_t)0x8013d0u,32u);}
/* Native30cdd8..30ce18: captured length survives gate and critical calls. */
uint32_t opencfw_em9305_command_advertising_data_30cdd8(uint32_t length,uintptr_t input)
{
 if(opencfw_em9305_ll_connection_gate_30e524()==0u)return 12u;
 if(length>=32u)return 18u;
 (void)opencfw_em9305_wsf_critical_enter();
 (void)opencfw_em9305_memcpy((void *)(uintptr_t)0x805ba0u,(const void *)input,length);
 *(volatile uint8_t *)(uintptr_t)0x805bc0u=1u;
 *(volatile uint8_t *)(uintptr_t)0x805bbfu=(uint8_t)length;
 (void)opencfw_em9305_wsf_critical_exit();
 (void)opencfw_em9305_command_advertising_data_notify_306a7c(1u);
 return 0u;
}
/* Native30df98..30dfd8: distinct adjacent scan-response data region. */
uint32_t opencfw_em9305_command_scan_response_30df98(uint32_t length,uintptr_t input)
{
 if(opencfw_em9305_ll_connection_gate_30e524()==0u)return 12u;
 if(length>=32u)return 18u;
 (void)opencfw_em9305_wsf_critical_enter();
 (void)opencfw_em9305_memcpy((void *)(uintptr_t)0x805bc1u,(const void *)input,length);
 *(volatile uint8_t *)(uintptr_t)0x805be1u=1u;
 *(volatile uint8_t *)(uintptr_t)0x805be0u=(uint8_t)length;
 (void)opencfw_em9305_wsf_critical_exit();
 (void)opencfw_em9305_command_advertising_data_notify_306a7c(2u);
 return 0u;
}
/* Native30bb50..30bb74: gate failure leaves output untouched. */
uint32_t opencfw_em9305_command_advertising_power_30bb50(uintptr_t output)
{
 if(opencfw_em9305_ll_connection_gate_30e524()==0u)return 12u;
 int32_t requested=(int8_t)*(volatile uint8_t *)(uintptr_t)0x805a9cu;
 uint32_t actual=opencfw_em9305_command_radio_power_310230(requested,0u);
 *(volatile uint8_t *)output=(uint8_t)actual;
 return 0u;
}
