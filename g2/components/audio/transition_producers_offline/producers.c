#include "producers.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
extern void stock_delay_us(uint32_t);
extern void stock_timer_start(uint32_t);
extern void stock_ton_adjust(uint32_t,uint32_t);
extern void pcm22_boost_completion(void);
static void field(uint32_t a,uint32_t value,unsigned shift,unsigned bits) {
    uint32_t mask=((1u<<bits)-1u)<<shift;
    W(a)=(W(a)&~mask)|((value<<shift)&mask);
}
static void barrier(void) { __asm volatile("dsb sy\nisb sy" ::: "memory"); }
uint32_t pcm22_icache_enable(void) {
    if(W(0xe001e300)&0x300) return 1;
    if(!(W(0xe000ed14)&0x20000)) {
        barrier();W(0xe000ef50)=0;barrier();W(0xe000ed14)|=0x20000;barrier();
    }
    return 0;
}
uint32_t pcm22_icache_disable(void) {
    if(W(0xe001e300)&0x300) return 1;
    barrier();W(0xe000ed14)&=~0x20000u;W(0xe000ef50)=0;barrier();return 0;
}
static void finish_previous(void) {
    if(W(0x400083e0)&1) {
        for(unsigned i=0;i<60 && !(W(0x40008064)&0x40000000u);i++) stock_delay_us(1);
        pcm22_boost_completion();
    }
}
static void publish(uint32_t next,uint32_t ton,uint32_t nc,uint32_t nf) {
    W(0x200742e4)=ton;W(0x200742e8)=next;
    W(0x200742dc)=(W(0x20056660+next*4u)>>7)&1023;
    W(0x200742e0)=(W(0x20056660+next*4u)>>17)&15;
    W(0x200742d4)=nc;W(0x200742d8)=nf;
}
static uint32_t doubled_boost(uint32_t next,uint32_t old) {
    int32_t diff=(int32_t)next-(int32_t)old;
    uint32_t value=old+(diff>0?(uint32_t)diff*2u:0u);
    return value>=128?127:value;
}
void pcm22_sequence_7(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton) {
    (void)old_ton;
    uint32_t n=W(0x20056660+next*4u),o=W(0x20056660+old*4u);
    uint32_t nc=(n>>21)&127,oc=(o>>21)&127,nf=n&127;
    finish_previous();publish(next,ton,nc,nf);stock_ton_adjust(ton,next);
    /* Stock difference is unsigned, with single-precision factor0x3F666666. */
    uint32_t base=W(0x20056664)&127;
    uint32_t margin=(uint32_t)((float)(nf-base)*0.9f);
    uint32_t boost=nf+margin;
    field(0x4002004c,boost>=128?127:boost,0,7);
    field(0x40020044,doubled_boost(nc,oc),0,7);
    W(0x200002a4)=next;stock_timer_start(50);B(0x20004540)=7;
}
void pcm22_sequence_21(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton) {
    (void)old_ton;
    uint32_t n=W(0x20056660+next*4u),o=W(0x20056660+old*4u);
    uint32_t nc=(n>>21)&127,nf=n&127,of=o&127;
    finish_previous();publish(next,ton,nc,nf);B(0x20074f77)=1;stock_ton_adjust(ton,next);
    field(0x4002004c,doubled_boost(nf,of),0,7);stock_delay_us(50);
    field(0x4002004c,nf,0,7);
    unsigned restore=(W(0xe000ed14)&0x20000u)!=0;
    if(restore) (void)pcm22_icache_disable();
    W(0x4002037c)|=0x10000;W(0x4002037c)|=0x2000000;
    stock_delay_us(20);
    if(restore) (void)pcm22_icache_enable();
}

