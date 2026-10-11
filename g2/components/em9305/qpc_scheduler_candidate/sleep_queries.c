/* Native readiness 0x30f568..0x30f57c and controller predicate
 * 0x30f60c..0x30f65c. Repeated volatile context reads preserve widths.
 * Controller callback receives its own address in native R0. */
#include <stdint.h>
static uintptr_t context(void) { return *(volatile uint32_t *)(uintptr_t)0x80fb8cu; }
uint32_t opencfw_em9305_sleep_ready_query(uint32_t incoming)
{ (void)incoming; return *(volatile uint8_t *)(context()+40u)==0; }
uint32_t opencfw_em9305_sleep_controller_query(uint32_t incoming)
{
 (void)incoming;
 if(*(volatile uint8_t *)(context()+36u)==1 && *(volatile uint8_t *)(context()+37u)==0) return 0;
 uintptr_t object=*(volatile uint32_t *)(uintptr_t)0x801090u;
 if(object!=0) {
  uintptr_t callback=*(volatile uint32_t *)(object+32u);
  if(callback!=0 && ((uint32_t (*)(uintptr_t))callback)(callback)==0) return 0;
 }
 if(*(volatile uint8_t *)(context()+39u)!=0) return 0;
 if(*(volatile uint8_t *)(uintptr_t)0x80fbbcu!=0) return 0;
 return 1;
}

/* Native state query 0x302de4..0x302df4, ignores incoming R0. */
uint32_t opencfw_em9305_sleep_state_query(uint32_t incoming)
{ (void)incoming; return *(volatile uint32_t *)(uintptr_t)0x8018e4u==0; }

/* Native mask update 0x302e64..0x302e80 and dual-group adapter
 * 0x30f6ec..0x30f710. Source stores use exact word widths. */
uint32_t opencfw_em9305_sleep_group_mask(uint32_t group,uint32_t mask,uint32_t enable)
{
 volatile uint32_t *slot=(volatile uint32_t *)(uintptr_t)(0x8018ecu+(group!=0)*4u);
 uint32_t value=*slot;
 value=enable!=0 ? value|mask : value&~mask;
 *slot=value;
 return value;
}
void opencfw_em9305_sleep_controller_enable(uint32_t group,uint32_t mask,uint32_t enable)
{
 if(group==1) (void)opencfw_em9305_sleep_group_mask(1,mask,enable);
 else if(group!=0) return;
 (void)opencfw_em9305_sleep_group_mask(0,mask,enable);
}
