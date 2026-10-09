#include "providers.h"
#include "../clock_manager_ownership_offline/ownership.h"
#include "../gpio_providers_offline/gpio.h"
#define W(a) (*(volatile uint32_t *)(a))
extern uint32_t stock_save_irq(void),stock_wait5(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern void stock_delay(uint32_t);
static void restore(uint32_t m){__asm volatile("msr primask, %0"::"r"(m):"memory");}
uint32_t audio_ext_request(uint32_t u){u=(uint8_t)u;if(!W(0x200001dc))return 7;if(audio_clock_user(3,u))return 0;uint32_t m=stock_save_irq();audio_gpio_pin_set(15,10);audio_clock_set(3,u,1);restore(m);return 0;}
uint32_t audio_ext_release(uint32_t u){u=(uint8_t)u;if(!audio_clock_user(3,u))return 0;uint32_t m=stock_save_irq();audio_clock_set(3,u,0);if(!audio_clock_any(3))audio_gpio_pin_set(15,3);restore(m);return 0;}
uint32_t audio_pll_power_enable(void){uint32_t m=stock_save_irq();if((W(0x4002000c)&255)>=0x22){W(0x400201b0)&=~0x200000u;stock_delay(1);}W(0x400204d8)&=~0x80000000u;W(0x400204d8)&=~0x40000000u;restore(m);stock_delay(5);return 0;}
uint32_t audio_pll_power_disable(void){uint32_t m=stock_save_irq();W(0x400204d8)|=0x80000000;W(0x400204d8)|=0x40000000;if((W(0x4002000c)&255)>=0x22){stock_delay(1);W(0x400201b0)|=0x200000;}restore(m);return 0;}
uint32_t audio_pll_power_enabled(uint8_t *out){*out=(W(0x400204d8)>>31)^1;return 0;}
uint32_t audio_hfrc_force(uint32_t on){W(0x40004044)=(W(0x40004044)&~1u)|((uint8_t)on!=0);return 0;}
uint32_t audio_hfrc_apply(uint32_t cfg){W(0x40004020)=cfg|1;return 0;}
uint32_t audio_hfrc_disable(void){W(0x40004020)&=~1u;return 0;}
uint32_t audio_hfrc2_force(uint32_t on){if((uint8_t)on){if(!(W(0x40004044)&32)){W(0x40004044)|=32;return stock_wait5(100,0x40004030,0x1000000,0x1000000,1);}}else W(0x40004044)&=~32u;return 0;}
uint32_t audio_hfrc2_apply(const void *cfg){if(!cfg)return 6;const uint8_t *b=cfg;const uint32_t *w=cfg;W(0x4000404c)|=7;W(0x40004048)=(W(0x40004048)&~0x20000000u)|((b[0]&1u)<<29);W(0x40004050)=(W(0x40004050)&~3u)|(b[1]&3u);W(0x40004050)=(W(0x40004050)&~0x7ffffffcu)|((w[1]&0x1fffffffu)<<2);W(0x40004048)|=1;return 0;}
uint32_t audio_hfrc2_disable(void){W(0x40004048)&=~1u;return 0;}
uint32_t audio_hfrc2_ratio(uint32_t reference,uint32_t target,uint32_t div,uint32_t *out){
 uint32_t denominator=(uint8_t)div<32?1u<<(uint8_t)div:0;uint32_t effective=denominator?reference/denominator:0;
 float ratio=(float)target/(float)effective;
 /* Fixed-point VFP conversion preserves the stock rounding/saturation and FPSCR effects. */
 __asm volatile("vcvt.u32.f32 %0, %0, #15":"+t"(ratio));
 union {float f;uint32_t u;} converted={.f=ratio};*out=converted.u;return 0;
}
uint32_t audio_hfrc_target(uint32_t reference,uint32_t target,uint32_t *out){*out=reference?target/reference:0;return 0;}