static uint32_t setup_profile(uint32_t next,uint32_t ton) {
    uint32_t n=W(0x20056660+next*4u),nc=(n>>21)&127,nf=n&127;
    finish_previous();publish(next,ton,nc,nf);return nf;
}
void pcm22_sequence_8(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton) {
    (void)old;(void)old_ton;(void)setup_profile(next,ton);stock_ton_adjust(ton,next);
}
void pcm22_sequence_9(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton) {
    (void)old;(void)old_ton;uint32_t nf=setup_profile(next,ton);
    field(0x4002004c,nf,0,7);stock_ton_adjust(ton,next);
}
void pcm22_sequence_20(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton) {
    (void)old;(void)old_ton;(void)setup_profile(next,ton);
    field(0x40020080,(W(0x20056660+next*4u)>>17)&15,10,4);
    field(0x40020080,(W(0x20056660+next*4u)>>7)&1023,0,10);stock_delay_us(5);
}

static uint32_t low_voltage_trim(uint32_t state) {
    return (W(0x200566c0)>>((state&3u)*7u))&127;
}
static void load_core(uint32_t next) {
    field(0x40020080,(W(0x20056660+next*4u)>>17)&15,10,4);
    field(0x40020080,(W(0x20056660+next*4u)>>7)&1023,0,10);
}
void pcm22_sequence_10(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton) {
    pcm22_sequence_8(next,old,ton,old_ton);
}
void pcm22_sequence_12(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton) {
    (void)old_ton;uint32_t nf=W(0x20056660+next*4u)&127,of=W(0x20056660+old*4u)&127;
    (void)setup_profile(next,ton);field(0x4002004c,doubled_boost(nf,of),0,7);
    load_core(next);stock_delay_us(50);field(0x4002004c,nf,0,7);
}
void pcm22_sequence_14(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton) {
    (void)old;(void)old_ton;uint32_t nf=setup_profile(next,ton);field(0x4002004c,nf,0,7);
}
void pcm22_sequence_15(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton) {
    (void)old;(void)old_ton;uint32_t lv=low_voltage_trim(next),nc=(W(0x20056660+next*4u)>>21)&127;
    (void)setup_profile(next,ton);field(0x40020048,lv,0,7);load_core(next);field(0x40020044,nc,0,7);
}
void pcm22_sequence_16(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton) {
    (void)old;(void)old_ton;uint32_t lv=low_voltage_trim(next);
    (void)setup_profile(next,ton);field(0x40020048,lv,0,7);
}
void pcm22_sequence_17(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton) {
    (void)old_ton;uint32_t lv=low_voltage_trim(next),previous=low_voltage_trim(old);
    (void)setup_profile(next,ton);field(0x40020048,doubled_boost(lv,previous),0,7);
    load_core(next);field(0x40020048,lv,0,7); /* No stock50us delay in this body. */
}
void pcm22_sequence_19(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton) {
    (void)old_ton;uint32_t lv=low_voltage_trim(next),previous=low_voltage_trim(old);
    (void)setup_profile(next,ton);field(0x40020048,doubled_boost(lv,previous),0,7);
    stock_delay_us(50);field(0x40020048,lv,0,7);
}

