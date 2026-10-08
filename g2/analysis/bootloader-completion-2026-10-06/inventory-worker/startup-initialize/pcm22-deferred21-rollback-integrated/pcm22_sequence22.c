/* Locked f89a4c46 selector22:429e00..429f68. Used by failed HP rollback. */
#include <stdint.h>
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
extern void opencfw_hal_delay_us(uint32_t);
extern uint32_t opencfw_pcm22_timer_service(void);
extern void event_a_power_ton_adjust(uint32_t,uint32_t);
uint32_t opencfw_spot_pcm22_transition22(uint32_t target,uint32_t current,uint32_t ton,uint32_t old_ton){
 (void)old_ton;uintptr_t p=0x20026ba0,t=p+4+4*target,o=p+4+4*current;
 uint32_t a=B(p+0x64)&127,b=(W(p+0x64)>>7)&127,c=(W(p+0x64)>>14)&127,d=(W(p+0x64)>>21)&127;
 uint32_t packed=a|(b<<8)|(c<<16)|(d<<24);
 (void)B(o);uint32_t old_ldo=(W(o)>>21)&127,ldo=(W(t)>>21)&127,vddf=B(t)&127;
 if(W(0x400083e0)&1){uint32_t n=0;while(n<60 && !(W(0x40008064)&0x40000000)){opencfw_hal_delay_us(1);n++;}(void)opencfw_pcm22_timer_service();}
 W(0x200270c0)=ton;W(0x200270c4)=target;
 W(0x200270b8)=(W(t)>>7)&1023;W(0x200270bc)=(W(t)>>17)&15;
 W(0x200270b0)=ldo;W(0x200270b4)=vddf;
 int32_t delta=(int32_t)(ldo-old_ldo);uint32_t boost=old_ldo+(delta>0?(uint32_t)delta*2u:0);
 if(boost>=128)W(0x40020044)=W(0x40020044)|127;
 else W(0x40020044)=(W(0x40020044)&~127u)|boost;
 opencfw_hal_delay_us(50);W(0x40020044)=(W(0x40020044)&~127u)|ldo;
 uint32_t temp=(W(t)>>17)&15;W(0x40020080)=(W(0x40020080)&~0x3c00u)|(temp<<10);
 uint32_t core=(W(t)>>7)&1023;W(0x40020080)=(W(0x40020080)&~1023u)|core;
 opencfw_hal_delay_us(5);
 W(0x4002037c)=W(0x4002037c)&~0x10000u;W(0x4002037c)=W(0x4002037c)&~0x02000000u;
 W(0x4002004c)=(W(0x4002004c)&~127u)|vddf;
 event_a_power_ton_adjust(ton,target);return packed;
}
