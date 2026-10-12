/* Native30c768..30c788: post-gate live config, signed min on positive halfword. */
uint32_t opencfw_em9305_command_packet_size_30c768(uintptr_t output)
{if(opencfw_em9305_ll_stream_gate_30e510()==0u)return 12u;uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;uint32_t size=*(volatile uint16_t *)(config+16u);if(size>1650u)size=1650u;*(volatile uint16_t *)output=(uint16_t)size;return 0u;}
/* Native30c7b0..30c7cc: failure preserves caller output. */
uint32_t opencfw_em9305_command_packet_count_30c7b0(uintptr_t output)
{if(opencfw_em9305_ll_stream_gate_30e510()==0u)return 12u;uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;uint32_t count=*(volatile uint8_t *)(config+12u);*(volatile uint8_t *)output=(uint8_t)count;return 0u;}
/* Native30bd8c tail306ee8..306f08: initial output sentinel before lookup. */
uint32_t opencfw_em9305_command_packet_power_30bd8c(uint32_t id,uintptr_t output)
{*(volatile uint8_t *)output=129u;uintptr_t record=opencfw_em9305_radio_record_find_31aa64((uint8_t)id);if(record==0u)return 66u;int32_t requested=*(volatile int8_t *)(record+60u);uint32_t power=opencfw_em9305_command_radio_power_310230(requested,0u);*(volatile uint8_t *)output=(uint8_t)power;return 0u;}
