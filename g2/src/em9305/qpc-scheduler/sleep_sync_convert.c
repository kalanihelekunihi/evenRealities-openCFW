/* Native 0x30f2d8..0x30f2f0. MPYDU returns unsigned full-width product
 * in R0/R1, followed by tail call to wide division 0x302748. */
#include <stdint.h>
extern uint64_t opencfw_em9305_sleep_sync_divide(uint32_t,uint32_t,uint32_t,uint32_t);
uint64_t opencfw_em9305_sleep_sync_convert(uint32_t delta,uint32_t incoming_r1)
{
 (void)incoming_r1;
 volatile uint32_t *root=(volatile uint32_t *)(uintptr_t)0x80fb8cu;
 uintptr_t first=*root;
 uint32_t factor=*(volatile uint32_t *)(first+8u);
 uintptr_t second=*root;
 uint64_t product=(uint64_t)factor*delta;
 uint32_t denominator=*(volatile uint32_t *)(second+12u);
 return opencfw_em9305_sleep_sync_divide((uint32_t)product,(uint32_t)(product>>32),denominator,0);
}
