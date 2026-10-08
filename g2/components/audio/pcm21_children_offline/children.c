#include "children.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
extern uint32_t stock_stimer_running(void);
void pcm21_prepare(struct pcm21_power_request *r) {
    if(r->range==3 || (r->masks[0]&0x3fffffff) || (r->masks[1]&0x4c4) || (W(0x400204d8)&0x20000000)) {B(0x20074f7b)=1;return;}
    if(stock_stimer_running() && (W(0x40008800)&15)>=1 && (W(0x40008800)&15)<3) {B(0x20074f7b)=1;return;}
    for(uint32_t i=0;i<16;i++) {
        if(!(W(0x40008200+32*i)&1) || !(W(0x40008010)&(1u<<i))) continue;
        uint32_t clk=(W(0x40008200+32*i)>>8)&511;
        if(clk<6 || (clk>=19 && clk<25) || (clk>=256 && clk<480)) {B(0x20074f7b)=1;return;}
    }
    B(0x20074f7b)=0;
}
void pcm21_change_state(uint32_t next,uint32_t old) {
    next=(uint8_t)next;old=(uint8_t)old;
    if(old==1 && next==2 && !B(0x20074f6d)) B(0x20074f6b)=1;
    if(old==1 && next==0) {W(0x4002037c)&=~0x10000u;W(0x4002037c)&=~8u;W(0x4002037c)&=~0x40u;B(0x20074f6d)=0;}
}
uint32_t pcm21_plan(struct pcm21_power_request *r,uint32_t *profile,uint32_t *ton) {
    uint32_t desc=W(0x78ee54),periph=!!((r->masks[0]&0x3fffffff)||(r->masks[1]&0x4c4));
    uint32_t cpu=r->cpu==1?1:r->cpu==0?0:((W(0x40021000)&3)==2);
    desc=(desc&~0xffffffu)|cpu|((periph||r->gpu==1||r->gpu==2)<<4)|((r->range&15)<<8)|((r->gpu==1?1:r->gpu==2?2:0)<<12)|(periph<<16)|(!!(r->masks[0]&0xc00000)<<20);
    uint32_t k=desc&0xf00fff,flag=B(0x200742b0)&1;
    switch(k) {
    case 0:*profile=flag?7:3;break;case 1:*profile=flag?15:11;break;case 0x10:*profile=7;break;case 0x11:*profile=15;break;
    case 0x100:*profile=flag?6:2;break;case 0x101:*profile=flag?14:10;break;case 0x110:*profile=6;break;case 0x111:*profile=14;break;
    case 0x200:*profile=flag?5:1;break;case 0x201:*profile=flag?13:9;break;case 0x210:*profile=5;break;case 0x211:*profile=13;break;
    case 0x300:*profile=flag?4:0;break;case 0x301:*profile=flag?12:8;break;case 0x310:*profile=4;break;case 0x311:*profile=12;break;
    case 0x100010:*profile=19;break;case 0x100011:*profile=15;break;case 0x100110:*profile=18;break;case 0x100111:*profile=14;break;
    case 0x100210:*profile=17;break;case 0x100211:*profile=13;break;case 0x100310:*profile=16;break;case 0x100311:*profile=12;break;
    default:return 5;
    }
    switch(desc&0xff00f) {
    case 0:*ton=0;break;case 1:*ton=flag?7:1;break;case 0x1000:case 0x11000:*ton=2;break;case 0x2000:case 0x12000:*ton=3;break;
    case 0x1001:case 0x11001:*ton=4;break;case 0x2001:case 0x12001:*ton=5;break;case 0x10000:*ton=6;break;case 0x10001:*ton=7;break;
    default:return 5;
    }
    return 0;
}
