#include <stdint.h>
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);
extern uint32_t opencfw_em9305_common_init_302e90(void);
extern uint32_t opencfw_em9305_init_lower_30e9e0(uint32_t);
extern void *opencfw_em9305_memset(void *,int,unsigned long);
extern uint32_t opencfw_em9305_callback_child_322e44(uintptr_t);
/* Native30e840..30e854: modify caller-owned header, then tail event dispatch. */
uint32_t opencfw_em9305_init_callback_30e840(uintptr_t event,uint32_t enabled)
{
 uint32_t code=(enabled!=0u?2u:0u)+52u;
 *(volatile uint8_t *)(event+3u)=0u;
 *(volatile uint16_t *)event=0u;
 *(volatile uint8_t *)(event+2u)=(uint8_t)code;
 return opencfw_em9305_ll_event_callback_30e79c(event);
}
/* Native327dc8..327ddc: all four event bytes source owned. */
uint32_t opencfw_em9305_init_callback_327dc8(void)
{
 volatile uint32_t event=UINT32_C(0x003f0000);
 return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)&event);
}
/* Native3280c8..3280e4: retain child return across the genuine clear. */
uint32_t opencfw_em9305_init_callback_3280c8(void)
{
 (void)opencfw_em9305_common_init_302e90();
 uint32_t value=(uint32_t)(uintptr_t)opencfw_em9305_memset((void *)(uintptr_t)0x8052d4u,0u,304u);
 return opencfw_em9305_init_lower_30e9e0(value);
}
/* Native325450..325472: full 32 byte record initialized by native memset. */
uint32_t opencfw_em9305_init_callback_325450(void)
{
 uint32_t state=*(volatile uint8_t *)(uintptr_t)0x805b82u;
 if(state!=0u)return state;
 _Alignas(4) uint8_t record[32];
 (void)opencfw_em9305_memset(record,255,32u);
 return opencfw_em9305_callback_child_322e44((uintptr_t)record);
}
