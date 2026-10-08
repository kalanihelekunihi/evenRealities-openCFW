#include "pending.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
extern uint32_t stock_save_irq(void);
extern void stock_delay(uint32_t);
extern void stock_buck_enable(uint32_t);
static void field(uint32_t a,uint32_t v,uint32_t mask,uint32_t shift) {W(a)=(W(a)&~mask)|((v<<shift)&mask);}
void pcm_hardware_temperature(uint32_t range) {
    if(!B(0x20074f63)||((W(0x40021108)>>4)&3)!=3) return;
    uint32_t boost=(W(0x40021004)&0x40000)&&B(0x20074f6f)?15:0;
    range=(uint8_t)range;uint32_t reduce=range==0||range==1?10:0,value;
    if((int32_t)(reduce-boost)>=1) {
        uint32_t diff=reduce-boost;value=diff<W(0x20074270)?W(0x20074270)-diff:0;
    } else {value=W(0x20074270)+boost-reduce;if(value>=128) value=127;}
    field(0x4002004c,value,127,0);
}
uint32_t pcm_postpone(void) {B(0x20074f71)=1;return 0;}
uint32_t pcm_pending_handle(void) {
    uint32_t irq=stock_save_irq();
    if(B(0x20074f72)) {pcm_hardware_temperature(B(0x20074f74));B(0x20074f72)=0;}
    B(0x20074f71)=0;
    __asm volatile("msr primask, %0" :: "r"(irq) : "memory");return 0;
}
uint32_t pcm_ton_initialize(void) {
    uint32_t major=W(0x4002000c)&255;
    if((major==0x21 && W(0x200001e8)!=0)||major>=0x22) {
        B(0x2000453a)=(W(0x40020344)>>25)&31;B(0x2000453b)=(W(0x40020344)>>11)&31;
        B(0x2000453e)=(W(0x40020358)>>8)&31;B(0x2000453f)=(W(0x40020354)>>17)&31;
        B(0x2000453c)=(W(0x4002034c)>>25)&31;B(0x2000453d)=(W(0x4002034c)>>11)&31;
    } else {B(0x2000453a)=14;B(0x2000453b)=31;B(0x2000453e)=21;B(0x2000453f)=31;B(0x2000453c)=11;B(0x2000453d)=11;}
    return 0;
}
/* Authenticated configuration data at0x789FE0, not executable opcodes. */
static const uint8_t ton_levels[3][3]={{1,1,2},{1,1,2},{1,2,2}};
uint32_t pcm_ton_config_update(uint32_t gpu_on,uint32_t mode) {
    uint32_t enabled=W(0x40021100)&1;
    if(enabled) {stock_buck_enable(0);stock_delay(5);W(0x40021100)&=~1u;}
    uint32_t row=!(uint8_t)gpu_on?0:!(uint8_t)mode?1:2;
    uint32_t cpu_lp=ton_levels[row][1]==1,cpu_hp=ton_levels[row][2]==1;
    W(0x40020340)|=0x80000000;
    field(0x40020344,B(cpu_lp?0x2000453a:0x2000453b),0x3e000000,25);
    field(0x40020344,B(cpu_hp?0x2000453a:0x2000453b),0xf800,11);
    field(0x40020358,B(cpu_lp?0x2000453e:0x2000453f),0x1f00,8);
    field(0x40020354,B(cpu_hp?0x2000453e:0x2000453f),0x3e0000,17);
    field(0x4002034c,B(cpu_lp?0x2000453c:0x2000453d),0x3e000000,25);
    field(0x4002034c,B(cpu_hp?0x2000453c:0x2000453d),0xf800,11);
    if(enabled) {W(0x40021100)|=1;stock_delay(5);stock_buck_enable(1);}
    return 0;
}

uint32_t pcm_lp_switch_initialize(void) {
    W(0x400211a0)&=~0x1f00u;field(0x400211a0,1000,0xffff0000,16);
    (void)W(0x400211a8);W(0x400211a8)=0;
    (void)W(0x400211a4);W(0x400211a4)=800;
    (void)W(0x400211ac);W(0x400211ac)=450;
    (void)W(0x400211b4);W(0x400211b4)=600;
    (void)W(0x400211bc);W(0x400211bc)=250;
    W(0x400211a0)&=~2u;W(0x400211a0)&=~1u;return 0;
}
uint32_t pcm_lp_switch_enable(void) {W(0x400211a0)|=3;B(0x20074f73)=1;return 0;}
uint32_t pcm_lp_switch_disable(void) {
    if(B(0x20074f73)) {W(0x400211a0)&=~3u;B(0x20074f73)=0;}
    return 0;
}

uint32_t pcm_early_before_enable(void) {
    if(B(0x20074f63)) {uint32_t cached=W(0x2007427c);field(0x40020080,cached>=7?cached-6:0,1023,0);}return 0;
}
uint32_t pcm_early_after_enable(void) {field(0x40020088,0,63,0);field(0x400201b0,1,0x18000,15);return 0;}
uint32_t pcm_middle_before_enable(void) {
    if(B(0x20074f63)) {uint32_t cached=W(0x2007427c);field(0x40020080,cached>=8?cached-7:0,1023,0);}return 0;
}
uint32_t pcm_middle_after_enable(void) {field(0x40020088,1,63,0);field(0x400201b0,2,0x18000,15);return 0;}