extern void pcm22_timer_stop(void);
extern uint32_t stock_delay_status(uint32_t,uint32_t,uint32_t,uint32_t);
static void switch_low(void) {
    field(0x40021000,1,0,2);
    for(unsigned i=0;i<20 && !(W(0x40021000)&4);i++) stock_delay_us(1);
}
static void switch_high(void) {
    unsigned temporary=!(W(0x40004044)&0x20u);
    if(temporary) {
        W(0x40004044)|=0x20;stock_delay_us(1);
        (void)stock_delay_status(15,0x40004030,0x1000000,0x1000000);
    }
    if(W(0x40004030)&0x1000000) {
        field(0x40021000,2,0,2);
        for(unsigned i=0;i<20 && !(W(0x40021000)&4);i++) stock_delay_us(1);
    }
    if(temporary) W(0x40004044)&=~0x20u;
}
static unsigned disable_cache_if_enabled(void) {
    unsigned enabled=(W(0xe000ed14)&0x20000u)!=0;
    if(enabled) (void)pcm22_icache_disable();return enabled;
}
static void restore_cache(unsigned enabled) { if(enabled) (void)pcm22_icache_enable(); }
void pcm22_sequence_0(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton) {
    (void)old_ton;
    uint32_t n=W(0x20056660+next*4u),nf=n&127,nc=(n>>21)&127,of=W(0x20056660+old*4u)&127;
    if((W(0x400083e0)&1) && next==W(0x200002a4)) {
        stock_ton_adjust(ton,next);field(0x40020044,nc,0,7);
        pcm22_timer_stop();B(0x20004540)=26;return;
    }
    finish_previous();publish(next,ton,nc,nf);stock_ton_adjust(ton,next);
    field(0x4002004c,doubled_boost(nf,of),0,7);stock_delay_us(50);field(0x4002004c,nf,0,7);
    unsigned restore=disable_cache_if_enabled();
    W(0x4002037c)|=0x10000;W(0x4002037c)|=0x2000000;stock_delay_us(20);restore_cache(restore);
    load_core(next);field(0x40020044,nc,0,7);
}
void pcm22_sequence_1(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton) {
    (void)old_ton;uint32_t n=W(0x20056660+next*4u),o=W(0x20056660+old*4u);
    uint32_t nf=n&127,of=o&127,nc=(n>>21)&127,oc=(o>>21)&127;
    finish_previous();publish(next,ton,nc,nf);stock_ton_adjust(ton,next);
    field(0x4002004c,doubled_boost(nf,of),0,7);field(0x40020044,doubled_boost(nc,oc),0,7);
    stock_delay_us(50);field(0x40020044,nc,0,7);load_core(next);stock_delay_us(5);field(0x4002004c,nf,0,7);
    unsigned restore=disable_cache_if_enabled();W(0x4002037c)|=0x10000;W(0x4002037c)|=8;W(0x4002037c)|=0x40;
    stock_delay_us(20);restore_cache(restore);
}
void pcm22_sequence_3(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton) {
    (void)old_ton;uint32_t nf=W(0x20056660+next*4u)&127,of=W(0x20056660+old*4u)&127;
    (void)setup_profile(next,ton);stock_ton_adjust(ton,next);
    field(0x4002004c,doubled_boost(nf,of),0,7);stock_delay_us(50);field(0x4002004c,nf,0,7);
}
void pcm22_sequence_4(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton) {
    (void)old;(void)old_ton;uint32_t nc=(W(0x20056660+next*4u)>>21)&127,nf=setup_profile(next,ton);
    load_core(next);field(0x40020044,nc,0,7);field(0x4002004c,nf,0,7);stock_ton_adjust(ton,next);
    W(0x4002037c)&=~8u;W(0x4002037c)&=~0x40u;W(0x4002037c)&=~0x10000u;
}
void pcm22_sequence_5(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton) {
    (void)old;(void)old_ton;uint32_t nc=(W(0x20056660+next*4u)>>21)&127;
    (void)setup_profile(next,ton);stock_ton_adjust(ton,next);switch_low();
    W(0x4002037c)&=~8u;W(0x4002037c)&=~0x40u;W(0x4002037c)|=0x2000000;
    switch_high();load_core(next);field(0x40020044,nc,0,7);
}
void pcm22_sequence_6(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton) {
    pcm22_sequence_9(next,old,ton,old_ton);
}
void pcm22_sequence_11(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton) {
    (void)old_ton;uint32_t n=W(0x20056660+next*4u),of=W(0x20056660+old*4u)&127,nf=n&127,nc=(n>>21)&127;
    (void)setup_profile(next,ton);switch_low();
    W(0x4002037c)&=~0x40u;W(0x4002037c)&=~8u;W(0x4002037c)|=0x2000000;
    switch_high();load_core(next);field(0x40020044,nc,0,7);
    field(0x4002004c,doubled_boost(nf,of),0,7);stock_delay_us(50);field(0x4002004c,nf,0,7);
    stock_ton_adjust(ton,next);
}
void pcm22_sequence_13(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton) {
    (void)old_ton;uint32_t n=W(0x20056660+next*4u),o=W(0x20056660+old*4u);
    uint32_t nf=n&127,nc=(n>>21)&127,oc=(o>>21)&127;
    finish_previous();publish(next,ton,nc,nf);stock_ton_adjust(ton,next);
    uint32_t base=W(0x20056664)&127,margin=(uint32_t)((float)(nf-base)*0.9f),boost=nf+margin;
    field(0x4002004c,boost>=128?127:boost,0,7);field(0x40020044,doubled_boost(nc,oc),0,7);
    stock_delay_us(50);field(0x40020044,nc,0,7);load_core(next);stock_delay_us(5);field(0x4002004c,nf,0,7);
    switch_low();W(0x4002037c)|=0x40;W(0x4002037c)|=8;W(0x4002037c)&=~0x2000000u;switch_high();
}
void pcm22_sequence_18(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton) {
    (void)old_ton;uint32_t n=W(0x20056660+next*4u),o=W(0x20056660+old*4u);
    uint32_t nf=n&127,nc=(n>>21)&127,oc=(o>>21)&127,lv=low_voltage_trim(next),previous=low_voltage_trim(old);
    finish_previous();publish(next,ton,nc,nf);
    field(0x40020048,doubled_boost(lv,previous),0,7);
    uint32_t base=W(0x20056660)&127,boost=(base-nf)*2u+nf;
    field(0x4002004c,boost>=128?127:boost,0,7);field(0x40020044,doubled_boost(nc,oc),0,7);
    stock_delay_us(50);field(0x40020044,nc,0,7);load_core(next);stock_delay_us(5);
    field(0x4002004c,nf,0,7);field(0x40020048,lv,0,7);
}
void pcm22_sequence_22(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton) {
    (void)old_ton;uint32_t n=W(0x20056660+next*4u),o=W(0x20056660+old*4u);
    uint32_t nc=(n>>21)&127,oc=(o>>21)&127,nf=n&127;
    finish_previous();publish(next,ton,nc,nf);field(0x40020044,doubled_boost(nc,oc),0,7);
    stock_delay_us(50);field(0x40020044,nc,0,7);load_core(next);stock_delay_us(5);
    W(0x4002037c)&=~0x10000u;W(0x4002037c)&=~0x2000000u;field(0x4002004c,nf,0,7);stock_ton_adjust(ton,next);
}
void pcm22_sequence_23(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton) {
    pcm22_sequence_8(next,old,ton,old_ton);
}
void pcm22_sequence_24(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton) { (void)next;(void)old;(void)ton;(void)old_ton; }
void pcm22_sequence_25(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton) { (void)next;(void)old;(void)ton;(void)old_ton; }
void pcm22_sequence_26(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton) { (void)next;(void)old;(void)ton;(void)old_ton; }

