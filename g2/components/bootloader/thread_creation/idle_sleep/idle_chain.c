/* Reconstructed fixed-address bootloader bodies, not an Apollo timing model. */
#include <stdint.h>
#define W(p) (*(volatile uint32_t *)(uintptr_t)(p))
extern void opencfw_bl_kernel_enter(void),opencfw_bl_kernel_exit(void);
extern uint32_t opencfw_bl_mask_interrupts(void);
static void assertion(void){(void)opencfw_bl_mask_interrupts();W(UINT32_MAX)=0;for(;;)__asm__ volatile("b .");}
void step_ticks(uint32_t jump){
 if(W(0x20027164)<W(0x20027148)+jump)assertion();
 if(W(0x20027148)+jump==W(0x20027164)){
  if(!W(0x2002716c))assertion();if(!jump)assertion();
  opencfw_bl_kernel_enter();W(0x20027154)++;opencfw_bl_kernel_exit();jump--;
 }
 W(0x20027148)+=jump;
}
void sample_three(uintptr_t address,uint32_t *out){
 uint32_t old;__asm__ volatile("mrs %0,primask\n cpsid i":"=r"(old)::"memory");
 uint32_t x=W(address),y=W(address),z=W(address);
 __asm__ volatile("msr primask,%0"::"r"(old):"memory");
 out[0]=x;out[1]=y;out[2]=z;
}
uint32_t counter_read(void){uint32_t v[3];sample_three(0x40008804,v);return v[0]==v[1]?v[1]:v[2];}
uint32_t irq_save(void){uint32_t old;__asm__ volatile("mrs %0,primask\n cpsid i":"=r"(old)::"memory");return old;}
uint32_t timer_compare(uint32_t channel,uint32_t delta){
 uint32_t start=counter_read(),now=start,status=0;
 if(channel>=8)return 5;
 while(now==W(0x200001c8+4*channel)||now==W(0x200001c8+4*channel)+1)now=counter_read();
 uint32_t mask=irq_save();now=counter_read();
 if(now-start+3>=delta){delta=1;status=0x08000000;}else delta=delta-now+start-3;
 W(0x40008820+4*channel)=delta;W(0x200001c8+4*channel)=counter_read();
 __asm__ volatile("msr primask,%0"::"r"(mask):"memory");return status;
}
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
