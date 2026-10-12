uint32_t opencfw_em9305_event_reset_332cc0(uint32_t incoming)
{(void)incoming;return (uint32_t)(uintptr_t)opencfw_em9305_memset((void *)(uintptr_t)0x8058dcu,0u,404u);}
/* Native332c84..332cbc retains path-specific R0, including state before write4. */
uint32_t opencfw_em9305_event_mode_332c84(uintptr_t event)
{
 uint32_t operation=*(volatile uint8_t *)(event+3u);
 if(operation==1u){
  *(volatile uint8_t *)(uintptr_t)0x805a78u=0u;
  *(volatile uint8_t *)(uintptr_t)0x8058dcu=0u;
  return opencfw_em9305_command_count_down_30e48c();
 }
 if(operation!=0u)return 0x805a70u;
 uint32_t enabled=*(volatile uint8_t *)(uintptr_t)0x805a78u;
 if(enabled==0u)return 0u;
 (void)opencfw_em9305_command_stop_30b654(0u);
 uint32_t state=*(volatile uint8_t *)(uintptr_t)0x8058dcu;
 if(state==3u)*(volatile uint8_t *)(uintptr_t)0x8058dcu=4u;
 return state;
}
/* Native30e0e8..30e11c: clear404, callback registration, actual common-init. */
uint32_t opencfw_em9305_init_event_state_30e0e8(uint32_t incoming)
{
 (void)incoming;(void)opencfw_em9305_memset((void *)(uintptr_t)0x8058dcu,0u,404u);
 *(volatile uint32_t *)(uintptr_t)0x805210u=(uint32_t)(uintptr_t)opencfw_em9305_event_reset_332cc0;
 *(volatile uint32_t *)(uintptr_t)0x802964u=(uint32_t)(uintptr_t)opencfw_em9305_event_mode_332c84;
 return opencfw_em9305_common_init_303d2c(0x802964u);
}
