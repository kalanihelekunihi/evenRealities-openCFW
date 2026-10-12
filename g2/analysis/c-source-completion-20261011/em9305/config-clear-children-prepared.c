/* Native31b2f8..31b2fc: channel byte23, returned in delay slot. */
uint32_t opencfw_em9305_config_channel_busy_31b2f8(uintptr_t channel)
{return *(volatile uint8_t *)(channel+23u);}
/* Native31ad88..31ad90: active-byte clear; R0 pointer remains intact. */
uint32_t opencfw_em9305_config_link_clear_31ad88(uintptr_t link)
{*(volatile uint8_t *)link=0u;return (uint32_t)link;}
/* Native31ad64..31ad88: exact channel clear stores, decrement and release1 result. */
uint32_t opencfw_em9305_config_channel_clear_31ad64(uintptr_t channel)
{
 *(volatile uint8_t *)(channel+112u)=0u;
 *(volatile uint16_t *)(channel+108u)=0u;
 *(volatile uint8_t *)(channel+23u)=0u;
 *(volatile uint8_t *)(channel+4u)=0u;
 *(volatile uint8_t *)(channel+3u)=0u;
 *(volatile uint16_t *)channel=0u;
 (void)opencfw_em9305_command_count_down_30e48c();
 return opencfw_em9305_common_release_304588(1u);
}
