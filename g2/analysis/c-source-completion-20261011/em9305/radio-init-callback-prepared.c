/* Native30bf24..30bf6a: event low15 bits dispatch, optional message, two
 * independent clock reads, fullword elapsed compared to halfword maximum. */
extern uint32_t opencfw_em9305_init_event_dispatch_306c7c(uint32_t);
extern uint32_t opencfw_em9305_init_message_3075cc(uintptr_t);
uint32_t opencfw_em9305_init_callback_30bf24(uint32_t events,uintptr_t message)
{
 uint32_t start=opencfw_em9305_pal_current_time();
 if(events!=0u){for(uint32_t i=0u;i<15u;i++){if((events&(1u<<i))!=0u)(void)opencfw_em9305_init_event_dispatch_306c7c((uint8_t)i);}}
 if(message!=0u)(void)opencfw_em9305_init_message_3075cc(message);
 uint32_t now=opencfw_em9305_pal_current_time();
 uint32_t elapsed=opencfw_em9305_pal_elapsed_raw(now,start);
 uint32_t maximum=*(volatile uint16_t *)(uintptr_t)0x8058d8u;
 if(maximum<elapsed)*(volatile uint16_t *)(uintptr_t)0x8058d8u=(uint16_t)elapsed;
 return elapsed;
}
/* Native30e9a4..30e9dc: capture high before low featuremask, complete
 * 64-byte clear; exact defaults/feature words and native lowword return. */
uint32_t opencfw_em9305_init_state_30e9a4(uint32_t incoming)
{
 (void)incoming;(void)opencfw_em9305_memset((void *)(uintptr_t)0x805a70u,0u,64u);
 *(volatile uint32_t *)(uintptr_t)0x805a88u=0xfe000000u;
 uint32_t high=*(volatile uint32_t *)(uintptr_t)0x805b34u;
 uint32_t low=*(volatile uint32_t *)(uintptr_t)0x805b30u;
 *(volatile uint32_t *)(uintptr_t)0x805aa4u=31u;
 *(volatile uint32_t *)(uintptr_t)0x805aa0u=0xffffffffu;
 *(volatile uint32_t *)(uintptr_t)0x805a84u=0x0046dc40u;
 *(volatile uint32_t *)(uintptr_t)0x805a98u=high;
 *(volatile uint32_t *)(uintptr_t)0x805a94u=low;
 return low;
}
