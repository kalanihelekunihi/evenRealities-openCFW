/* Synthetic extraction of native sleep branch 0x312714..0x312772,
 * 0x312824..0x3128e4. Child ABI contracts remain explicit; no ARC runtime
 * equivalence or complete controller image is claimed by compilation. */
#include <stdint.h>
extern uint32_t opencfw_em9305_sleep_metadata(uint32_t *,uint32_t *,uint32_t *); /* 0x3125a4 */
extern uint32_t opencfw_em9305_sleep_metadata_action(uint32_t,uint32_t,uint32_t,uint32_t); /* 0x30f250 */
extern void opencfw_em9305_sleep_controller_enable(uint32_t,uint32_t,uint32_t); /* 0x30f6ec */
extern void opencfw_em9305_controller_sleep_mode(uint32_t); /* 0x30f374 */
extern uint32_t opencfw_em9305_sleep_ready_query(uint32_t); /* 0x30f568 */
static uint32_t save_irq(void) { uint32_t s; __asm__ volatile("clri %0\n\tsync" : "=r"(s) :: "memory"); return s; }
static void restore_irq(uint32_t s) { __asm__ volatile("seti %0" :: "r"(s) : "memory"); }
static uint32_t link_state(void) { uint32_t s; __asm__ volatile("mov %0,ilink" : "=r"(s) :: "memory"); return s; }
static uintptr_t object(void) { return *(volatile uint32_t *)(uintptr_t)0x801090u; }
static uintptr_t callback(uintptr_t o,uint32_t offset) { return *(volatile uint32_t *)(o+offset); }
static void notify(uint32_t event) { uintptr_t o=object(); if(o) { uintptr_t f=callback(o,12); if(f) ((void (*)(uint32_t,uintptr_t))f)(event,f); } }
static uint32_t update(uintptr_t address,uint8_t clear,uint8_t set) {
 uint32_t irq=save_irq(); volatile uint8_t *p=(volatile uint8_t *)address;
 uint8_t value=(uint8_t)((*p & (uint8_t)~clear)|set); *p=value; restore_irq(irq); return value;
}
uint32_t opencfw_em9305_sleep_controller_branch(void) {
 uint32_t outputs[3]; /* Written by the native metadata contract, not fabricated defaults. */
 uint32_t type=opencfw_em9305_sleep_metadata(&outputs[2],&outputs[1],&outputs[0]);
 uint32_t transient; uintptr_t o,f;
 if(type==2) goto loop_start;
 o=object();
 if(o) {
  f=callback(o,24);
  if(f) { if(((uint32_t (*)(uintptr_t,uintptr_t))f)(o,f)) goto loop_start; o=object(); if(!o) goto prepare; }
  f=callback(o,28);
  if(f) { if(((uint32_t (*)(uintptr_t,uintptr_t))f)(o,f)) goto loop_start; o=object(); if(!o) goto prepare; }
  f=callback(o,12); if(f) ((void (*)(uint32_t,uintptr_t))f)(1,f);
 }
prepare:
 (void)update(0xf00407u,0,4); (void)update(0xf00405u,0,1);
 o=object();
 if(o) {
  f=callback(o,28);
  if(f) { transient=1; if(((uint32_t (*)(uintptr_t,uintptr_t))f)(o,f)) goto restart_notify; o=object(); if(!o) goto metadata_action; }
  f=callback(o,24);
  if(f) { transient=1; if(((uint32_t (*)(uintptr_t))f)(f)) goto restart_notify; }
 }
metadata_action:
 if(type==0) {
  if(!opencfw_em9305_sleep_metadata_action(outputs[2],0,outputs[1],outputs[0])) goto loop_start;
  opencfw_em9305_sleep_controller_enable(1,65536,1);
 }
 transient=1;
 if(link_state()!=0 || *(volatile uint32_t *)(uintptr_t)0xf0383cu!=0) goto restart_notify;
 opencfw_em9305_controller_sleep_mode(*(volatile uint8_t *)(uintptr_t)0x80fbbdu);
loop_start:
 transient=0;
restart_notify:
 notify(0);
 { uint32_t state=update(0xf00405u,1,0);
   if(transient==0 && opencfw_em9305_sleep_ready_query(state)!=0) {
    uint32_t irq=save_irq();
    if(link_state()!=0) restore_irq(irq);
    else { uint32_t sleep_state=irq&31u; __asm__ volatile("sleep %0" :: "r"(sleep_state) : "memory"); }
   }
 }
 return save_irq();
}
