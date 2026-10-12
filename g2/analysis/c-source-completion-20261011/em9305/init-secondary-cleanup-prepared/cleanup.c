#include <stdint.h>
extern uint32_t opencfw_em9305_common_release_304588(uint32_t);
extern uint32_t opencfw_em9305_command_count_down_30e48c(void);
extern uint32_t opencfw_em9305_wsf_event_release(uintptr_t);
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t);
extern uint32_t opencfw_em9305_wsf_task_message_send(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_init_secondary_event_30e928(uint32_t,uint32_t,uint8_t *,uint32_t);
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
uint32_t opencfw_em9305_init_secondary_count_down_30e47c(void)
{
 uint32_t count=*(volatile uint8_t *)(uintptr_t)0x805a77u;
 *(volatile uint8_t *)(uintptr_t)0x805a77u=(uint8_t)(count-1u);
 return 0x805a77u;
}
/* Full321450..32148c; typed callback is original record slot+12. */
uint32_t opencfw_em9305_init_secondary_cleanup_321450(uintptr_t record)
{
 (void)opencfw_em9305_common_release_304588(1u);
 uintptr_t callback=*(volatile uint32_t *)(record+12u);
 if(callback!=0u){
  int32_t difference=(int32_t)((uint32_t)record-0x803d78u);
  int32_t quotient=difference/784;
  (void)((uint32_t (*)(uint32_t,uint32_t,uintptr_t))callback)((uint8_t)quotient,(uint32_t)quotient,callback);
 }
 uint32_t flagged=*(volatile uint8_t *)(record+624u);
 if(flagged!=0u)(void)opencfw_em9305_init_secondary_count_down_30e47c();
 (void)opencfw_em9305_command_count_down_30e48c();
 uintptr_t pending=*(volatile uint32_t *)(record+604u);
 uint32_t result=(uint32_t)pending;
 if(pending!=0u)result=opencfw_em9305_wsf_event_release(pending);
 *(volatile uint8_t *)record=0u;
 return result;
}
/* Full3190e0..3191aa. Source preserves fresh-root record loads around
 * message children and native R0 at each return. */
uint32_t opencfw_em9305_init_secondary_action_3190e0(uintptr_t incoming,uint32_t offset,uint32_t state)
{
 (void)incoming;(void)offset;(void)state;uintptr_t root=0x8051a4u;
 if(*(volatile uint8_t *)(root+1u)!=0u)*(volatile uint8_t *)(root+1u)=0u;
 uintptr_t record=*(volatile uint32_t *)(root+20u);
 (void)opencfw_em9305_init_secondary_cleanup_321450(record);
 record=*(volatile uint32_t *)(root+20u);
 _Alignas(4) uint8_t response[20];
 if(*(volatile uint8_t *)(record+4u)!=0u){
  (void)opencfw_em9305_memset(response,0u,18u);
  uint32_t slot=(uint8_t)((int32_t)((uint32_t)record-0x803d78u)/784);
  uint32_t flag=*(volatile uint8_t *)(record+777u);
  (void)opencfw_em9305_init_secondary_event_30e928(68u,slot,response,flag);
  record=*(volatile uint32_t *)(root+20u);
 }
 uint32_t armed=*(volatile uint8_t *)(record+603u);
 if(armed==0u)return 0u;
 uint32_t flags=*(volatile uint8_t *)(root+4u);
 if((flags&1u)==0u){
  (void)opencfw_em9305_memset(response,0u,18u);
  uint32_t slot=(uint8_t)((int32_t)((uint32_t)record-0x803d78u)/784);
  uint32_t flag=*(volatile uint8_t *)(record+777u);
  (void)opencfw_em9305_init_secondary_event_30e928(26u,slot,response,flag);
 }else{
  uintptr_t message=opencfw_em9305_wsf_event_allocate(24u);
  if(message!=0u){
   *(volatile uint16_t *)(message+2u)=267u;
   uint32_t high=*(volatile uint32_t *)(root+12u),b=*(volatile uint8_t *)(root+6u),a=*(volatile uint8_t *)(root+5u);
   *(volatile uint32_t *)(message+12u)=high;
   uint32_t freshflags=*(volatile uint8_t *)(root+4u),low=*(volatile uint32_t *)(root+8u);
   *(volatile uint8_t *)(message+7u)=(uint8_t)b;*(volatile uint8_t *)(message+6u)=(uint8_t)a;
   *(volatile uint8_t *)(message+4u)=(uint8_t)freshflags;*(volatile uint32_t *)(message+8u)=low;
   uintptr_t freshrecord=*(volatile uint32_t *)(root+20u);
   uint32_t enabled=*(volatile uint8_t *)(freshrecord+6u);*(volatile uint8_t *)(message+5u)=(uint8_t)enabled;
   uint32_t period=*(volatile uint32_t *)(freshrecord+620u);*(volatile uint16_t *)(message+18u)=(uint16_t)period;
   uint32_t half=*(volatile uint16_t *)(freshrecord+616u);*(volatile uint16_t *)(message+16u)=(uint16_t)half;
   uint32_t option=*(volatile uint8_t *)(root+16u),handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
   *(volatile uint8_t *)(message+21u)=(uint8_t)option;
   (void)opencfw_em9305_wsf_task_message_send(handler,message);
  }
 }
 record=*(volatile uint32_t *)(root+20u);
 *(volatile uint8_t *)(record+603u)=0u;
 return (uint32_t)(record+603u);
}
