#include "transition.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
extern void stock_delay_us(uint32_t);
extern void stock_timer_start(uint32_t);
extern uint32_t stock_clock_release(uint32_t,uint32_t);
extern void stock_ton_adjust(uint32_t,uint32_t);
extern uint32_t stock_delay_status(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t stock_save_irq(void);
static void field(uint32_t a,uint32_t value,unsigned shift,unsigned bits) {
    uint32_t mask=((1u<<bits)-1u)<<shift;
    W(a)=(W(a)&~mask)|((value<<shift)&mask);
}
void pcm22_timer_stop(void) {
    W(0x400083e0)&=~1u;W(0x40008010)&=~0x8000u;
    (void)stock_clock_release(4,49);
    W(0xe000e188)=0x40000u;W(0x40008068)=0xc0000000u;
    (void)W(0x47ff0000);W(0xe000e288)=0x40000u;
}
static void load_pending_trims(void) {
    field(0x40020044,W(0x200742d4),0,7);
    field(0x40020080,W(0x200742e0),10,4);
    field(0x40020080,W(0x200742dc),0,10);
    stock_delay_us(5);
}
void pcm22_sequence_2_complete(void) {
    load_pending_trims();
    W(0x4002037c)&=~0x10000u;W(0x4002037c)&=~0x2000000u;
    field(0x4002004c,W(0x200742d8),0,7);B(0x20004540)=26;
}
void pcm22_sequence_7_complete(void) {
    load_pending_trims();field(0x4002004c,W(0x200742d8),0,7);
    unsigned restore=(W(0x40021000)&3u)==2;
    if(restore) {
        field(0x40021000,1,0,2);
        for(unsigned i=0;i<20 && !(W(0x40021000)&4);i++) stock_delay_us(1);
    }
    W(0x4002037c)|=0x40;W(0x4002037c)|=8;W(0x4002037c)&=~0x2000000u;
    if(restore) {
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
    B(0x20004540)=26;
}
void pcm22_boost_completion(void) {
    uint32_t irq=stock_save_irq();
    if(B(0x20004540)==2) pcm22_sequence_2_complete();
    else if(B(0x20004540)==7) pcm22_sequence_7_complete();
    pcm22_timer_stop();
    __asm volatile("msr primask, %0" :: "r"(irq) : "memory");
}
void pcm22_sequence_2(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton) {
    (void)old_ton;
    /* Original loads trim fields before optionally completing prior work. */
    uint32_t n=W(0x20056660+next*4u),o=W(0x20056660+old*4u);
    uint32_t nc=(n>>21)&127,oc=(o>>21)&127,nf=n&127;
    if(W(0x400083e0)&1) {
        for(unsigned i=0;i<60 && !(W(0x40008064)&0x40000000u);i++) stock_delay_us(1);
        pcm22_boost_completion();
    }
    W(0x200742e4)=ton;W(0x200742e8)=next;
    W(0x200742dc)=(W(0x20056660+next*4u)>>7)&1023;
    W(0x200742e0)=(W(0x20056660+next*4u)>>17)&15;
    W(0x200742d4)=nc;W(0x200742d8)=nf;
    stock_ton_adjust(ton,next);
    field(0x4002004c,W(0x200566ac),0,7);
    int32_t diff=(int32_t)nc-(int32_t)oc;
    uint32_t boost=oc+(diff>0?(uint32_t)diff*2u:0u);
    if(boost>=128) W(0x40020044)|=127;
    else field(0x40020044,boost,0,7);
    W(0x200002a4)=next;stock_timer_start(50);B(0x20004540)=2;
}

void pcm22_sequence_21_complete(void) {
    field(0x40020080,W(0x20056660+W(0x200002a0)*4u)>>17,10,4);
    field(0x40020080,W(0x20056660+W(0x200002a0)*4u)>>7,0,10);
    field(0x40020044,W(0x20056660+W(0x200002a0)*4u)>>21,0,7);
    B(0x20074f77)=0;
}
uint32_t pcm22_post_low_to_high(void) {
    if(B(0x20074f77)) pcm22_sequence_21_complete();
    return 0;
}