void pcm22_registered_timer_service(void) {
    uintptr_t target=W(0x2007329c);
    if(target) ((void (*)(void))target)();
}
void pcm22_timer15_vector_handler(void) { pcm22_registered_timer_service(); }
uint32_t pcm22_registered_post_low_to_high(void) {
    uintptr_t target=W(0x20073298);
    return target?((uint32_t (*)(void))target)():0;
}
void pcm22_ton_adjust(uint32_t ton,uint32_t profile) {
    uint32_t a,b;
    if(profile==8) ton=7;
    switch(ton) {
    case 0: a=W(0x200566b8)&31;b=(W(0x200566b8)>>10)&31;break;
    case 1: a=(W(0x200566b8)>>5)&31;b=(W(0x200566b8)>>15)&31;break;
    case 2: a=W(0x200566b0)&31;b=W(0x200566b4)&31;break;
    case 3: a=(W(0x200566b0)>>10)&31;b=(W(0x200566b4)>>10)&31;break;
    case 4: a=(W(0x200566b0)>>5)&31;b=(W(0x200566b4)>>5)&31;break;
    case 6: a=W(0x200566bc)&31;b=(W(0x200566bc)>>10)&31;break;
    case 7: a=(W(0x40020344)>>11)&31;b=(W(0x40020354)>>17)&31;break;
    default:a=(W(0x200566b0)>>15)&31;b=(W(0x200566b4)>>15)&31;break;
    }
    field(0x40020344,a,25,5);field(0x40020358,b,8,5);
}
