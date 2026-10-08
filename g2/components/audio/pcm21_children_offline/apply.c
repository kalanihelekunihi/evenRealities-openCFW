#include "children.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
extern void stock_ton(uint32_t,uint32_t);
extern void stock_timer_publish(uint32_t);
extern void stock_timer_start(uint32_t);
extern void stock_timer_restart(uint32_t);
extern void stock_delay(uint32_t);
extern void stock_cache_disable(void);
extern void stock_cache_enable(void);
extern void stock_timer_stop(void);
extern void stock_completion(void);
extern void stock_timer_clear(uint32_t);
static uint32_t cal(uint32_t i) {return W(0x20056660+4*i);}
static uint32_t core(uint32_t x) {return (x>>7)&1023;}
static uint32_t f(uint32_t x) {return (x>>21)&127;}
static uint32_t c(uint32_t x) {return x&127;}
static void field(uint32_t a,uint32_t v,uint32_t mask,uint32_t shift) {W(a)=(W(a)&~mask)|((v<<shift)&mask);}
static uint32_t rising(uint32_t old,uint32_t next) {return W(0x200001f4+4*old)<W(0x200001f4+4*next)||W(0x20000244+4*old)<W(0x20000244+4*next);}
static uint32_t special(uint32_t p) {return p==1||p==5||p==17||p==8||p==12||p==14||p==15;}
static void setcore(uint32_t value,uint32_t boosted) {
    if(boosted) {W(0x200742c8)=value+7>=1024?1023-value:7;value=(value+W(0x200742c8))&1023;}
    field(0x40020080,value,1023,0);
}
void pcm21_apply(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton) {
    uint32_t nc=cal(next),oc=cal(old),cached=W(0x20000298),cachedc=cal(cached);
    if(next==old) {if(ton!=old_ton) stock_ton(ton,next);return;}
    if(rising(old,next)) {
        if(ton!=old_ton || special(next)||special(old)) stock_ton(ton,next);
        W(0x200742cc)=f(nc);W(0x200742d0)=c(nc);
        field(0x40020080,(nc>>17)&15,0x3c00,10);
        uint32_t oldf,oldc;
        if(!(W(0x400083e0)&1)) {setcore(core(nc),0);oldf=f(oc);oldc=c(oc);}
        else {setcore(core(nc),1);oldf=f(cachedc);oldc=c(cachedc);}
        uint32_t deltaf=oldf<W(0x200742cc)?2*(W(0x200742cc)-oldf):W(0x200742cc)-oldf;
        uint32_t deltac=oldc<W(0x200742d0)?2*(W(0x200742d0)-oldc):W(0x200742d0)-oldc;
        uint32_t wait;
        if(deltaf+oldf>=128 || deltac+oldc>=128 || B(0x20074f69)) {
            /* Stock OR after clearing low7, rather than saturating the target. */
            W(0x40020044)=(W(0x40020044)&~127u)|W(0x200742cc);
            W(0x4002004c)=(W(0x4002004c)&~127u)|W(0x200742d0);
            wait=B(0x20074f69)?2000:200;
        } else {field(0x40020044,deltaf+oldf,127,0);field(0x4002004c,deltac+oldc,127,0);wait=50;}
        if(!(W(0x400083e0)&1)) {stock_timer_publish(1);stock_timer_start(wait);W(0x20000298)=old;}
        else stock_timer_restart(wait);
        uint32_t cache=0;
        if((old<8 || (uint32_t)(old-16)<4) && (uint32_t)(next-8)<8) {
            if(W(0xe000ed14)&0x20000) {stock_cache_disable();cache=1;}
            W(0x4002037c)|=0x10000;B(0x20074f6d)=1;
        }
        stock_delay(20);if(cache) stock_cache_enable();
    } else {
        uint32_t enabled=W(0x400083e0)&1;
        setcore(core(nc),enabled && rising(W(0x20000298),next));
        field(0x40020080,(nc>>17)&15,0x3c00,10);
        if(B(0x20074f69)||!(W(0x400083e0)&1)) {
            W(0x40020044)=(W(0x40020044)&~127u)|f(nc);
            W(0x4002004c)=(W(0x4002004c)&~127u)|c(nc);
        } else {W(0x200742cc)=f(nc);W(0x200742d0)=c(nc);}
        if(ton!=old_ton||special(next)||special(old)) stock_ton(ton,next);
        if((W(0x400083e0)&1) && !rising(W(0x20000298),next)) {stock_timer_stop();stock_completion();stock_timer_clear(0);}
    }
}
