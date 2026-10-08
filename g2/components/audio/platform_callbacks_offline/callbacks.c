#include "callbacks.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define SLOT(i) W(0x20073270u + 4u*(i))
typedef uint32_t (*init_fn)(void);
extern uint32_t early_zero(uint32_t), early_other(uint32_t);
extern void middle_action0(uint32_t);
extern uint32_t middle_zero(uint32_t), middle_other(uint32_t), middle_action2(uint8_t *);
uint32_t audio_platform_callbacks_initialize(void) {
    for (unsigned i=0;i<15;i++) SLOT(i)=0;
    uint32_t major=W(0x4002000c)&255u, revision=W(0x200001e8);
    unsigned a=(major==0x23 && revision>=2)||major>=0x24;
    unsigned b=(major==0x22 && revision==2)||(major==0x23 && revision==1);
    unsigned c=(major==0x21 && (revision==2||revision==3))||(major==0x22 && revision==0);
    unsigned d=major==0x21 && revision>=3;
    unsigned e=(major==0x22 && revision==1)||(major==0x23 && revision==0);
    unsigned f=b && !(B(0x2007197c)&1u);
    B(0x20074f68)=a; B(0x20074f64)=b; B(0x20074f65)=c;
    B(0x20074f66)=d; B(0x20074f67)=e; B(0x20074f69)=f;
    if(c||e||f) {
        W(0x40020028)&=~2u; W(0x40020028)|=1u;
        W(0x40020060)|=0x8000u; W(0x40020060)|=0x4000u; W(0x40020060)|=0x2000u;
    }
    if(a) {
        SLOT(0)=0x5a4d49; SLOT(1)=0x5a490d; SLOT(2)=0x5a4e0d;
        SLOT(7)=0x5a4d01; SLOT(10)=0x5a40b7; SLOT(11)=0x5a40cb;
    } else if(b) {
        SLOT(0)=0x5a1c19; SLOT(1)=0x5a1739; SLOT(2)=0x5a1da5;
        SLOT(5)=0x5a1bbd; SLOT(6)=0x5a1bcd; SLOT(7)=0x5a1bed; SLOT(11)=0x5a0bcd;
    } else if((major==0x21 && revision>=2)||(major==0x22 && revision<2)||(major==0x23 && revision==0)) {
        SLOT(0)=0x5a08e5; SLOT(1)=0x5a0787; SLOT(2)=0x5a0a6d; SLOT(3)=0x5a07e7;
        SLOT(4)=0x5a07f1; SLOT(12)=0x5a085f; SLOT(13)=0x5a08b7; SLOT(14)=0x5a08cb;
        if(major==0x21 && revision==2) { SLOT(6)=0x59fd83; SLOT(7)=0x59fda9; }
        else { SLOT(6)=0x5a081d; SLOT(7)=0x5a0843; }
    } else if(major==0x21 && revision==1) {
        SLOT(0)=0x5a0019; SLOT(1)=0x59fd37; SLOT(6)=0x59fd83; SLOT(7)=0x59fda9;
    }
    if(major==0x21 && revision<2) { SLOT(8)=0x59fdc3; SLOT(9)=0x59fe5b; }
    return SLOT(0) ? ((init_fn)(uintptr_t)SLOT(0))() : 0;
}
uint32_t audio_platform_early_control(uint32_t action,uint32_t enable,uint8_t *m) {
    (void)enable;
    switch((uint8_t)action) {
    case 1: if(m[0]==0) (void)early_zero(0); else (void)early_other(m[0]); break;
    case 2: /* Literal values resolved independently by verifier/disassembly. */
        ((uint32_t *)m)[1]=0xc3888000; ((uint32_t *)m)[2]=0x447a0000; break;
    default: break;
    }
    return 0;
}
uint32_t audio_platform_middle_control(uint32_t action,uint32_t enable,uint8_t *m) {
    (void)enable;
    switch((uint8_t)action) {
    case 0: if(m && m[0]==2) middle_action0(2); return 0;
    case 1: return m[0]==0 ? middle_zero(0) : middle_other(m[0]);
    case 2: return middle_action2(m);
    default: return 0;
    }
}
