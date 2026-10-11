/* Native metadata preparation 0x3125a8..0x312674. Volatile views retain
 * native widths and repeated reads. XB FU is retained as the actual ARC EM
 * instruction rather than assigning unverified arithmetic semantics. */
#include <stdint.h>
extern uint32_t opencfw_em9305_sleep_metadata_rom(uint32_t,uintptr_t,uintptr_t); /* 0x103b0c */
extern uint32_t opencfw_em9305_sleep_register(uintptr_t); /* 0x311848 */
extern uint32_t opencfw_em9305_sleep_finalize(uint32_t); /* 0x3117f8 */
extern void opencfw_em9305_sleep_registered_callback(void); /* 0x3128e4 */
static uintptr_t context(void) { return *(volatile uint32_t *)(uintptr_t)0x80fb8cu; }
static uint8_t byte(uintptr_t p) { return *(volatile uint8_t *)p; }
static void put(uintptr_t p,uint8_t value) { *(volatile uint8_t *)p=value; }
uint32_t opencfw_em9305_sleep_metadata_prepare(uint32_t *deadline,uint32_t *distance,uint32_t *origin)
{
 (void)deadline;
 (void)opencfw_em9305_sleep_metadata_rom(3,(uintptr_t)distance,(uintptr_t)origin);
 uint32_t value=byte(context()+38u);
 if(value!=0) return value;
 value=byte(0x80fbbcu); if(value!=0) return value;
 value=byte(context()+42u); if(value==0) return value;
 volatile uint32_t *timer=(volatile uint32_t *)(uintptr_t)0xf0045cu;
 uint32_t now,again;
 do { now=*timer; again=*timer; } while(now!=again);
 uint32_t limit=*(volatile uint32_t *)(uintptr_t)0x80fba8u;
 if(limit!=0) {
  limit=*(volatile uint32_t *)(uintptr_t)0x80fba8u;
  uint32_t elapsed=now-*(volatile uint32_t *)(context()+16u);
  if(limit>=elapsed && byte(context()+41u)!=0) {
   uintptr_t c=context(); put(c+42u,0); return (uint32_t)c;
  }
 }
 put(context()+41u,1); put(context()+43u,1);
 put(context()+44u,0); put(context()+45u,0);
 if(*(volatile uint32_t *)(uintptr_t)0x80199cu==0 && byte(0x80fbbfu)!=0) {
  uint32_t irq;
  __asm__ volatile("clri %0\n\tsync" : "=r"(irq) :: "memory");
  volatile uint32_t *control=(volatile uint32_t *)(uintptr_t)0xf00404u;
  uint32_t old=*control; *control=old|(1u<<17);
  __asm__ volatile("seti %0" :: "r"(irq) : "memory");
  uint32_t field;
  __asm__ volatile("xbfu %0,%1,0x11" : "=r"(field) : "r"(old));
  put(context()+44u,(uint8_t)field); put(context()+45u,1);
 }
 put(context()+42u,0);
 value=opencfw_em9305_sleep_register((uintptr_t)opencfw_em9305_sleep_registered_callback);
 return opencfw_em9305_sleep_finalize(value);
}
