/* Reconstructed fixed-address bootloader bodies, not an Apollo timing model. */
#include <stdint.h>
#define W(p) (*(volatile uint32_t *)(uintptr_t)(p))
extern void opencfw_bl_kernel_enter(void),opencfw_bl_kernel_exit(void);
extern uint32_t opencfw_bl_mask_interrupts(void);
static void assertion(void){(void)opencfw_bl_mask_interrupts();W(UINT32_MAX)=0;for(;;){ }}
void step_ticks(uint32_t jump){
 if(W(0x20027164)<W(0x20027148)+jump)assertion();
 if(W(0x20027148)+jump==W(0x20027164)){
  if(!W(0x2002716c))assertion();if(!jump)assertion();
  opencfw_bl_kernel_enter();W(0x20027154)++;opencfw_bl_kernel_exit();jump--;
 }
 W(0x20027148)+=jump;
}
/* am_hal_stimer_counter_get 0x41f424, am_hal_stimer_compare_delta_set 0x41f440,
 * the PRIMASK triple read 0x422aac and am_hal_interrupt_master_disable 0x41b8ec
 * each have one provider: port-timer/port_timer.c
 * (opencfw_bl_port_timer_read_counter/_compare_set),
 * runtime-memory/boot_triple_snapshot.c and upstream am_hal_interrupt.c. */
uint32_t stimer_interrupt_clear(uint32_t bits){W(0x40008908)=bits;return W(0x40008904);}
void irq_clear(uint32_t irq){int16_t n=(int16_t)irq;if(n>=0)W(0xe000e280+4*((uint32_t)n>>5))=1u<<(irq&31);}
extern uint32_t deep_sleep(uint32_t);
uint32_t pre_sleep(uint32_t expected){(void)expected;(void)deep_sleep(1);return 0;}
void post_sleep(uint32_t expected){(void)expected;}
extern uint32_t expected_idle_ticks(void);
extern void cleanup(void),reschedule(void),suspend_scheduler(void),resume_scheduler(void),tickless_sleep(uint32_t);
void idle_entry(void){for(;;){
 cleanup();if(W(0x20024870)>=2)reschedule();
 if(expected_idle_ticks()<2)continue;
 suspend_scheduler();if(W(0x20027164)<W(0x20027148))assertion();
 uint32_t expected=expected_idle_ticks();if(expected>=2)tickless_sleep(expected);
 resume_scheduler();
}}
