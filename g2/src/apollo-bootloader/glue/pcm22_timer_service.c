/* SPDX-License-Identifier: MIT. Source-owned PCM2.2 timer service and children.
 * Extracted from authenticated timer_support.c; common timer/cache leaves
 * are provided separately by selected modules. */
#include <stdint.h>
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
extern uint32_t opencfw_boot_control_critical_save(void);
extern void opencfw_hal_delay_us(uint32_t);
extern uint32_t opencfw_hal_status_poll(uint32_t,uintptr_t,uint32_t,uint32_t,uint32_t);
extern void opencfw_pcm22_spot_timer_stop(void);
static void apply_cached(void){
 W(0x40020044)=(W(0x40020044)&~0x7fu)|(W(0x200270b0)&0x7f);
 W(0x40020080)=(W(0x40020080)&~0x3c00u)|((W(0x200270bc)&15)<<10);
 W(0x40020080)=(W(0x40020080)&~0x3ffu)|(W(0x200270b8)&0x3ff);
 opencfw_hal_delay_us(5);
}
void opencfw_pcm22_sequence2b(void){
 apply_cached();W(0x4002037c)&=~0x10000u;W(0x4002037c)&=~0x2000000u;
 W(0x4002004c)=(W(0x4002004c)&~0x7fu)|(W(0x200270b4)&0x7f);B(0x2000055a)=26;
}
static void mode_wait(uint32_t mode){
 W(0x40021000)=(W(0x40021000)&~3u)|mode;
 for(uint32_t n=0;n<20&&!(W(0x40021000)&4);n++)opencfw_hal_delay_us(1);
}
void opencfw_pcm22_sequence7b(void){
 apply_cached();W(0x4002004c)=(W(0x4002004c)&~0x7fu)|(W(0x200270b4)&0x7f);
 uint32_t hp=(W(0x40021000)&3)==2;
 if(hp)mode_wait(1);
 W(0x4002037c)|=0x40;W(0x4002037c)|=8;W(0x4002037c)&=~0x2000000u;
 if(hp){uint32_t enable=(W(0x40004044)&0x20)==0;
  if(enable){W(0x40004044)|=0x20;opencfw_hal_delay_us(1);(void)opencfw_hal_status_poll(15,0x40004030,0x1000000,0x1000000,1);}
  if(W(0x40004030)&0x1000000)mode_wait(2);
  if(enable)W(0x40004044)&=~0x20u;
 }
 B(0x2000055a)=26;
}
uint32_t opencfw_pcm22_timer_service(void){
 uint32_t saved=opencfw_boot_control_critical_save();
 if(B(0x2000055a)==2)opencfw_pcm22_sequence2b();
 else if(B(0x2000055a)==7)opencfw_pcm22_sequence7b();
 opencfw_pcm22_spot_timer_stop();
 __asm volatile("msr primask,%0" :: "r"(saved) : "memory");return saved;
}
