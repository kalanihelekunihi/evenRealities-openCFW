#include "control.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
extern uint32_t stock_save_irq(void);
extern uint32_t pcm21_classify(float);
extern void stock_prepare(struct pcm21_power_request *);
extern void stock_change_state(uint32_t next,uint32_t old);
extern uint32_t stock_plan(struct pcm21_power_request *,uint32_t *,uint32_t *);
extern void stock_apply(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton);
static void restore_irq(uint32_t irq) { __asm volatile("msr primask, %0" :: "r"(irq) : "memory"); }
uint32_t pcm21_control(uint32_t action,uint32_t enable,uint8_t *metadata) {
    if(((W(0x40021108)>>4)&3)!=3) return 0;
    if(W(0x2005665c)!=0x1f01600d) return 1;
    action=(uint8_t)action;enable=(uint8_t)enable;
    uint32_t irq=stock_save_irq(),result=0,defer=0,skip=0,replan=1;
    /* Stock profiling probes read four readable bytes, even for a byte enum.
       Profiling calls themselves are NOPs; stack-only log packing is omitted. */
    if(metadata) (void)*(volatile uint32_t *)metadata;
    if(action==0 && metadata && B(0x20074f76)>=2 && B(0x20074f76)<=4 && *metadata<=1) {
        B(0x20074f76)=*metadata;skip=1;
    }
    if(!skip) {
        struct pcm21_power_request r;
        r.masks[0]=W(0x40021008);r.masks[1]=W(0x40021010);
        r.masks[2]=W(0x40021018);r.masks[3]=W(0x40021028);
        r.range=B(0x20074f75);r.cpu=B(0x20074f76);
        r.gpu=(r.masks[0]&0x40000)?(B(0x20074f60)?2:1):0;
        switch(action) {
        case 0:
            if(!metadata) { result=6;break; }
            r.cpu=*metadata;
            if(B(0x20074f76)!=r.cpu) {
                if(r.cpu==2) {
                    stock_prepare(&r);
                    B(0x20074f6a)=W(0x20000294)!=8 && W(0x20000294)!=12;
                }
                if(B(0x20074f76)==0 && r.cpu==1) B(0x20074f76)=r.cpu;
                else if(B(0x20074f76)==1 && r.cpu==0) defer=1;
                else if(B(0x20074f76)==0 && r.cpu==2) {
                    if((W(0x200742b0)&1) && r.gpu!=1 && r.gpu!=2 && !(r.masks[0]&0x3fffffff) && !(r.masks[1]&0x4c4)) B(0x20074f6c)=1;
                    B(0x20074f76)=r.cpu;
                } else {
                    stock_change_state(r.cpu,B(0x20074f76));replan=0;B(0x20074f76)=r.cpu;
                }
            }
            break;
        case 1: if(metadata) r.gpu=*metadata;else result=6;break;
        case 2:
            if(!metadata) { result=6;break; }
            r.range=(uint8_t)pcm21_classify(*(float *)metadata);B(0x20074f75)=r.range;
            B(0x20004539)=B(0x20074f75)<3;
            switch(B(0x20074f75)) {
            case 0:((uint32_t *)metadata)[1]=0xc3888000;((uint32_t *)metadata)[2]=0xc1a00000;break;
            case 1:((uint32_t *)metadata)[1]=0xc1b00000;((uint32_t *)metadata)[2]=0;break;
            case 2:((uint32_t *)metadata)[1]=0xc0000000;((uint32_t *)metadata)[2]=0x42480000;break;
            case 3:((uint32_t *)metadata)[1]=0x42400000;((uint32_t *)metadata)[2]=0x447a0000;break;
            case 4:((uint32_t *)metadata)[1]=0;((uint32_t *)metadata)[2]=0;result=6;break;
            }
            break;
        case 3:if(enable) { if(metadata) r.masks[0]|=*(uint32_t *)metadata;else result=6; }break;
        case 4:if(enable) { if(metadata) r.masks[1]|=*(uint32_t *)metadata;else result=6; }break;
        case 5:if(metadata) r.masks[2]=*(uint32_t *)metadata;else result=6;break;
        case 6:if(enable) { if(metadata) r.masks[3]=*(uint32_t *)metadata;else result=6; }break;
        default:result=6;break;
        }
        if(result==0 && replan) {
            uint32_t next=0,ton=0;result=stock_plan(&r,&next,&ton);
            if(result==0) {
                uint32_t old=W(0x20000294),old_ton=W(0x2000029c);
                if(next!=old || ton!=old_ton) {
                    if(metadata) (void)*(volatile uint32_t *)metadata;
                    stock_apply(next,old,ton,old_ton);
                    if(defer) {stock_change_state(r.cpu,B(0x20074f76));B(0x20074f76)=r.cpu;}
                }
                if((W(0x20000294)==12 && next>=13 && next<=15) || (W(0x20000294)==8 && next>=9 && next<=11)) {
                    W(0x4002037c)|=0x40;W(0x4002037c)|=8;
                }
                W(0x20000294)=next;W(0x2000029c)=ton;
            }
        }
    }
    restore_irq(irq);return result;
}
