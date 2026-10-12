/* Native31b6b0..31b6c6: disabled zero return, otherwise trigger byte and
 * post-increment schedule object. Native incoming arguments are unused. */
uint32_t opencfw_em9305_init_state_action_31b6b0(uintptr_t incoming,uint32_t state)
{
 (void)incoming;(void)state;
 uint32_t enabled=*(volatile uint8_t *)(uintptr_t)0x805a74u;
 if(enabled==0u)return 0u;
 *(volatile uint8_t *)(uintptr_t)0x803c29u=1u;
 return opencfw_em9305_ll_schedule_notify_313354((uintptr_t)0x803c2cu);
}
