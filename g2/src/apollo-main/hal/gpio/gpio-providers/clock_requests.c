#include "clock_requests.h"
extern unsigned char g2ref_g2_stock_ram_200740e8[] __asm__("g2_stock_ram_200740e8"); /* Fix 44: stock owner of blob+offset access */
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_stock_ram_20074000[] __asm__("g2_stock_ram_20074000");
#define W(a) (*(volatile uint32_t *)(a))
#define B(a) (*(volatile uint8_t *)(a))
extern uint32_t stock_save_irq(void);
void audio_clock_reference_update(uint32_t reference){
 uint32_t mask=stock_save_irq();
 W(0x40008858)=(W(0x40008858)&~64u)|(((uint8_t)reference&1u)<<6);
 __asm volatile("msr primask, %0"::"r"(mask):"memory");
}
void audio_clock_requests_update(uint32_t mux_index,uint32_t sources){
 uint32_t mask=stock_save_irq();
 B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_200740e8+0x4u)+(uint8_t)mux_index)=(uint8_t)sources;
 uint32_t needed=0;
 for(uint32_t i=0;i<6;i++)needed|=B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_200740e8+0x4u)+i);
 for(uint32_t bit=0;bit<5;bit++)W(0x40008858)=(W(0x40008858)&~(1u<<(bit+1)))|(((needed>>bit)&1u)<<(bit+1));
 __asm volatile("msr primask, %0"::"r"(mask):"memory");
}
