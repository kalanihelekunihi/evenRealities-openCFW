#include "driver.h"
#include "../gpio_providers_offline/clock_requests.h"
#define W(a) (*(volatile uint32_t *)(a))
extern uint32_t stock_pll_power_enable(void),stock_pll_power_disable(void),stock_pll_power_enabled(uint8_t *);
extern uint32_t stock_wait5(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
static uint32_t valid(uint32_t h){return h&&(W(h)&~0xfe000000u)==0x01504c30;}
uint32_t audio_pll_init(uint32_t module,uint32_t *out){
 if(module)return 5;if(!out)return 6;if(W(0x200740f4)&0x01000000)return 7;
 W(0x200740f4)|=0x01000000;W(0x200740f4)=(W(0x200740f4)&0xff000000)|0x00504c30;W(0x200740f8)=module;stock_pll_power_enable();*out=0x200740f4;return 0;
}
uint32_t audio_pll_enable(uint32_t h){if(!valid(h))return 2;if(W(h)&0x02000000)return 0;if((W(0x40020060)&0xf0000)!=0xf0000)return 7;W(0x400204d8)|=0x20000000;W(h)|=0x02000000;return 0;}
uint32_t audio_pll_disable(uint32_t h){if(!valid(h))return 2;W(0x400204d8)&=~0x20000000u;W(h)&=~0x02000000u;return 0;}
uint32_t audio_pll_deinit(uint32_t h){
 if(!valid(h))return 2;uint32_t status=0;uint8_t powered=0;if(W(h)&0x02000000)status=audio_pll_disable(h);stock_pll_power_enabled(&powered);if(powered)stock_pll_power_disable();W(h)&=~0x01000000u;return status;
}
uint32_t audio_pll_configure(uint32_t h,const audio_pll_config *c){
 if(!valid(h))return 2;if(W(h)&0x02000000)return 7;
 if(c->refdiv>=64)return 6;
 if(c->mode==1){if((uint32_t)c->fbdiv-4>=957)return 6;}else if((uint32_t)c->fbdiv-10>=87)return 6;
 if(c->postdiv1>=8||c->postdiv2>=8||c->postdiv1<c->postdiv2)return 6;
 W(0x400204d8)=(W(0x400204d8)&~512u)|((c->vco&1u)<<9);
 W(0x400204d8)=(W(0x400204d8)&~32u)|((c->reference&1u)<<5);
 W(0x400204d8)=(W(0x400204d8)&~8u)|((c->mode&1u)<<3);
 W(0x400204dc)=(W(0x400204dc)&0xff000000)|(c->fraction&0xffffff);
 W(0x400204e0)=(W(0x400204e0)&~0x0fff0000u)|((c->fbdiv&4095u)<<16);
 W(0x400204e0)=(W(0x400204e0)&~63u)|(c->refdiv&63u);
 W(0x400204e0)=(W(0x400204e0)&~0x7000u)|((c->postdiv1&7u)<<12);
 W(0x400204e0)=(W(0x400204e0)&~0x700u)|((c->postdiv2&7u)<<8);
 audio_clock_reference_update(c->reference);
 W(0x400204d8)&=~16u;W(0x400204d8)|=1;W(0x400204d8)&=~2u;W(0x400204d8)&=~4u;return 0;
}
uint32_t audio_pll_wait(uint32_t h){if(!valid(h))return 2;uint32_t vco=(W(0x400204d8)>>9)&1,div=W(0x400204e0)&63;if(!(W(0x400204d8)&0x20000000))return 7;uint32_t us=((vco?1875u:1000u)*div+11)/12;return stock_wait5(us,0x400204e4,1,1,1);}
