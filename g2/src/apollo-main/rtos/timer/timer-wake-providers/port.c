/* Offline reconstruction from authenticated stock Thumb instructions.
 * Named architectural operations; no retained opcode arrays. */
#include <stdint.h>
static volatile uint32_t * const nesting=(volatile uint32_t *)0x2000309cu;
extern void stock_bad_critical_exit(void) __attribute__((noreturn));
uint32_t audio_port_mask_set(void){
 uint32_t previous;const uint32_t threshold=0x30;
 __asm__ volatile("mrs %0, basepri\n\tmsr basepri, %1\n\tdsb\n\tisb":"=&r"(previous):"r"(threshold):"memory");
 return previous;
}
void audio_port_mask_restore(uint32_t previous){
 __asm__ volatile("msr basepri, %0"::"r"(previous):"memory");
}
void stock_enter_critical(void){
 (void)audio_port_mask_set();*nesting=*nesting+1u;
 __asm__ volatile("dsb\n\tisb":::"memory");
}
void stock_exit_critical(void){
 if(*nesting==0){(void)audio_port_mask_set();stock_bad_critical_exit();}
 *nesting=*nesting-1u;if(*nesting==0)audio_port_mask_restore(0);
}
void stock_missed_yield(void){*(volatile uint32_t *)0x20074a44u=1;}
