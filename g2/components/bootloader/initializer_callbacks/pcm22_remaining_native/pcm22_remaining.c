/* Locked f89a4c46 selector4:428506..42863e. Timer/cache publication then TON. */
#include <stdint.h>
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
extern void opencfw_hal_delay_us(uint32_t);
extern uint32_t opencfw_pcm22_timer_service(void);
extern void event_a_power_ton_adjust(uint32_t,uint32_t);
uint32_t opencfw_spot_pcm22_transition4(uint32_t target,uint32_t current,uint32_t ton,uint32_t old_ton){
 (void)old_ton;uintptr_t p=0x20026ba0,t=p+4+4*target,o=p+4+4*current;
 uint32_t a=B(p+0x64)&127,b=(W(p+0x64)>>7)&127,c=(W(p+0x64)>>14)&127,d=(W(p+0x64)>>21)&127;
 uint32_t packed=a|(b<<8)|(c<<16)|(d<<24);
 (void)B(o);(void)W(o);uint32_t ldo=(W(t)>>21)&127,vddf=B(t)&127;
 if(W(0x400083e0)&1){uint32_t n=0;while(n<60 && !(W(0x40008064)&0x40000000)){opencfw_hal_delay_us(1);n++;}(void)opencfw_pcm22_timer_service();}
 W(0x200270c0)=ton;W(0x200270c4)=target;
 W(0x200270b8)=(W(t)>>7)&1023;W(0x200270bc)=(W(t)>>17)&15;
 W(0x200270b0)=ldo;W(0x200270b4)=vddf;
 W(0x40020080)=(W(0x40020080)&~0x3c00u)|(((W(t)>>17)&15)<<10);
 W(0x40020080)=(W(0x40020080)&~1023u)|((W(t)>>7)&1023);
 W(0x40020044)=(W(0x40020044)&~127u)|ldo;
 W(0x4002004c)=(W(0x4002004c)&~127u)|vddf;
 event_a_power_ton_adjust(ton,target);
 W(0x4002037c)&=~8u;W(0x4002037c)&=~64u;W(0x4002037c)&=~0x10000u;
 return packed;}
uint32_t opencfw_pcm22_timer_service(void);
extern void event_a_power_ton_adjust(uint32_t,uint32_t);
uint32_t opencfw_spot_pcm22_transition19(uint32_t target,uint32_t current,uint32_t ton,uint32_t old_ton){
 (void)old_ton;uintptr_t p=0x20026ba0,t=p+4+4*target,o=p+4+4*current;
 uint32_t a=B(p+0x64)&127,b=(W(p+0x64)>>7)&127,c=(W(p+0x64)>>14)&127,d=(W(p+0x64)>>21)&127;
 uint32_t packed=a|(b<<8)|(c<<16)|(d<<24);
 uint32_t old_lv=(packed>>(8*(current&3)))&127,new_lv=(packed>>(8*(target&3)))&127;
 (void)B(o);(void)W(o);uint32_t ldo=(W(t)>>21)&127,vddf=B(t)&127;
 if(W(0x400083e0)&1){uint32_t n=0;while(n<60 && !(W(0x40008064)&0x40000000)){opencfw_hal_delay_us(1);n++;}(void)opencfw_pcm22_timer_service();}
 W(0x200270c0)=ton;W(0x200270c4)=target;
 W(0x200270b8)=(W(t)>>7)&1023;W(0x200270bc)=(W(t)>>17)&15;
 W(0x200270b0)=ldo;W(0x200270b4)=vddf;
 int32_t difference=(int32_t)(new_lv-old_lv);
 uint32_t boost=old_lv+(difference>0?(uint32_t)difference*2u:0);
 W(0x40020048)=boost>=128 ? W(0x40020048)|127u : (W(0x40020048)&~127u)|boost;
 opencfw_hal_delay_us(50);W(0x40020048)=(W(0x40020048)&~127u)|new_lv;
 return packed;}
/* Locked f89a4c46 selector7:428920..428a78. Timer/cache publication then TON. */
#include <stdint.h>
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
extern uint32_t opencfw_boot_control_delay_status_change(uint32_t,volatile uint32_t *,uint32_t,uint32_t);
extern void opencfw_pcm22_spot_timer_start(uint32_t);
extern void opencfw_hal_delay_us(uint32_t);
extern uint32_t opencfw_pcm22_timer_service(void);
extern void event_a_power_ton_adjust(uint32_t,uint32_t);
uint32_t opencfw_spot_pcm22_transition7(uint32_t target,uint32_t current,uint32_t ton,uint32_t old_ton){
 (void)old_ton;uintptr_t p=0x20026ba0,t=p+4+4*target,o=p+4+4*current;
 uint32_t old_ldo=(W(o)>>21)&127;
 uint32_t a=B(p+0x64)&127,b=(W(p+0x64)>>7)&127,c=(W(p+0x64)>>14)&127,d=(W(p+0x64)>>21)&127;
 uint32_t packed=a|(b<<8)|(c<<16)|(d<<24);
 (void)B(o);(void)W(o);uint32_t ldo=(W(t)>>21)&127,vddf=B(t)&127;
 if(W(0x400083e0)&1){uint32_t n=0;while(n<60 && !(W(0x40008064)&0x40000000)){opencfw_hal_delay_us(1);n++;}(void)opencfw_pcm22_timer_service();}
 W(0x200270c0)=ton;W(0x200270c4)=target;
 W(0x200270b8)=(W(t)>>7)&1023;W(0x200270bc)=(W(t)>>17)&15;
 W(0x200270b0)=ldo;W(0x200270b4)=vddf;
 event_a_power_ton_adjust(ton,target);
 uint32_t base_vddf=B(p+8)&127;
 uint32_t delta=(uint32_t)((float)(vddf-base_vddf)*0.9f);
 uint32_t boosted=vddf+delta;
 W(0x4002004c)=boosted>=128 ? W(0x4002004c)|127u : (W(0x4002004c)&~127u)|boosted;
 int32_t difference=(int32_t)(ldo-old_ldo);
 boosted=old_ldo+(difference>0?(uint32_t)difference*2u:0);
 W(0x40020044)=boosted>=128 ? W(0x40020044)|127u : (W(0x40020044)&~127u)|boosted;
 W(0x20000154)=target;
 opencfw_pcm22_spot_timer_start(50);B(0x2000055a)=7;
 return delta;}
