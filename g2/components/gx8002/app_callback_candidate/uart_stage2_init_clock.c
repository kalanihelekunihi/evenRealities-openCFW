/* SPDX-License-Identifier: MIT
 * UART stage-2 reset clock/interrupt initializer at native 0x10005100.
 * Control-register bitfields and NVIC write order come from stage-2 bytes.
 */
#include <stdint.h>

extern void gx8002_uart_stage2_clock_subinit_52c4(void);
extern uint32_t gx8002_uart_stage2_ready_4fb0(void);
extern void gx8002_uart_stage2_interrupt_setup_29a0(void);

static uint32_t cr18_read(void) { uint32_t x; __asm__ volatile("mfcr %0, cr<18,0>" : "=r"(x)); return x; }
static uint32_t cr19_read(void) { uint32_t x; __asm__ volatile("mfcr %0, cr<19,0>" : "=r"(x)); return x; }
static uint32_t cr20_read(void) { uint32_t x; __asm__ volatile("mfcr %0, cr<20,0>" : "=r"(x)); return x; }
static uint32_t cr21_read(void) { uint32_t x; __asm__ volatile("mfcr %0, cr<21,0>" : "=r"(x)); return x; }
static void cr18_write(uint32_t x) { __asm__ volatile("mtcr %0, cr<18,0>" :: "r"(x) : "memory"); }
static void cr19_write(uint32_t x) { __asm__ volatile("mtcr %0, cr<19,0>" :: "r"(x) : "memory"); }
static void cr20_write(uint32_t x) { __asm__ volatile("mtcr %0, cr<20,0>" :: "r"(x) : "memory"); }
static void cr21_write(uint32_t x) { __asm__ volatile("mtcr %0, cr<21,0>" :: "r"(x) : "memory"); }
static void cr1_write(uint32_t x) { __asm__ volatile("mtcr %0, cr<1,0>" :: "r"(x) : "memory"); }

void gx8002_uart_stage2_clear_bss_292c(void)
{
    for (uintptr_t address = UINT32_C(0x2000953c);
         address < UINT32_C(0x2000a1fc); address += 4u)
        *(volatile uint32_t *)address = 0;
}

void gx8002_uart_stage2_init_clock(void)
{
    uint32_t cr19 = cr19_read();
    uint32_t cr20 = cr20_read();
    uint32_t cr21 = cr21_read();
    cr21_write(cr21 & ~UINT32_C(7));
    cr20 = (cr20 & UINT32_C(0xfff)) | UINT32_C(0x3f);
    cr19_write((cr19 & UINT32_C(0xfefffcfe)) | UINT32_C(0x300));
    cr20_write(cr20);
    cr18_write(cr18_read() | UINT32_C(3));
    gx8002_uart_stage2_clock_subinit_52c4();
    if (gx8002_uart_stage2_ready_4fb0() == 0)
        gx8002_uart_stage2_clear_bss_292c();
    cr1_write(UINT32_C(0x10002800));

    volatile uint32_t *const nvic = (volatile uint32_t *)(uintptr_t)UINT32_C(0xe000e100);
    nvic[0xb10 / 4] = 255u;
    for (unsigned i = 0; i < 4u; ++i) {
        nvic[(0x200 / 4) + i] = 0;
        nvic[(0x180 / 4) + i] = UINT32_MAX;
    }
    __asm__ volatile("psrset ee, ie" ::: "memory");
    gx8002_uart_stage2_interrupt_setup_29a0();
}
