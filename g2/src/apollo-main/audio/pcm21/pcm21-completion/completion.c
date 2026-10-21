#include "completion.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
extern void stock_delay(uint32_t);
extern void stock_timer_stop(void);
extern uint32_t stock_save_irq(void);
static void field(uint32_t a,uint32_t v,uint32_t mask,uint32_t shift) {W(a)=(W(a)&~mask)|((v<<shift)&mask);}
void pcm21_timer_publish(uint32_t boost_memory) {
    if((uint8_t)boost_memory) {W(0x400201b0)|=0x18000;field(0x40020088,W(0x200566c4)>>14,63,0);}
    uint32_t trim=W(0x40020080)&1023;
    W(0x200742c8)=trim+7>=1024?1023-trim:7;
    field(0x40020080,W(0x40020080)+W(0x200742c8),1023,0);
}
void pcm21_boost_remove(uint32_t remove_core) {
    field(0x40020088,W(0x200566c4)>>2,63,0);
    field(0x400201b0,W(0x200566c4),0x18000,15);
    if((uint8_t)remove_core) field(0x40020080,W(0x40020080)-W(0x200742c8),1023,0);
}
void pcm21_buck_complete(void) {
    if(!B(0x20074f69)) {field(0x40020044,W(0x200742cc),127,0);field(0x4002004c,W(0x200742d0),127,0);}
}
void pcm21_timer_isr(void) {
    uint32_t irq=stock_save_irq();pcm21_buck_complete();
    if(B(0x20074f6d)) {
        if(W(0x20000294)!=8 && W(0x20000294)!=12) {W(0x4002037c)|=8;W(0x4002037c)|=0x40;}
        B(0x20074f6d)=0;
    }
    stock_timer_stop();pcm21_boost_remove(1);
    __asm volatile("msr primask, %0" :: "r"(irq) : "memory");
}
void pcm21_ton(uint32_t selector,uint32_t profile) {
    uint32_t core=W(0x40020080)&1023,mem=W(0x40020088)&63;
    uint32_t cb=core+14>=1024?1023-core:14,mb=mem+6>=64?63-mem:6;
    field(0x40020080,W(0x40020080)+cb,1023,0);field(0x40020088,W(0x40020088)+mb,63,0);
    stock_delay(20);W(0x40020380)|=0x20000000;W(0x40020380)|=0x10000000;stock_delay(20);
    uint32_t ct,ft;
    switch(selector) {
    case 0:ct=W(0x200566b8)&31;ft=(W(0x200566b8)>>10)&31;break;
    case 1:ct=(W(0x200566b8)>>5)&31;ft=(W(0x200566b8)>>15)&31;break;
    case 2:ct=W(0x200566b0)&31;ft=W(0x200566b4)&31;break;
    case 3:ct=(W(0x200566b0)>>10)&31;ft=(W(0x200566b4)>>10)&31;break;
    case 4:ct=(W(0x200566b0)>>5)&31;ft=(W(0x200566b4)>>5)&31;break;
    case 6:ct=W(0x200566bc)&31;ft=(W(0x200566bc)>>10)&31;break;
    case 7:ct=(W(0x40020344)>>11)&31;ft=(W(0x40020354)>>17)&31;break;
    default:ct=(W(0x200566b0)>>15)&31;ft=(W(0x200566b4)>>15)&31;break;
    }
    if(profile==8) ct=(W(0x200566b8)>>20)&31;
    else if(profile==12) ct=(W(0x200566b0)>>20)&31;
    else if(profile==14) ct=ct+6>=32?31:ct+6;
    else if(profile==15) ct=ct+12>=32?31:ct+12;
    field(0x40020344,ct,0x3e000000,25);field(0x40020358,ft,0x1f00,8);
    field(0x4002034c,(profile==1||profile==5||profile==17)?4:6,0x3e000000,25);
    W(0x40020380)&=~0x20000000u;W(0x40020380)&=~0x10000000u;
    field(0x40020080,W(0x40020080)-cb,1023,0);field(0x40020088,W(0x40020088)-mb,63,0);
}
