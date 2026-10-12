#include <stdint.h>
extern void *opencfw_em9305_memset(void *,int,unsigned long);
extern void *opencfw_em9305_memcpy(void *,const void *,uint32_t);
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);
/* Native322e44..322e7c: all38 bytes initialized before fresh state read. */
uint32_t opencfw_em9305_callback_child_322e44(uintptr_t input)
{
 _Alignas(4) uint8_t record[40];
 (void)opencfw_em9305_memset(record,0,38u);
 uint32_t state=*(volatile uint8_t *)(uintptr_t)0x805b82u;
 *(volatile uint8_t *)(record+4u)=state==0u?18u:0u;
 *(volatile uint8_t *)(record+2u)=20u;
 (void)opencfw_em9305_memcpy(record+5u,(const void *)input,32u);
 return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)record);
}
