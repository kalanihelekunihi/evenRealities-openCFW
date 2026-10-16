/* Native prepare 0x30f288..0x30f2b8, config setter 0x31183c..0x311848,
 * timer reset 0x30fa40..0x30fa78. Actual timer children stay explicit. */
#include <stdint.h>
extern uint32_t opencfw_em9305_timer_initialize(uint32_t); /* 0x313a0c */
extern uint32_t opencfw_em9305_timer_enable(uint32_t); /* 0x313ae4 */
extern uint32_t opencfw_em9305_timer_irq_enable(uint32_t); /* 0x313c4c */
static uintptr_t timer_context(void)
{
 return *(volatile uint32_t *)(uintptr_t)0x80fde0u;
}
extern uint32_t opencfw_em9305_timer_calibrate_a(void); /* 0x313bc0 */
extern uint32_t opencfw_em9305_timer_calibrate_b(void); /* 0x313bec */
extern uint32_t opencfw_em9305_timer_rom_set_a(uint32_t); /* 0x104cc4 */
extern uint32_t opencfw_em9305_timer_rom_set_b(uint32_t); /* 0x104d04 */
extern void opencfw_em9305_controller_timer_changed(uint32_t); /* 0x30f944 */
extern uint32_t opencfw_em9305_timer_rom_probe_a(uint32_t); /* 0x104ca4 */
extern uint32_t opencfw_em9305_timer_rom_probe_b(uint32_t); /* 0x104cb4 */
static uint32_t timer_probe(uint32_t value,int alternate)
{
 if (alternate) (void)opencfw_em9305_timer_rom_set_b(value);
 else (void)opencfw_em9305_timer_rom_set_a(value);
 uint32_t clock=*(volatile uint32_t *)(uintptr_t)0xf03800u;
 uint32_t offset=(clock & 1u)!=0u ? 24u : 26u;
 uint32_t count=*(volatile uint16_t *)(uintptr_t)(0x80fdd4u+offset);
 if (count!=0u) {
  /* Stock uses LP_COUNT and two no-ops; retain the architectural loop. */
  __asm__ volatile("mov lp_count,%0\n\tlp 1f\n\tnop\n\tnop_s\n1:"
                   :: "r"(count) : "lp_count", "memory");
 }
 uint32_t probe_argument=count!=0u ? count : UINT32_MAX;
 return alternate ? opencfw_em9305_timer_rom_probe_b(probe_argument) :
                    opencfw_em9305_timer_rom_probe_a(probe_argument);
}
/* Native 0x313bc0/0x313bec search, including its final two decrements. */
static uint32_t timer_calibrate(int alternate)
{
 uint32_t candidate=8,step=8,upper=0,probe=0;
 do {
  step>>=1;
  upper=candidate+step;
  probe=timer_probe((uint32_t)(int32_t)(int8_t)candidate,alternate);
  candidate-=step;
  if (probe!=0u) candidate=upper;
 } while (step!=0u);
 if (probe==0u) {
  upper=candidate-1u;
  if (timer_probe((uint32_t)(int32_t)(int8_t)upper,alternate)==0u)
   upper=candidate-2u;
 }
 return (uint32_t)(int32_t)(int8_t)upper;
}
uint32_t opencfw_em9305_timer_calibrate_a(void) { return timer_calibrate(0); }
uint32_t opencfw_em9305_timer_calibrate_b(void) { return timer_calibrate(1); }
/* Native 0x30f730..0x30f768: packed byte fields, protected update with
 * temporary control-bit disable only if the word actually changes. */
uint32_t opencfw_em9305_controller_timer_word(uint32_t a,uint32_t b,
                                            uint32_t c,uint32_t d)
{
 uint32_t packed=a+(b<<8)+(c<<16)+(d<<24);
 uint32_t irq;
 __asm__ volatile("clri %0\n\tsync" : "=r"(irq) :: "memory");
 volatile uint32_t *word=(volatile uint32_t *)(uintptr_t)0xf00414u;
 uint32_t old=*word;
 if (old!=packed) {
  volatile uint8_t *control=(volatile uint8_t *)(uintptr_t)0xf0041cu;
  uint8_t previous=*control;
  *control=(uint8_t)(previous & ~2u);
  *word=packed;
  *control=previous;
 }
 __asm__ volatile("seti %0" :: "r"(irq) : "memory");
 return old!=packed;
}
/* Native 0x30f944..0x30f998. Product tables are actual root pointers,
 * not inferred replacement data. */
