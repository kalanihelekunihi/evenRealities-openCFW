/* Native30cf28 tail308780..30879c: saved record, critical store word72. */
uint32_t opencfw_em9305_command_vendor_mask_30cf28(uint32_t id,uint32_t mask)
{uintptr_t record=opencfw_em9305_radio_record_find_31aa64(id);if(record==0u)return 66u;(void)opencfw_em9305_wsf_critical_enter();*(volatile uint32_t *)(record+72u)=mask;(void)opencfw_em9305_wsf_critical_exit();return 0u;}
/* Native30d5a8 tail308c44..308c6c: exact byte wrapping validation. */
uint32_t opencfw_em9305_command_vendor_mode_30d5a8(uint32_t id,uint32_t mode)
{uintptr_t record=opencfw_em9305_radio_record_find_31aa64(id);if(record==0u)return 66u;if((uint8_t)(mode+4u)<5u)return 18u;(void)opencfw_em9305_wsf_critical_enter();*(volatile uint8_t *)(record+76u)=(uint8_t)mode;(void)opencfw_em9305_wsf_critical_exit();return 0u;}
/* Native30d75c..30d772 tail308f28..308f50: low-byte OR validation, ordered stores. */
uint32_t opencfw_em9305_command_vendor_option_30d75c(uint32_t id,uint32_t first,uint32_t second)
{if((uint8_t)((first-1u)|(second-1u))>1u)return 18u;uintptr_t record=opencfw_em9305_radio_record_find_31aa64(id);if(record==0u)return 66u;(void)opencfw_em9305_wsf_critical_enter();*(volatile uint8_t *)(record+2531u)=(uint8_t)second;*(volatile uint8_t *)(record+2327u)=(uint8_t)first;(void)opencfw_em9305_wsf_critical_exit();return 0u;}
