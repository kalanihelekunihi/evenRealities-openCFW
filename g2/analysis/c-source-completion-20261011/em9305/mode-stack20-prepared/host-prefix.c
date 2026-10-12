#include <stdint.h>
extern uint32_t opencfw_em9305_mode_event_322fdc(uintptr_t,uint32_t);
uint32_t opencfw_em9305_mode_event_31ac3c(uintptr_t context)
{
 uint32_t flags=*(volatile uint32_t *)(context+636u);
 if((flags&(1u<<17u))==0u)return (uint32_t)context;
 uint32_t byte12=*(volatile uint8_t *)(context+12u);
 *(volatile uint32_t *)(context+636u)=flags&~(1u<<17u);
 *(volatile uint32_t *)(context+640u)=0u;
 return opencfw_em9305_mode_event_322fdc(context,byte12);
}
