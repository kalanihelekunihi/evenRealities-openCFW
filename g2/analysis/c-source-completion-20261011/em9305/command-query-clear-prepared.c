/* Native303700..30370a: address-list count clear. */
uint32_t opencfw_em9305_address_count_clear_303700(void)
{*(volatile uint8_t *)(uintptr_t)0x80160au=0u;return 0x80160au;}
/* Native30370c..303716: address-list capacity byte query. */
uint32_t opencfw_em9305_address_capacity_30370c(void)
{return *(volatile uint8_t *)(uintptr_t)0x80160bu;}
/* Native307cb8..307cc6: product state equals1. */
uint32_t opencfw_em9305_address_busy_307cb8(void)
{return *(volatile uint8_t *)(uintptr_t)0x8051a4u==1u;}
/* Native30b12c..30b150: read flag even if gate is closed. */
uint32_t opencfw_em9305_command_address_clear_30b12c(void)
{
 uint32_t gate=opencfw_em9305_ll_stream_gate_30e510();
 uint32_t flag=*(volatile uint8_t *)(uintptr_t)0x805a77u;
 if(flag!=0u||gate==0u)return 12u;
 if(opencfw_em9305_address_busy_307cb8()!=0u)return 12u;
 (void)opencfw_em9305_address_count_clear_303700();return 0u;
}
/* Native30c80c..30c824: output pointer preserved across gate. */
uint32_t opencfw_em9305_command_power_query_30c80c(uintptr_t output)
{
 if(opencfw_em9305_ll_stream_gate_30e510()==0u)return 12u;
 *(volatile uint8_t *)output=(uint8_t)opencfw_em9305_address_capacity_30370c();return 0u;
}
