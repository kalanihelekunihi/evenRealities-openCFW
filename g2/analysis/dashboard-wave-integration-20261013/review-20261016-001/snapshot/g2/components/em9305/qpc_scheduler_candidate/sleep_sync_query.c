/* Native 0x310b08..0x310b54. Explicit volatile register write sequence;
 * static native correspondence, without physical peripheral qualification. */
#include <stdint.h>
static uintptr_t context(void) { return *(volatile uint32_t *)(uintptr_t)0x80fd2cu; }
uint32_t opencfw_em9305_sleep_sync_query(uint32_t incoming)
{
 (void)incoming;
 uint32_t state=*(volatile uint32_t *)(context()+76u);
 if(state==0) {
  volatile uint32_t *config=(volatile uint32_t *)(uintptr_t)0xf01804u;
  *config=*config|(1u<<17);
  *(volatile uint32_t *)(uintptr_t)0xf00820u=512;
  __asm__ volatile("sync" ::: "memory");
  *(volatile uint32_t *)(uintptr_t)0xf00810u=512;
  *(volatile uint32_t *)(uintptr_t)0xf00804u=512;
  *(volatile uint32_t *)(uintptr_t)0xf01814u=*(volatile uint32_t *)(context()+4u);
  *(volatile uint32_t *)(uintptr_t)0xf01800u=512;
  *(volatile uint32_t *)(uintptr_t)0xf01800u=1;
  *(volatile uint32_t *)(context()+76u)=1;
 }
 return state==0;
}
