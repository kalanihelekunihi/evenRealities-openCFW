#include "completion.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t stock_info_read(uint32_t,uint32_t,uint32_t,uint32_t *);
extern void stock_timer_init(void);
static void field(uint32_t a,uint32_t v,uint32_t mask,uint32_t shift) {W(a)=(W(a)&~mask)|((v<<shift)&mask);}
uint32_t pcm21_before_override(void) {field(0x4002034c,6,0x3e000000,25);return 0;}
uint32_t pcm21_before_enable(void) {if(W(0x2005665c)==0x1f01600d) field(0x40020080,W(0x2005667c)>>7,1023,0);return 0;}
uint32_t pcm21_after_enable(void) {
    if(W(0x2005665c)==0x1f01600d) {field(0x40020088,W(0x200566c4)>>2,63,0);field(0x400201b0,W(0x200566c4),0x18000,15);}
    return 0;
}
uint32_t pcm21_initialize(void) {
    if((W(0x400201bc)&8) && !(W(0x40021008)&0x8000000)) return 7;
    uint32_t result=stock_info_read(1,0x25c,16,(uint32_t *)(uintptr_t)0x20056660);if(result) return result;
    for(uint32_t i=0;i<4;i++) W(0x200566a0+4*i)=W(0x20056670+4*i);
    for(uint32_t i=0;i<4;i++) field(0x200566a0+4*i,W(0x20056690+4*i),127,0);
    uint32_t info[4];result=stock_info_read(1,0x270,4,info);if(result) return result;
    for(uint32_t i=0;i<4;i++) W(0x200566b0+4*i)=info[i];
    result=stock_info_read(1,0x278,1,info);if(result) return result;
    W(0x200566c4)=info[0];
    field(0x20056680,(((W(0x20056690)>>21)&127)+((W(0x20056694)>>21)&127))/2,0xfe00000,21);
    field(0x20056684,W(0x20056688)>>21,0xfe00000,21);
    field(0x20056680,W(0x20056690)>>28,0x10000000,28);
    field(0x20056684,W(0x20056688)>>28,0x10000000,28);
    field(0x20056690,W(0x20056694)>>21,0xfe00000,21);
    field(0x20056690,W(0x20056694)>>28,0x10000000,28);
    field(0x20056690,W(0x20056694)>>17,0x1e0000,17);
    field(0x20056690,W(0x20056694)>>7,0x1ff80,7);
    field(0x200566c4,31,0x3f00000,20);W(0x2005665c)=0x1f01600d;
    stock_timer_init();return 0;
}