void opencfw_em9305_controller_timer_changed(uint32_t incoming)
{
 (void)incoming;
 volatile uint32_t *mode=(volatile uint32_t *)(uintptr_t)0x80199cu;
 if (*mode!=0u && *mode!=2u) return;
 uintptr_t second=*(volatile uint32_t *)(uintptr_t)0x8012c8u;
 uintptr_t first=*(volatile uint32_t *)(uintptr_t)0x8012c4u;
 int32_t value=*(volatile int8_t *)(uintptr_t)0x8019a0u;
 uint32_t offset=value<1 ? 0u : ((uint32_t)value<<1)&254u;
 if (offset>30u) return;
 uint32_t d=*(volatile uint8_t *)(second+offset+1u);
 uint32_t c=*(volatile uint8_t *)(second+offset);
 uint32_t b=*(volatile uint8_t *)(first+offset+1u);
 uint32_t a=*(volatile uint8_t *)(first+offset);
 (void)opencfw_em9305_controller_timer_word(a,b,c,d);
}
/* Native 0x313c18..0x313c4c: mode is captured before IRQ masking. */
uint32_t opencfw_em9305_timer_select(void)
{
 uint32_t mode=*(volatile uint32_t *)(uintptr_t)0x80199cu;
 uint32_t irq_enabled=opencfw_em9305_timer_irq_enable(0);
 uint32_t selected=0;
 if (mode<2u) selected=opencfw_em9305_timer_calibrate_a();
 else if ((mode & ~1u)==2u) selected=opencfw_em9305_timer_calibrate_b();
 (void)opencfw_em9305_timer_irq_enable(irq_enabled);
 return selected;
}
/* Native 0x313c74..0x313c9c: signed negative values skip ROM writes. */
uint32_t opencfw_em9305_timer_apply(int32_t value)
{
 if (value<0) return (uint32_t)value;
 uint32_t mode=*(volatile uint32_t *)(uintptr_t)0x80199cu;
 if (mode<2u) return opencfw_em9305_timer_rom_set_a((uint32_t)value);
 if ((mode & ~1u)==2u) return opencfw_em9305_timer_rom_set_b((uint32_t)value);
 return (uint32_t)value;
}
/* Native 0x313c9c..0x313cde: signed threshold bytes and native variable
 * bit shifts. Root loads and intermediate 0xff write are observable. */
uint32_t opencfw_em9305_timer_threshold_flags(int32_t threshold)
{
 *(volatile uint8_t *)(timer_context()+14u)=255;
 uint32_t result=*(volatile uint8_t *)(timer_context()+14u);
 uint32_t mask=*(volatile uint8_t *)(timer_context()+11u);
 uintptr_t values=timer_context();
 uint32_t count=*(volatile uint8_t *)(timer_context()+13u);
 for (uint32_t index=0;index<count;index++) {
  if ((mask & (1u << (index & 31u))) != 0u) {
   int32_t value=*(volatile int8_t *)(values+index+4u);
   if (threshold < value) result &= ~(1u << (index & 31u));
  }
 }
 uintptr_t context=timer_context();
 *(volatile uint8_t *)(context+14u)=(uint8_t)result;
 return (uint32_t)context;
}
/* Native 0x313ae4..0x313b4c. The timestamp store is the branch delay
 * instruction, so executes regardless of saved flag bit6. */
