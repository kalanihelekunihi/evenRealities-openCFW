/* Native refresh 0x30f9d0..0x30fa08. Native incidental R0 carry
 * is explicit; actual slot updater remains a source contract 0x30f218. */
#include <stdint.h>
extern uint32_t opencfw_em9305_sleep_refresh_slot(uint32_t,uint32_t);
uint32_t opencfw_em9305_sleep_refresh(uint32_t incoming)
{
 uint32_t enabled=*(volatile uint8_t *)(uintptr_t)0xf00466u&15u;
 uint32_t result=incoming;
 for(uint32_t index=0;index<4;index++) if((enabled&(1u<<index))!=0) {
  uintptr_t context=*(volatile uint32_t *)(uintptr_t)0x80fb8cu;
  result=*(volatile uint32_t *)(context+20u+index*4u);
  if(result!=0) {
   context=*(volatile uint32_t *)(uintptr_t)0x80fb8cu;
   result=*(volatile uint32_t *)(context+20u+index*4u);
   result=opencfw_em9305_sleep_refresh_slot(result,index);
  }
 }
 return result;
}
