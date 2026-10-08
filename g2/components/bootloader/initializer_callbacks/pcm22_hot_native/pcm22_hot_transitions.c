/* Stock instruction reconstructions, not SDK replacement bodies.
 * 11:428e6a..4290a2;12:4290a2..4291e0;21:429c46..429d9e.
 * Raw R0 is a private test ABI: walker discards callback results. */
#include <stdint.h>
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern void opencfw_hal_delay_us(uint32_t);
extern uint32_t opencfw_pcm22_timer_service(void);
extern void event_a_power_ton_adjust(uint32_t,uint32_t);
extern uint32_t opencfw_boot_control_delay_status_change(uint32_t,volatile uint32_t *,uint32_t,uint32_t);
extern uint32_t opencfw_pcm22_icache_disable(void);
extern uint32_t opencfw_boot_icache_enable(void);
typedef struct {uintptr_t word;uint32_t packed,old_vddf,ldo,vddf;} profile;
static inline profile read_profile(uint32_t target,uint32_t current){
 uintptr_t p=0x20026ba0,q=p+4+current*4;profile r;
 r.word=p+4+target*4;
 uint32_t a=B(p+0x64)&127,b=(W(p+0x64)>>7)&127,c=(W(p+0x64)>>14)&127,d=(W(p+0x64)>>21)&127;
 r.packed=a|(b<<8)|(c<<16)|(d<<24);
 r.old_vddf=B(q)&127;(void)W(q);
 r.ldo=(W(r.word)>>21)&127;r.vddf=B(r.word)&127;return r;
}
static inline void timer_and_globals(profile r,uint32_t target,uint32_t ton){
 if(W(0x400083e0)&1){uint32_t n=0;while(n<60 && !(W(0x40008064)&0x40000000)){opencfw_hal_delay_us(1);n++;}(void)opencfw_pcm22_timer_service();}
 W(0x200270c0)=ton;W(0x200270c4)=target;
 W(0x200270b8)=(W(r.word)>>7)&1023;W(0x200270bc)=(W(r.word)>>17)&15;
 W(0x200270b0)=r.ldo;W(0x200270b4)=r.vddf;
}
static inline void core_ldo(profile r){
 uint32_t t=(W(r.word)>>17)&15;
 W(0x40020080)=(W(0x40020080)&~0x3c00u)|(t<<10);
 t=(W(r.word)>>7)&1023;W(0x40020080)=(W(0x40020080)&~1023u)|t;
}
static inline void vddf_boost(profile r){
 int32_t delta=(int32_t)(r.vddf-r.old_vddf);
 uint32_t value=r.old_vddf+(delta>0?(uint32_t)delta*2u:0);
 if(value>=128)W(0x4002004c)=W(0x4002004c)|127u;
 else W(0x4002004c)=(W(0x4002004c)&~127u)|value;
}
uint32_t opencfw_spot_pcm22_transition11(uint32_t target,uint32_t current,uint32_t ton,uint32_t old_ton){
 (void)old_ton;profile r=read_profile(target,current);timer_and_globals(r,target,ton);
 W(0x40021000)=(W(0x40021000)&~3u)|1u;
 uint32_t n=0;while(n<20 && !(W(0x40021000)&4)){opencfw_hal_delay_us(1);n++;}
 /* 11 clears AOR before CPU; selector5 uses the reverse order. */
 W(0x4002037c)=W(0x4002037c)&~64u;W(0x4002037c)=W(0x4002037c)&~8u;
 W(0x4002037c)=W(0x4002037c)|0x02000000u;
 uint32_t temporary=0;
 if(!(W(0x40004044)&32)){
  W(0x40004044)=W(0x40004044)|32u;opencfw_hal_delay_us(1);
  (void)opencfw_boot_control_delay_status_change(15,(volatile uint32_t *)0x40004030,0x01000000,0x01000000);temporary=1;
 }
 if(W(0x40004030)&0x01000000){
  W(0x40021000)=(W(0x40021000)&~3u)|2u;
  n=0;while(n<20 && !(W(0x40021000)&4)){opencfw_hal_delay_us(1);n++;}
 }
 if(temporary)W(0x40004044)=W(0x40004044)&~32u;
 core_ldo(r);W(0x40020044)=(W(0x40020044)&~127u)|r.ldo;
 vddf_boost(r);opencfw_hal_delay_us(50);W(0x4002004c)=(W(0x4002004c)&~127u)|r.vddf;
 (void)event_a_power_ton_adjust(ton,target);return (uint32_t)r.word;
}
uint32_t opencfw_spot_pcm22_transition12(uint32_t target,uint32_t current,uint32_t ton,uint32_t old_ton){
 (void)old_ton;profile r=read_profile(target,current);timer_and_globals(r,target,ton);
 /* No TON adjustment in the locked selector12, despite SDK counterpart. */
 vddf_boost(r);core_ldo(r);opencfw_hal_delay_us(50);
 W(0x4002004c)=(W(0x4002004c)&~127u)|r.vddf;return r.packed;
}
uint32_t opencfw_spot_pcm22_transition21(uint32_t target,uint32_t current,uint32_t ton,uint32_t old_ton){
 (void)old_ton;profile r=read_profile(target,current);timer_and_globals(r,target,ton);
 B(0x200271bc)=1;(void)event_a_power_ton_adjust(ton,target);
 vddf_boost(r);opencfw_hal_delay_us(50);W(0x4002004c)=(W(0x4002004c)&~127u)|r.vddf;
 uint32_t enabled=W(0xe000ed14)&0x20000;
 if(enabled)opencfw_pcm22_icache_disable();
 W(0x4002037c)=W(0x4002037c)|0x10000;W(0x4002037c)=W(0x4002037c)|0x02000000;
 opencfw_hal_delay_us(20);if(enabled)(void)opencfw_boot_icache_enable();return r.packed;
}
