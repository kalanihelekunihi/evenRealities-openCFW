/* Native 0x30f218..0x30f288 and inverse converter 0x30f2b8..0x30f2d8.
 * Native delay-slot store occurs before clock call. Child timer-program
 * register facade 0x3137b4 remains explicit and unqualified. */
#include <stdint.h>
extern uint32_t opencfw_em9305_sleep_metadata_clock(uint32_t);
extern uint64_t opencfw_em9305_sleep_sync_divide(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_sleep_program_slot(uint32_t,uint32_t,uint32_t,uint32_t);
static uintptr_t context(void) { return *(volatile uint32_t *)(uintptr_t)0x80fb8cu; }
uint64_t opencfw_em9305_sleep_inverse_convert(uint32_t low,uint32_t high)
{
 uintptr_t c=context(); uint32_t factor=*(volatile uint32_t *)(c+12u);
 uint64_t product=(uint64_t)factor*low;
 c=context();
 uint32_t upper=(uint32_t)(product>>32)+(uint32_t)(high*factor);
 uint32_t denominator=*(volatile uint32_t *)(c+8u);
 return opencfw_em9305_sleep_sync_divide((uint32_t)product,upper,denominator,0);
}
uint32_t opencfw_em9305_sleep_refresh_slot(uint32_t value,uint32_t index)
{
 uintptr_t c=context(); *(volatile uint32_t *)(c+20u+index*4u)=value;
 uint32_t clock=opencfw_em9305_sleep_metadata_clock(value);
 uint64_t converted=opencfw_em9305_sleep_inverse_convert(value-clock,0);
 volatile uint32_t *timer=(volatile uint32_t *)(uintptr_t)0xf0045cu;
 uint32_t first,second; do { first=*timer;second=*timer; } while(first!=second);
 return opencfw_em9305_sleep_program_slot((uint32_t)converted+first,index,first,second);
}
uint32_t opencfw_em9305_sleep_metadata_action(uint32_t deadline,uint32_t index,uint32_t distance,uint32_t origin)
{
 uint32_t base=*(volatile uint32_t *)context();
 uint32_t period=*(volatile uint32_t *)(context()+4u);
 uint32_t before=base-origin;
 uint32_t target=before+period;
 target+=opencfw_em9305_sleep_metadata_clock(before);
 if(distance>=target) {
  uint32_t start=*(volatile uint32_t *)context();
  (void)opencfw_em9305_sleep_refresh_slot(deadline-start,index);
 }
 return distance>=target;
}
