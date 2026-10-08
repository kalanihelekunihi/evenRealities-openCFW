/* Locked f89a4c46 selector13:4291ec..42944a. Timer/cache publication then TON. */
#include <stdint.h>
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
extern uint32_t opencfw_boot_control_delay_status_change(uint32_t,volatile uint32_t *,uint32_t,uint32_t);
extern void opencfw_hal_delay_us(uint32_t);
extern uint32_t opencfw_pcm22_timer_service(void);
extern void event_a_power_ton_adjust(uint32_t,uint32_t);
uint32_t opencfw_spot_pcm22_transition13(uint32_t target,uint32_t current,uint32_t ton,uint32_t old_ton){
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
 opencfw_hal_delay_us(50);W(0x40020044)=(W(0x40020044)&~127u)|ldo;
 W(0x40020080)=(W(0x40020080)&~0x3c00u)|(((W(t)>>17)&15)<<10);
 W(0x40020080)=(W(0x40020080)&~1023u)|((W(t)>>7)&1023);
 opencfw_hal_delay_us(5);W(0x4002004c)=(W(0x4002004c)&~127u)|vddf;
 W(0x40021000)=(W(0x40021000)&~3u)|1u;
 uint32_t n=0;while(n<20 && !(W(0x40021000)&4)){opencfw_hal_delay_us(1);n++;}
 W(0x4002037c)|=64;W(0x4002037c)|=8;W(0x4002037c)&=~0x02000000u;
 uint32_t temporary=0;
 if(!(W(0x40004044)&32)){W(0x40004044)|=32;opencfw_hal_delay_us(1);
 (void)opencfw_boot_control_delay_status_change(15,(volatile uint32_t *)0x40004030,0x01000000,0x01000000);temporary=1;}
 if(W(0x40004030)&0x01000000){W(0x40021000)=(W(0x40021000)&~3u)|2u;n=0;while(n<20 && !(W(0x40021000)&4)){opencfw_hal_delay_us(1);n++;}}
 if(temporary)W(0x40004044)&=~32u;
 return delta;
}
