#include <stdint.h>
extern uint32_t opencfw_em9305_init_secondary_notify_313354(uintptr_t);
extern uint32_t opencfw_em9305_init_secondary_fill_324768(uintptr_t,uint8_t *);
extern uint32_t opencfw_em9305_init_secondary_event_30e928(uint32_t,uint32_t,uint8_t *,uint32_t);
/* Full native319094..3190dc. Child324768 owns stack response content;
 * no fabricated zero fill, slot identity uses signed native DIV then EXTB. */
uint32_t opencfw_em9305_init_secondary_action_319094(uintptr_t incoming,uint32_t offset,uint32_t state)
{
 (void)incoming;(void)offset;(void)state;
 uintptr_t root=0x8051a4u;
 if(*(volatile uint8_t *)(root+1u)!=0u){
  uintptr_t record=*(volatile uint32_t *)(root+20u);
  *(volatile uint8_t *)(record+4u)=0u;
  *(volatile uint8_t *)(record+3u)=1u;
  (void)opencfw_em9305_init_secondary_notify_313354(record+48u);
  *(volatile uint8_t *)(root+1u)=0u;
 }
 uint8_t response[20];
 uintptr_t record=*(volatile uint32_t *)(root+20u);
 (void)opencfw_em9305_init_secondary_fill_324768(record,response);
 record=*(volatile uint32_t *)(root+20u);
 int32_t difference=(int32_t)((uint32_t)record-0x803d78u);
 uint32_t slot=(uint8_t)(difference/784);
 uint32_t flag=*(volatile uint8_t *)(record+777u);
 return opencfw_em9305_init_secondary_event_30e928(62u,slot,response,flag);
}
