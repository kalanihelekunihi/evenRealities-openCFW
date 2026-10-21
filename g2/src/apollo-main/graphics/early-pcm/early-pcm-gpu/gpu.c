#include "gpu.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
extern void stock_delay(uint32_t);
extern uint32_t stock_ton_update(uint32_t,uint32_t);
extern void stock_buck_enable(uint32_t);
extern uint32_t stock_save_irq(void);
extern void stock_temperature_apply(uint32_t);
extern uint32_t stock_stimer_running(void);
static void field(uint32_t a,uint32_t v,uint32_t mask,uint32_t shift) {W(a)=(W(a)&~mask)|((v<<shift)&mask);}
static uint32_t cap(uint32_t v,uint32_t max) {return v>=max+1?max:v;}
static uint32_t buck(void) {return ((W(0x40021108)>>4)&3)==3;}
void pcm_early_switch(uint32_t enable) {
    if((uint8_t)enable) {W(0x40021100)|=1;stock_delay(5);stock_buck_enable(1);}
    else {stock_buck_enable(0);stock_delay(5);W(0x40021100)&=~1u;}
}
uint32_t pcm_early_on(uint32_t state) {
    if((uint8_t)state!=2) (void)stock_ton_update(1,0);
    if(!buck()) {
        W(0x200742b4)=(W(0x40020080)>>10)&15;field(0x40020080,2,0x3c00,10);
        W(0x200742b8)=W(0x40020088)&63;field(0x40020088,cap((W(0x40020088)&63)+5,63),63,0);stock_delay(15);
    } else if(B(0x20074f63)) {
        pcm_early_switch(0);field(0x40020080,1,0x3c00,10);
        field(0x40020044,cap(W(0x2007426c)+9,127),127,0);W(0x400201b0)|=0x100;
        field(0x4002004c,cap(W(0x20074270)+15,127),127,0);W(0x40020374)|=0x60000000;
        pcm_early_switch(1);stock_delay(15);
    }
    return 0;
}
uint32_t pcm_early_off(void) {
    if(!buck()) {field(0x40020088,W(0x200742b8),63,0);field(0x40020080,W(0x200742b4),0x3c00,10);}
    else if(B(0x20074f63)) {
        pcm_early_switch(0);field(0x40020374,W(0x20074274),0x60000000,29);
        field(0x4002004c,W(0x20074270),127,0);W(0x400201b0)&=~0x100u;
        field(0x40020044,W(0x2007426c),127,0);field(0x40020080,W(0x20074278),0x3c00,10);pcm_early_switch(1);
    }
    (void)stock_ton_update(0,0);return 0;
}
void pcm_temperature_publish(uint32_t range) {
    uint32_t irq=stock_save_irq();B(0x20074f74)=(uint8_t)range;
    if(B(0x20074f71)) B(0x20074f72)=1;else stock_temperature_apply((uint8_t)range);
    __asm volatile("msr primask, %0" :: "r"(irq) : "memory");
}
uint32_t pcm_temperature(uint32_t metadata[3]) {
    float temperature=*(float *)metadata;uint32_t range;
    if(temperature<35.0f && temperature>=-273.0f) range=0;
    else if(temperature>=35.0f && temperature<50.0f) range=1;
    else if(temperature>=50.0f && temperature<1000.0f) range=2;
    else {metadata[1]=0;metadata[2]=0;return 1;}
    if(!B(0x20074f67)) B(0x20074f7b)=range==2;
    pcm_temperature_publish(range);
    metadata[1]=range==0?0xc3888000:range==1?0x42040000:0x42400000;
    metadata[2]=range==0?0x420c0000:range==1?0x42480000:0x447a0000;return 0;
}
void pcm_sleep(uint32_t state) {
    (void)state;if(!B(0x20074f67)) return;
    if(B(0x20074f74)==2) {B(0x20074f7b)=1;return;}
    if(stock_stimer_running() && (W(0x40008800)&15)>=1 && (W(0x40008800)&15)<3) {B(0x20074f7b)=1;return;}
    for(uint32_t i=0;i<16;i++) {
        if(!(W(0x40008200+32*i)&1)||!(W(0x40008010)&(1u<<i))) continue;
        uint32_t clk=(W(0x40008200+32*i)>>8)&511;
        if(clk<6||(clk>=19&&clk<25)||(clk>=256&&clk<480)) {B(0x20074f7b)=1;return;}
    }
    B(0x20074f7b)=0;
}
static uint32_t core_boost(void) {
    uint32_t core=W(0x40020080)&1023,boost=core+12>=1024?1023-core:12;
    field(0x40020080,W(0x40020080)+boost,1023,0);field(0x40020088,5,63,0);stock_delay(5);return boost;
}
static void shorts(uint32_t enable) {
    uint32_t bits[4]={0x20000000,0x10000000,0x80000000,0x40000000};
    for(uint32_t i=0;i<4;i++) if(enable) W(0x40020380)|=bits[i];else W(0x40020380)&=~bits[i];
}
static void restore_core(uint32_t boost) {field(0x40020080,W(0x40020080)-boost,1023,0);}
static void restore_memory(void) {field(0x40020088,B(0x20074f6e)?0:1,63,0);}
static void rail_ton(uint32_t c,uint32_t lv,uint32_t f,uint32_t fsleep) {
    field(0x40020344,c,0x3e000000,25);field(0x40020344,c,0xf800,11);
    field(0x4002034c,lv,0x3e000000,25);field(0x4002034c,lv,0xf800,11);
    field(0x40020358,f,0x1f00,8);field(0x40020354,fsleep,0x3e0000,17);
}
uint32_t pcm_middle_on(uint32_t state) {
    if(!buck()) {
        W(0x200742bc)=(W(0x40020080)>>10)&15;field(0x40020080,2,0x3c00,10);
        W(0x200742c4)=W(0x40020088)&63;field(0x40020088,cap((W(0x40020088)&63)+5,63),63,0);stock_delay(15);return 0;
    }
    if(B(0x20074f6f)) {W(0x200742c0)=(W(0x40020080)>>10)&15;field(0x40020080,1,0x3c00,10);}
    uint32_t boost=core_boost();
    if(B(0x20074f6f)) field(0x4002004c,cap((W(0x4002004c)&127)+15,127),127,0);
    shorts(1);stock_delay(10);
    if(B(0x20074f6f)) {field(0x40020044,cap((W(0x40020044)&127)+9,127),127,0);W(0x400201b0)|=0x100;}
    uint32_t low=(uint8_t)state==1;
    if(B(0x20074f6f)) rail_ton(10,8,low?16:20,low?20:22);
    else rail_ton(6,5,low?9:13,low?13:19);
    shorts(0);restore_core(boost);restore_memory();return 0;
}
uint32_t pcm_middle_off(void) {
    if(!buck()) {field(0x40020088,W(0x200742c4),63,0);field(0x40020080,W(0x200742bc),0x3c00,10);return 0;}
    uint32_t boost=core_boost();shorts(1);stock_delay(10);rail_ton(6,5,7,10);
    if(B(0x20074f6f)) {
        uint32_t f=W(0x4002004c)&127,c=W(0x40020044)&127;
        field(0x4002004c,f>=16?f-15:0,127,0);field(0x40020044,c>=10?c-9:0,127,0);
        field(0x40020080,W(0x200742c0),0x3c00,10);W(0x400201b0)&=~0x100u;
    }
    restore_core(boost);restore_memory();shorts(0);return 0;
}
