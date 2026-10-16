/* Native controller mode 0x30f374..0x30f468. Explicit real lower
 * contracts retain observed registers. Arithmetic at 0x30f400 uses the
 * native operation port, not an inferred multiply. ARC/hardware runtime
 * equality and child ABIs remain unqualified. */
#include <stdint.h>
extern uint32_t opencfw_em9305_sleep_mode_ready(uint32_t,uint32_t); /* 0x30f57c */
extern uint32_t opencfw_em9305_sleep_refresh(uint32_t); /* 0x30f9d0 */
extern uint32_t opencfw_em9305_sleep_enter_mode(uint32_t); /* 0x30f468 */
extern uint32_t opencfw_em9305_native_clock_product(uint32_t,uint32_t);
extern uint64_t opencfw_em9305_sleep_sync_divide(uint32_t,uint32_t,uint32_t,uint32_t);
static uintptr_t context(void) { return *(volatile uint32_t *)(uintptr_t)0x80fb8cu; }
static uint32_t save_irq(void) { uint32_t s; __asm__ volatile("clri %0\n\tsync" : "=r"(s) :: "memory"); return s; }
static void restore_irq(uint32_t s) { __asm__ volatile("seti %0" :: "r"(s) : "memory"); }
void opencfw_em9305_controller_sleep_mode(uint32_t mode)
{
 uint32_t period=*(volatile uint32_t *)(context()+4u);
 if(*(volatile uint8_t *)(context()+36u)==1 && *(volatile uint8_t *)(context()+37u)==0) return;
 if(opencfw_em9305_sleep_mode_ready(period,0)==0) return;
 if((*(volatile uint8_t *)(uintptr_t)0xf0383bu&3u)==3u) {
  uint32_t flag=*(volatile uint8_t *)(context()+38u);
  if(flag!=0) (void)opencfw_em9305_sleep_refresh(flag);
  else {
   if(*(volatile uint8_t *)(context()+43u)!=0) {
    *(volatile uint8_t *)(context()+43u)=0;
    uint32_t irq;
    for(;;) {
     irq=save_irq();
     if((*(volatile uint32_t *)(uintptr_t)0xf01c08u&1u)==0) break;
     uint32_t masked=irq&31u; __asm__ volatile("sleep %0" :: "r"(masked) : "memory");
    }
    restore_irq(irq);
    uint32_t ticks=*(volatile uint32_t *)(uintptr_t)0x8019bcu;
    int32_t trim=*(volatile int16_t *)(uintptr_t)0x80fbacu;
    uintptr_t destination=context();
    uintptr_t denominator_context=context();
    uint32_t count=*(volatile uint32_t *)(uintptr_t)0x8019b8u;
    uint32_t denominator=opencfw_em9305_native_clock_product(ticks,400);
    uint64_t numerator=(uint64_t)count*UINT32_C(200000000);
    *(volatile uint32_t *)(denominator_context+12u)=denominator;
    uint32_t divisor=(uint32_t)(trim+1000000);
    uint64_t converted=opencfw_em9305_sleep_sync_divide((uint32_t)numerator,(uint32_t)(numerator>>32),divisor,0);
    *(volatile uint32_t *)(destination+8u)=(uint32_t)converted;
    (void)opencfw_em9305_sleep_refresh((uint32_t)converted);
   }
   *(volatile uint8_t *)(context()+42u)=1;
  }
 }
 uint32_t irq=save_irq(),link;
 __asm__ volatile("mov %0,ilink" : "=r"(link) :: "memory");
 if(link==0 && opencfw_em9305_sleep_mode_ready(period,0)!=0) {
  (void)opencfw_em9305_sleep_enter_mode(mode);
 } else {
  uint32_t nested=save_irq();
  volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)0xf00405u;
  *state=(uint8_t)(*state&~1u); restore_irq(nested);
 }
 restore_irq(irq);
}
