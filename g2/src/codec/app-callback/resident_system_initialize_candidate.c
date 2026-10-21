/* SPDX-License-Identifier: MIT
 * Isolated image-A SRAM startup root 0x1002354c. Direct native CR and VIC
 * instruction order is retained. Final vector source, 0x10025a88 clock root,
 * and section/alias placement are explicit external contracts.
 */
#include <stdint.h>

extern void gx8002_resident_clock_init_pointer_25a88(
    uint32_t mode, uint32_t mask, uint32_t enabled, uint32_t cpu_state);
extern uint32_t gx8002_resident_start_mode_24984(void);
extern void gx8002_resident_clear_bss_23528(void);
extern void gx8002_resident_board_initialize_25cbc(void);
extern const uint8_t gx8002_resident_vectors_23400[];

static inline uint32_t gx8002_read_cr19(void)
{
    uint32_t value;
    __asm__ volatile("mfcr %0, cr<19, 0>" : "=r"(value));
    return value;
}
static inline uint32_t gx8002_read_cr20(void)
{
    uint32_t value;
    __asm__ volatile("mfcr %0, cr<20, 0>" : "=r"(value));
    return value;
}
static inline uint32_t gx8002_read_cr21(void)
{
    uint32_t value;
    __asm__ volatile("mfcr %0, cr<21, 0>" : "=r"(value));
    return value;
}
static inline uint32_t gx8002_read_cr18(void)
{
    uint32_t value;
    __asm__ volatile("mfcr %0, cr<18, 0>" : "=r"(value));
    return value;
}

void gx8002_resident_system_initialize_2354c(void)
{
    uint32_t cr19 = gx8002_read_cr19();
    uint32_t cr20 = gx8002_read_cr20();
    uint32_t cr21 = gx8002_read_cr21();
    cr21 &= ~UINT32_C(7);
    __asm__ volatile("mtcr %0, cr<21, 0>" : : "r"(cr21) : "memory");
    cr19 = (cr19 & UINT32_C(0xfefffcfe)) | UINT32_C(0x300);
    __asm__ volatile("mtcr %0, cr<19, 0>" : : "r"(cr19) : "memory");
    cr20 = (cr20 & UINT32_C(0xfff)) | UINT32_C(0x3f);
    __asm__ volatile("mtcr %0, cr<20, 0>" : : "r"(cr20) : "memory");
    uint32_t cr18 = gx8002_read_cr18() | 3u;
    __asm__ volatile("mtcr %0, cr<18, 0>" : : "r"(cr18) : "memory");

    gx8002_resident_clock_init_pointer_25a88(
        0u, UINT32_C(0xfefffcfe), 1u, cr18);
    if (gx8002_resident_start_mode_24984() == 0u)
        gx8002_resident_clear_bss_23528();
    gx8002_resident_board_initialize_25cbc();

    __asm__ volatile("mtcr %0, cr<1, 0>" : :
                     "r"((uint32_t)(uintptr_t)gx8002_resident_vectors_23400)
                     : "memory");
    volatile uint32_t *const vic =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xe000e100);
    vic[0xb10u / 4u] = 0xffu;
    for (uint32_t bank = 0; bank < 4u; ++bank) {
        vic[(0x200u / 4u) + bank] = 0u;
        vic[(0x180u / 4u) + bank] = UINT32_MAX;
    }
    __asm__ volatile("psrset ee, ie" ::: "memory");
}
