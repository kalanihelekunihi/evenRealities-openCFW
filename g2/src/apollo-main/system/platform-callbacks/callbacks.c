#include "callbacks.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define SLOT(i) W(0x20073270u + 4u*(i))
extern uint32_t early_zero(uint32_t), early_other(uint32_t);
extern void middle_action0(uint32_t);
extern uint32_t middle_zero(uint32_t), middle_other(uint32_t), middle_action2(uint8_t *);
/* The SPOT-manager table initializer (stock 0x480434) is the stock-variant
 * am_hal_spotmgr_init_480434 in hal/p-06-spotmgr. */

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
