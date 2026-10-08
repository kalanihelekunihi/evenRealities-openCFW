/* SPDX-License-Identifier: MIT. Locked f89a4c46 timer-service reconstruction.
 * Actual instructions override Ghidra's spurious privilege branch and the
 * public PCM2.2 10us waits: stock 2b/7b use delay(5).
 */
#include <stdint.h>
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
extern uint32_t opencfw_boot_control_critical_save(void);
extern void opencfw_hal_delay_us(uint32_t);
extern uint32_t opencfw_hal_status_poll(uint32_t,uintptr_t,uint32_t,uint32_t,uint32_t);
extern uint32_t clock_request(uint32_t,uint32_t);
extern uint32_t clock_release(uint32_t,uint32_t);
void opencfw_pcm22_spot_timer_start(uint32_t wait){
 (void)clock_request(4,0x31);W(0x400083e8)=wait*6;
 W(0x40008010)|=0x8000;W(0x400083e0)|=2;W(0x400083e0)&=~2u;
 W(0xe000e108)=0x40000;W(0x400083e0)|=1;
}
void opencfw_pcm22_spot_timer_stop(void){
 W(0x400083e0)&=~1u;W(0x40008010)&=~0x8000u;(void)clock_release(4,0x31);
 W(0xe000e188)=0x40000;W(0x40008068)=0xc0000000;(void)W(0x47ff0000);W(0xe000e288)=0x40000;
}
uint32_t opencfw_pcm22_icache_disable(void){
 if((W(0xe001e300)&0x300)!=0)return 1;
 __asm volatile("dsb sy\n\tisb sy" ::: "memory");
 W(0xe000ed14)&=~0x20000u;W(0xe000ef50)=0;
 __asm volatile("dsb sy\n\tisb sy" ::: "memory");return 0;
}
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
