/* Unsigned wide quotient entry 0x302748, native long-division path
 * 0x302844..0x30299c. Zero denominator returns native R1:R0
 * 0x7fffffff:0xffffffff (0x30298e..0x302998), not C undefined division.
 * Bitwise division avoids an unresolved compiler wide-divide recursion.
 * Native ARC runtime equivalence remains unverified. */
#include <stdint.h>
uint64_t opencfw_em9305_sleep_sync_divide(uint32_t low,uint32_t high,uint32_t denominator_low,uint32_t denominator_high)
{
 uint64_t dividend=((uint64_t)high<<32)|low;
 uint64_t divisor=((uint64_t)denominator_high<<32)|denominator_low;
 if(divisor==0) return UINT64_C(0x7fffffffffffffff);
 uint64_t quotient=0,remainder=0;
 for(uint32_t remaining=64;remaining!=0;--remaining) {
  uint32_t overflow=(uint32_t)(remainder>>63);
  remainder=(remainder<<1)|((dividend>>(remaining-1u))&1u);
  if(overflow!=0 || remainder>=divisor) {
   remainder-=divisor;
   quotient|=UINT64_C(1)<<(remaining-1u);
  }
 }
 return quotient;
}
