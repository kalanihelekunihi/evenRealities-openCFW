/* SPDX-License-Identifier: MIT
 * Reconstructed locked41b754..41b818. Counter-wrap formula preserved.
 * This is a bounded addon with timer/hook interfaces, not hardware timing.
 */
#include <stdint.h>
#define W(p) (*(volatile uint32_t *)(uintptr_t)(p))
extern uint32_t confirm_sleep(void),counter_read(void),pre_sleep(uint32_t);
extern void timer_compare(uint32_t,uint32_t),post_sleep(uint32_t),timer_enable(uint32_t),irq_clear(uint32_t),step_ticks(uint32_t);
static uint32_t elapsed(uint32_t now,uint32_t before){return now<before?now+(UINT32_MAX-before):now-before;}
void tickless_sleep(uint32_t expected) {
 if(W(0x20027128u)<expected)expected=W(0x20027128u);
 __asm__ volatile("cpsid i\n dsb sy\n isb sy":::"memory");
 if(!confirm_sleep()) {__asm__ volatile("cpsie i":::"memory");return;}
 uint32_t now=counter_read();
 timer_compare(0,expected*W(0x20027124u)-elapsed(now,W(0x20027120u)));
 if(pre_sleep(expected)){__asm__ volatile("dsb sy\n wfi\n isb sy":::"memory");}
 post_sleep(expected);now=counter_read();
 uint32_t distance=elapsed(now,W(0x20027120u));
 uint32_t ticks=distance/W(0x20027124u), remainder=distance%W(0x20027124u);
 W(0x20027120u)=now-remainder;
 timer_enable(1);irq_clear(0x20);timer_compare(0,W(0x20027124u)-remainder);
 step_ticks(ticks<expected?ticks:expected);
 __asm__ volatile("cpsie i":::"memory");
}
