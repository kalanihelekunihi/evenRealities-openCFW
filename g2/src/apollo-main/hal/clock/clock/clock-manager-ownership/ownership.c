#include "ownership.h"
#define W(a) (*(volatile uint32_t *)(a))
#define B(a) (*(volatile uint8_t *)(a))
static volatile uint32_t *row(uint32_t c){return (volatile uint32_t *)(0x20073324u+8u*(uint8_t)c);}
uint32_t audio_clock_any(uint32_t c){for(unsigned i=0;i<2;i++)if(row(c)[i])return 1;return 0;}
uint32_t audio_clock_user(uint32_t c,uint32_t u){return (row(c)[(uint8_t)u>>5]>>(u&31))&1;}
uint32_t audio_clock_count(uint32_t c){unsigned n=0;for(unsigned i=0;i<2;i++){uint32_t v=row(c)[i];while(v){n+=v&1;v>>=1;}}return (uint8_t)n;}
uint32_t audio_clock_set(uint32_t c,uint32_t u,uint32_t yes){
 if((uint8_t)c>=7||(uint8_t)u>=57)return 6;
 volatile uint32_t *p=row(c)+((uint8_t)u>>5);uint32_t bit=1u<<(u&31);
 if((uint8_t)yes)*p|=bit;else *p&=~bit;return 0;
}
uint32_t audio_xtal_status(uint8_t *s){if(W(0x4002012c)&256)*s=2;else if(W(0x4002012c)&1)*s=1;else *s=0;return 0;}
extern uint32_t stock_save_irq(void);
extern uint32_t stock_oscillator(uint32_t,const void *);
uint32_t audio_xtal_release(uint32_t u){
 if(!audio_clock_user(2,(uint8_t)u))return 0;
 uint32_t mask=stock_save_irq();audio_clock_set(2,(uint8_t)u,0);
 if(!audio_clock_any(2)){uint8_t yes=1;stock_oscillator(4,&yes);B(0x20074f56)=0;W(0x20074260)=0;}
 __asm volatile("msr primask, %0"::"r"(mask):"memory");return 0;
}
