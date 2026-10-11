/* Native metadata selection 0x312674..0x3126dc. Preparation remains an
 * explicit synthetic contract for 0x3125a8..0x312674. ARC child register
 * facades express observed arguments, not qualified public SDK signatures. */
#include <stdint.h>
extern uint32_t opencfw_em9305_sleep_metadata_prepare(uint32_t *,uint32_t *,uint32_t *);
extern uint32_t opencfw_em9305_sleep_metadata_sync(uint32_t); /* 0x310990 */
extern uintptr_t opencfw_em9305_sleep_metadata_head(uint32_t); /* 0x3108f4 */
extern uint32_t opencfw_em9305_sleep_metadata_clock(uint32_t); /* 0x310900 */
uint32_t opencfw_em9305_sleep_metadata(uint32_t *deadline,uint32_t *distance,uint32_t *origin)
{
 uint32_t carried=opencfw_em9305_sleep_metadata_prepare(deadline,distance,origin);
 carried=opencfw_em9305_sleep_metadata_sync(carried);
 for(;;) {
  uintptr_t node=opencfw_em9305_sleep_metadata_head(carried);
  uint32_t start=opencfw_em9305_sleep_metadata_clock((uint32_t)node);
  uint32_t status=1,minimum=0,chosen=0;
  carried=start;
  while(node!=0 && status!=2) {
   uintptr_t f=*(volatile uint32_t *)node;
   uint32_t value; /* Only read on status zero, as required by the native child. */
   carried=((uint32_t (*)(uint32_t *,uintptr_t))f)(&value,f);
   if(carried==2) status=2;
   else if(carried==0) {
    uint32_t delta=value-start,previous=status;
    status=0;
    if(previous!=0 || delta<minimum) { minimum=delta; chosen=value; }
    carried=delta;
   }
   node=*(volatile uint32_t *)(node+4u);
  }
  carried=opencfw_em9305_sleep_metadata_clock(carried)-start;
  if(status==0 && carried>=minimum) continue;
  if(status==0) { *deadline=chosen; *distance=minimum; }
  *origin=start;
  return status;
 }
}
