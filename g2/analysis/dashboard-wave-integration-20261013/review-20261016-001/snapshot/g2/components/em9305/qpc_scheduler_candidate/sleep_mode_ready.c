/* Native 0x30f57c..0x30f60c. Retain XB FU and conditional carry
 * selection as native operations instead of guessing bitfield semantics. */
#include <stdint.h>
extern uint64_t opencfw_em9305_sleep_sync_convert(uint32_t,uint32_t);
uint32_t opencfw_em9305_sleep_mode_ready(uint32_t low,uint32_t high)
{
 if(*(volatile uint8_t *)(uintptr_t)0x80fbbcu!=0) return 0;
 volatile uint8_t *status=(volatile uint8_t *)(uintptr_t)0xf0383au;
 uint32_t first=(*status>>1u)&1u,second=(*status>>1u)&1u;
 if(first!=second) first=(*status>>1u)&1u;
 if(first==0) return 1;
 uint32_t mask=*(volatile uint32_t *)(uintptr_t)0xf00464u;
 __asm__ volatile("xbfu %0,%0,112" : "+r"(mask));
 uint32_t earliest=UINT32_MAX;
 if(mask!=0) {
  for(uint32_t bit=0;bit<4;bit++) if((mask&(1u<<bit))!=0) {
   uint32_t value=*(volatile uint32_t *)(uintptr_t)(0xf00468u+4u*bit);
   __asm__ volatile("cmp %1,%0\n\tmov.c %0,%1" : "+r"(earliest) : "r"(value) : "cc");
  }
  volatile uint32_t *timer=(volatile uint32_t *)(uintptr_t)0xf0045cu;
  uint32_t now,again; do {now=*timer;again=*timer;} while(now!=again);
  earliest+=~now;
 }
 uint64_t available=opencfw_em9305_sleep_sync_convert(earliest,0);
 return (((uint64_t)high<<32)|low)<available;
}
