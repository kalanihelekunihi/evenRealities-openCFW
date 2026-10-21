/* Native metadata synchronization 0x310990..0x310a4c. Child ABI
 * facades remain unresolved; direct peripheral behavior is unverified. */
#include <stdint.h>
extern uint32_t opencfw_em9305_sleep_rom_start(uint32_t); /* 0x103b20 */
extern uint32_t opencfw_em9305_sleep_rom_configure(uint32_t); /* 0x103b54 */
extern uint32_t opencfw_em9305_sleep_sync_query(uint32_t); /* 0x310b08 */
extern uint32_t opencfw_em9305_sleep_sync_restore(uint32_t); /* 0x310cec */
extern uint32_t opencfw_em9305_sleep_sync_update(uint32_t); /* 0x310a4c */
static uintptr_t context(void) { return *(volatile uint32_t *)(uintptr_t)0x80fd2cu; }
uint32_t opencfw_em9305_sleep_metadata_sync(uint32_t incoming)
{
 (void)incoming;
 uint32_t state=*(volatile uint32_t *)(context()+76u);
 if(state==2) { *(volatile uint32_t *)(uintptr_t)0xf01800u=1; return state; }
 state=*(volatile uint32_t *)(context()+76u); if(state!=0) return state;
 (void)opencfw_em9305_sleep_rom_start(3);
 uint32_t result=opencfw_em9305_sleep_rom_configure(3);
 result=opencfw_em9305_sleep_sync_query(result); if(result==0) return result;
 uint32_t irq;
 for(;;) {
  __asm__ volatile("clri %0\n\tsync" : "=r"(irq) :: "memory");
  if((*(volatile uint32_t *)(uintptr_t)0xf0180cu&1u)!=0) break;
  uint32_t masked=irq&31u; __asm__ volatile("sleep %0" :: "r"(masked) : "memory");
 }
 __asm__ volatile("seti %0" :: "r"(irq) : "memory");
 result=opencfw_em9305_sleep_sync_restore(irq);
 (void)opencfw_em9305_sleep_sync_update(result);
 uint32_t now=*(volatile uint32_t *)(uintptr_t)0xf01808u;
 uint32_t period=*(volatile uint16_t *)(uintptr_t)0x80fd36u;
 uint32_t divisor=*(volatile uint8_t *)(uintptr_t)0xf01804u+1u;
 uint32_t enabled=*(volatile uint8_t *)(uintptr_t)0xf01818u;
 uint32_t numerator=period*24u,end,mask=0;
 __asm__ volatile("divu %0,%1,%2" : "=r"(end) : "r"(numerator),"r"(divisor));
 for(uint32_t bit=0;bit<8;bit++) if((enabled&(1u<<bit))!=0) {
  uint32_t slot=*(volatile uint32_t *)(uintptr_t)(0xf0181cu+bit*4u);
  uint32_t combined=(end-now+slot)|(now-slot);
  if((combined&0x80000000u)==0) mask|=1u<<bit;
 }
 uint32_t active=*(volatile uint32_t *)(uintptr_t)0xf00800u;
 __asm__ volatile("cmp %1,%2\n\tbset.nc %0,%0,8" : "+r"(mask) : "r"(end),"r"(now) : "cc");
 result=(uint16_t)(active&mask);
 *(volatile uint32_t *)(uintptr_t)0xf0081cu=result;
 return result;
}