uint32_t opencfw_em9305_timer_enable(uint32_t enable)
{
 volatile uint32_t *clock=(volatile uint32_t *)(uintptr_t)0xf0045cu;
 uint32_t now,confirm;
 do { now=*clock; confirm=*clock; } while (now!=confirm);
 volatile uint32_t *interval=(volatile uint32_t *)(uintptr_t)0x80fde8u;
 int update=1;
 if (*interval!=0u) {
  uint32_t bound=*interval;
  uint32_t last=*(volatile uint32_t *)timer_context();
  if (bound >= now-last && enable==0u) update=0;
 }
 volatile uint8_t *selected=(volatile uint8_t *)(uintptr_t)0x8019a0u;
 if (update) {
  uintptr_t before=timer_context();
  uint32_t old=*selected;
  uint32_t flags=*(volatile uint8_t *)(before+14u);
  *selected=(uint8_t)opencfw_em9305_timer_select();
  (void)opencfw_em9305_timer_threshold_flags(*(volatile int8_t *)selected);
  (void)opencfw_em9305_timer_apply(*(volatile int8_t *)selected);
  uint32_t current=*selected;
  if (old!=current) opencfw_em9305_controller_timer_changed(current);
  uintptr_t context=timer_context();
  *(volatile uint32_t *)context=now;
  if ((flags & 64u)!=0u) (void)timer_context();
 }
 return (uint32_t)(int32_t)*(volatile int8_t *)selected;
}
/* Native 0x313a0c..0x313ae2. Reload context for each native root load. */
uint32_t opencfw_em9305_timer_initialize(uint32_t incoming)
{
 (void)incoming;
 *(volatile uint8_t *)(timer_context()+11u)=0;
 *(volatile uint8_t *)(timer_context()+13u)=7;
 volatile uint32_t *mode=(volatile uint32_t *)(uintptr_t)0x80199cu;
 if (*mode==0u || *mode==1u) {
  *(volatile uint8_t *)(timer_context()+4u)=6;
  for (uint32_t bit=0;bit<6u;bit++) {
   uintptr_t context=timer_context();
   volatile uint8_t *flags=(volatile uint8_t *)(context+11u);
   *flags=(uint8_t)(*flags | (1u<<bit));
   *(volatile uint8_t *)(timer_context()+5u+bit)=255;
  }
 } else {
  if (*mode!=2u) {
   uint32_t last=*mode;
   if (last!=3u) return last;
  }
  static const uint8_t values[6]={15,10,7,5,2,2};
  for (uint32_t bit=0;bit<6u;bit++) {
   *(volatile uint8_t *)(timer_context()+5u+bit)=values[bit];
   uintptr_t context=timer_context();
   volatile uint8_t *flags=(volatile uint8_t *)(context+11u);
   *flags=(uint8_t)(*flags | (1u<<(bit+1u)));
  }
 }
 uintptr_t context=timer_context();
 volatile uint8_t *flags=(volatile uint8_t *)(context+11u);
 *flags=(uint8_t)(*flags | 64u);
 return (uint32_t)context;
}
/* Native 0x313c4c..0x313c74: return previous enable bit, with byte-width
 * read/modify/write enclosed by the architectural IRQ save/restore. */
uint32_t opencfw_em9305_timer_irq_enable(uint32_t enable)
{
 uint32_t irq;
 __asm__ volatile("clri %0\n\tsync" : "=r"(irq) :: "memory");
 volatile uint8_t *control=(volatile uint8_t *)(uintptr_t)0xf00406u;
 uint32_t previous=*control;
 *control=(uint8_t)((previous & ~4u) | (enable != 0u ? 4u : 0u));
 __asm__ volatile("seti %0" :: "r"(irq) : "memory");
 return (previous & 4u) >> 2;
}
uint32_t opencfw_em9305_timer_config_pair(uint32_t first,uint32_t second)
{
 *(volatile uint32_t *)(uintptr_t)0x8019b0u=first;
 *(volatile uint32_t *)(uintptr_t)0x8019b4u=second;
 return first;
}
uint32_t opencfw_em9305_controller_prepare_timer(void)
{
 *(volatile uint32_t *)(uintptr_t)0xf00964u=1;
 __asm__ volatile("sync" ::: "memory");
 *(volatile uint32_t *)(uintptr_t)0xf00954u=1;
 *(volatile uint32_t *)(uintptr_t)0xf00948u=1;
 uint32_t first=*(volatile uint32_t *)(uintptr_t)0x80fba0u;
 uint32_t second=*(volatile uint32_t *)(uintptr_t)0x80fba4u;
 (void)opencfw_em9305_timer_config_pair(first,second);
 uintptr_t context=*(volatile uint32_t *)(uintptr_t)0x80fb8cu;
 *(volatile uint8_t *)(context+38u)=0;
 return (uint32_t)context;
}
uint32_t opencfw_em9305_controller_timer_reset(uint32_t incoming)
{
 (void)opencfw_em9305_timer_initialize(incoming);
 uintptr_t context=*(volatile uint32_t *)(uintptr_t)0x80fde0u;
 *(volatile uint8_t *)(context+14u)=0;
 (void)opencfw_em9305_timer_enable(1);
 (void)opencfw_em9305_timer_irq_enable(1);
 *(volatile uint32_t *)(uintptr_t)0xf009acu=1;
 __asm__ volatile("sync" ::: "memory");
 *(volatile uint32_t *)(uintptr_t)0xf00990u=1;
 *(volatile uint32_t *)(uintptr_t)0xf0099cu=1;
 return 0xf009acu;
}
