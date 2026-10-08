#include "callbacks.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
/* Reconstructed request; padding byte19 is not an input to the selected helper. */
struct power_request { uint32_t masks[4]; uint8_t range, state, request; };
extern uint32_t callback_save_disable_irq(void);
extern uint32_t callback_classify(float);
extern void callback_prepare_state(struct power_request *);
extern void callback_change_state(uint32_t next, uint32_t old);
extern uint32_t callback_plan(struct power_request *,uint32_t *,uint32_t *);
extern void callback_apply(uint32_t next_a,uint32_t old_a,uint32_t next_b,uint32_t old_b);
static void restore(uint32_t mask) { __asm__ volatile("msr primask, %0"::"r"(mask):"memory"); }
uint32_t audio_platform_newer_control(uint32_t action,uint32_t enable,uint8_t *m) {
    action=(uint8_t)action; enable=(uint8_t)enable;
    if(((W(0x40021108)>>4)&3u)!=3) return 0;
    if(W(0x2005665c)!=0x1f01600d) return 1;
    uint32_t irq=callback_save_disable_irq(), result=0;
    if(action==0 && m && B(0x20074f79)>=2 && B(0x20074f79)<=4 && m[0]<=1) {
        B(0x20074f79)=m[0]; restore(irq); return 0;
    }
    struct power_request r;
    r.masks[0]=W(0x40021008); r.masks[1]=W(0x40021010);
    r.masks[2]=W(0x40021018); r.masks[3]=W(0x40021028);
    r.range=B(0x20074f78); r.state=B(0x20074f79);
    r.request=(r.masks[0]&(1u<<18)) ? (B(0x20074f60)?2:1) : 0;
    unsigned plan=1;
    switch(action) {
    case 0:
        if(!m) { result=6; break; }
        r.state=m[0];
        if(r.state!=B(0x20074f79)) {
            if(r.state==2) {
                callback_prepare_state(&r);
                B(0x20074f6a)= ((W(0x200002a0)-9u)<3u) && B(0x20004540)!=7;
            }
            uint8_t old=B(0x20074f79);
            if(!((old==0 && (r.state==1||r.state==2))||(old==1 && r.state==0))) {
                callback_change_state(r.state,old); plan=0;
            }
            B(0x20074f79)=r.state;
        }
        break;
    case 1: if(m) r.request=m[0]; else result=6; break;
    case 2:
        if(!m) { result=6; break; }
        { union { uint32_t bits; float value; } x; x.bits=*(uint32_t *)m;
          r.range=(uint8_t)callback_classify(x.value); B(0x20074f78)=r.range;
          B(0x20004539)=r.range<3;
          switch(r.range) {
          case 0: ((uint32_t *)m)[1]=0xc3888000; ((uint32_t *)m)[2]=0xc1a00000; break;
          case 1: ((uint32_t *)m)[1]=0xc1b00000; ((uint32_t *)m)[2]=0; break;
          case 2: ((uint32_t *)m)[1]=0xc0000000; ((uint32_t *)m)[2]=0x42480000; break;
          case 3: ((uint32_t *)m)[1]=0x42400000; ((uint32_t *)m)[2]=0x447a0000; break;
          default: ((uint32_t *)m)[1]=0; ((uint32_t *)m)[2]=0; result=6; break;
          }
        } break;
    case 3: if(enable) { if(m) r.masks[0]|=*(uint32_t *)m; else result=6; } break;
    case 4: if(enable) { if(m) r.masks[1]|=*(uint32_t *)m; else result=6; } break;
    case 5: if(m) r.masks[2]=*(uint32_t *)m; else result=6; break;
    case 6: if(enable) { if(m) r.masks[3]=*(uint32_t *)m; else result=6; } break;
    default: result=6; break;
    }
    if(result==0 && plan) {
        uint32_t next_a=0,next_b=0;
        result=callback_plan(&r,&next_a,&next_b);
        if(result==0) {
            uint32_t old_a=W(0x200002a0),old_b=W(0x20000314);
            if(next_a!=old_a || next_b!=old_b) callback_apply(next_a,old_a,next_b,old_b);
            W(0x200002a0)=next_a; W(0x20000314)=next_b;
        }
    }
    restore(irq); return result;
}
