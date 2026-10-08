/* Independent reconstruction of 0x08005048..0x08005086.
 * Polls PWR voltage regulator readiness, not a clock-ready flag.
 * Synthetic tests establish retry counts; no measured physical delay claim. */
#include <stdint.h>
static uint32_t divide_u32(uint32_t n,uint32_t d) {
 uint32_t q=0;
 for(unsigned k=32;k>0;k--) { unsigned i=k-1; if(d<=(n>>i)) { n-=d<<i;q+=1u<<i; } }
 return q;
}
uint32_t case_voltage_scaling(uint32_t scale) {
 volatile uint32_t *pwr=(volatile uint32_t *)0x40007000u;
 pwr[0]=(pwr[0]&~0x600u)|scale;
 if(scale==0x200u) {
  uint32_t clock=*(volatile uint32_t *)0x20000124u;
  uint32_t budget=divide_u32(clock*6u,1000000u)+1u;
  while(pwr[5]&0x400u) {
   if(budget==0u)return 3u;
   --budget;
  }
 }
 return 0u;
}
