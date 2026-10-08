/* SPDX-License-Identifier: MIT. Locked-f89a4c46 TON callback family. */
#include <stdint.h>
#include "startup_ton_hooks.h"
#include "startup_initialize_leaves.h"

#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))

extern uint32_t opencfw_boot_ton_gate_write(uint32_t);
extern void opencfw_boot_delay_us_math(uint32_t);

uint32_t opencfw_boot_ton_trim_cache(void) {
    uint32_t revision = W(0x4002000c) & 0xffu;
    uint32_t variant = W(0x20000098);
    if (!(revision >= 34u || (revision == 33u && variant != 0u))) {
        B(0x20000554) = 14;
        B(0x20000555) = 31;
        B(0x20000558) = 21;
        B(0x20000559) = 31;
        B(0x20000556) = 11;
        B(0x20000557) = 11;
        return 0;
    }
    uint32_t trim = W(0x40020344);
    B(0x20000554) = (uint8_t)((trim >> 25) & 31u);
    B(0x20000555) = (uint8_t)((trim >> 11) & 31u);
    trim = W(0x40020358);
    B(0x20000558) = (uint8_t)((trim >> 8) & 31u);
    trim = W(0x40020354);
    B(0x20000559) = (uint8_t)((trim >> 17) & 31u);
    trim = W(0x4002034c);
    B(0x20000556) = (uint8_t)((trim >> 25) & 31u);
    B(0x20000557) = (uint8_t)((trim >> 11) & 31u);
    return 0;
}

uint32_t opencfw_boot_ton_trim_apply(uint32_t gpu_on, uint32_t gpu_mode) {
    volatile uint32_t *const state = (volatile uint32_t *)(uintptr_t)0x40021100;
    uint32_t was_enabled = *state & 1u;
    if (was_enabled) {
        (void)opencfw_boot_ton_gate_write(0);
        (void)opencfw_boot_delay_us_math(5);
        *state &= ~1u;
    }

    uint32_t row = 0;
    if ((uint8_t)gpu_on != 0u)
        row = ((uint8_t)gpu_mode == 0u) ? 1u : 2u;

    const volatile uint8_t *const cfg =
        (const volatile uint8_t *)(uintptr_t)(0x433f20u + row * 3u);
    uint32_t use_first = cfg[1] == 1u;
    uint32_t use_second = cfg[2] == 1u;
    W(0x40020340) |= 0x80000000u;

    uint32_t a, b;
    a = B(use_first ? 0x20000554 : 0x20000555);
    b = B(use_second ? 0x20000554 : 0x20000555);
    W(0x40020344) = (W(0x40020344) & ~(31u << 25)) | (a << 25);
    W(0x40020344) = (W(0x40020344) & ~(31u << 11)) | (b << 11);

    a = B(use_first ? 0x20000558 : 0x20000559);
    b = B(use_second ? 0x20000558 : 0x20000559);
    W(0x40020358) = (W(0x40020358) & ~(31u << 8)) | (a << 8);
    W(0x40020354) = (W(0x40020354) & ~(31u << 17)) | (b << 17);

    a = B(use_first ? 0x20000556 : 0x20000557);
    b = B(use_second ? 0x20000556 : 0x20000557);
    W(0x4002034c) = (W(0x4002034c) & ~(31u << 25)) | (a << 25);
    W(0x4002034c) = (W(0x4002034c) & ~(31u << 11)) | (b << 11);

    if (was_enabled) {
        *state |= 1u;
        (void)opencfw_boot_delay_us_math(5);
        (void)opencfw_boot_ton_gate_write(1);
    }
    return 0;
}

/* Stock42f1c8: its R0 return is caller R7, ignored by these callers.
 * This ordinary C interface deliberately exposes only ordered effects. */
void opencfw_boot_ton_clock_gate(uint32_t enabled){
 if((uint8_t)enabled){W(0x40021100)|=1;(void)opencfw_boot_delay_us_math(5);(void)opencfw_boot_ton_gate_write(1);}
 else {(void)opencfw_boot_ton_gate_write(0);(void)opencfw_boot_delay_us_math(5);W(0x40021100)&=~1u;}
}
/* Stock42f204: GPU state enters a temporary trim state. Integer offsets,
 * saturation and register ordering are instruction-derived; units unknown. */
uint32_t opencfw_boot_ton_lowpower_begin(uint32_t mode){
 if((uint8_t)mode!=2)(void)opencfw_boot_startup_hook24(1,0);
 if(((W(0x40021108)>>4)&3)!=3){
  W(0x20027090)=(W(0x40020080)>>10)&15;
  W(0x40020080)=(W(0x40020080)&~0x3c00u)|0x800;
  W(0x20027094)=W(0x40020088)&63;
  uint32_t v=(W(0x40020088)&63)+5;if(v>=64)v=63;
  W(0x40020088)=(W(0x40020088)&~63u)|(v&63);
  (void)opencfw_boot_delay_us_math(15);
 }else if(B(0x200271a8)){
  opencfw_boot_ton_clock_gate(0);
  W(0x40020080)=(W(0x40020080)&~0x3c00u)|0x400;
  uint32_t v=W(0x2002704c)+9;if(v>=128)v=127;
  W(0x40020044)=(W(0x40020044)&~127u)|(v&127);
  W(0x400201b0)|=256;
  v=W(0x20027050)+15;if(v>=128)v=127;
  W(0x4002004c)=(W(0x4002004c)&~127u)|(v&127);
  W(0x40020374)|=0x60000000;
  opencfw_boot_ton_clock_gate(1);(void)opencfw_boot_delay_us_math(15);
 }
 return 0;
}
/* Stock42f2fa restores cached fields before hook24(0,0). */
uint32_t opencfw_boot_ton_lowpower_end(void){
 if(((W(0x40021108)>>4)&3)!=3){
  W(0x40020088)=(W(0x40020088)&~63u)|(W(0x20027094)&63);
  W(0x40020080)=(W(0x40020080)&~0x3c00u)|((W(0x20027090)&15)<<10);
 }else if(B(0x200271a8)){
  opencfw_boot_ton_clock_gate(0);
  W(0x40020374)=(W(0x40020374)&~0x60000000u)|((W(0x20027054)&3)<<29);
  W(0x4002004c)=(W(0x4002004c)&~127u)|(W(0x20027050)&127);
  W(0x400201b0)&=~256u;
  W(0x40020044)=(W(0x40020044)&~127u)|(W(0x2002704c)&127);
  W(0x40020080)=(W(0x40020080)&~0x3c00u)|((W(0x20027058)&15)<<10);
  opencfw_boot_ton_clock_gate(1);
 }
 (void)opencfw_boot_startup_hook24(0,0);return 0;
}
/* Stock42f38e; R1 is unused, R2 points to selector-specific data. */
uint32_t opencfw_boot_ton_state_event(uint32_t selector,uint32_t enabled,void *payload){
 (void)enabled;
 switch((uint8_t)selector){
 case 1:if(*(const uint8_t *)payload)(void)opencfw_boot_ton_lowpower_begin(*(const uint8_t *)payload);else(void)opencfw_boot_ton_lowpower_end();break;
 case 2:((uint32_t *)payload)[1]=0xc3888000u;((uint32_t *)payload)[2]=0x447a0000u;break;
 default:break;
 }
 return 0;
}

/* Nine authenticated configuration bytes at433f20: data, not code. */
__attribute__((section(".rodata.opencfw_ton_rows"),used))
const uint8_t opencfw_ton_trim_rows[3][3]={{1,1,2},{1,1,2},{1,2,2}};
