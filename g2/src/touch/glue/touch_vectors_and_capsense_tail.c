/* SPDX-License-Identifier: MIT
 * Vector table symbols required by system_cat2 / reset path, plus CapSense
 * symbols that live in the closed libcy_capsense.a / tuner when those are
 * not yet linked into the compose.
 */
#include <stdint.h>
#include <stddef.h>

#ifndef CY_VECTOR_TABLE_SIZE
#define CY_VECTOR_TABLE_SIZE (48u)
#endif

typedef void (*cy_israddress)(void);

/* Wave 13 evidence: stock firmware_touch.bin 2.2.6.10 payload (FWPK+0x20, base 0x3300,
 * objdump -b binary --adjust-vma=0x3300) vector words: [0]=0x20002000 [1]=0x4675
 * [2]=0x465d [3]=0x465f [11]=0x465d [14..28]=0x465d, all others 0.
 * 0x465c is "b ." (shared_default_handler); 0x465e is push/bl 0xa338/pop, and
 * 0xa338 is "b ." (touch_runtime_7038_halt). */
void Default_Handler(void);
void Default_Handler(void) { for (;;) { } }

static void touch_runtime_7038_halt(void) { for (;;) { } }
void touch_hardfault_halt_handler(void);
void touch_hardfault_halt_handler(void) { touch_runtime_7038_halt(); }

/* Stock 0x4670 and 0x4718 are single "bx lr" leaves (touch_leaf_1370/1418). */
static void touch_leaf_1370_passthrough(void) { }
static void touch_leaf_1418_passthrough(void) { }

/* Stock 0x471c (touch_runtime_141c_handoff): str 0xaced8865 -> [0x40030000+0x38],
 * cpsid i, bl 0x4718. Literals from pool 0x472c/0x4730. */
static void touch_runtime_141c_handoff(void)
{
    *(volatile uint32_t *)0x40030038u = 0xaced8865u;
    __asm volatile ("cpsid i" ::: "memory");
    touch_leaf_1418_passthrough();
}

typedef struct { const uint32_t *src; uint32_t *dst; uint32_t words; } touch_copy_rec;
typedef struct { uint32_t *dst; uint32_t words; } touch_zero_rec;
extern const touch_copy_rec __touch_copy_table_start[], __touch_copy_table_end[];
extern const touch_zero_rec __touch_zero_table_start[], __touch_zero_table_end[];
extern uint32_t __touch_ram_vectors[];
extern const uint32_t __touch_flash_vectors[];

extern void touch_runtime_0164_reset_entry(void);

/* Stock 0x4674..0x46d8 (reset_startup_handler): bl 0x4670; bl 0x471c;
 * memcpy(0x20000400, 0x3300, 0xc0); VTOR(0xe000ed08) = 0x20000400; dsb sy;
 * word-copy table [0xb578,0xb584) then word-zero table [0xb584,0xb58c);
 * bl 0x3464. Our tables come from the linker script; stock's are
 * {0xb58c, 0x200004c0, 0xf1} and {0x200008a8, 0x1ac}. */
void Reset_Handler(void);
void Reset_Handler(void)
{
    touch_leaf_1370_passthrough();
    touch_runtime_141c_handoff();
    for (uint32_t i = 0; i < 48u; ++i) __touch_ram_vectors[i] = __touch_flash_vectors[i];
    *(volatile uint32_t *)0xe000ed08u = (uint32_t)(uintptr_t)__touch_ram_vectors;
    __asm volatile ("dsb sy" ::: "memory");
    for (const touch_copy_rec *r = __touch_copy_table_start; r < __touch_copy_table_end; ++r)
        for (uint32_t i = 0; i < r->words; ++i) r->dst[i] = r->src[i];
    for (const touch_zero_rec *r = __touch_zero_table_start; r < __touch_zero_table_end; ++r)
        for (uint32_t i = 0; i < r->words; ++i) r->dst[i] = 0u;
    touch_runtime_0164_reset_entry();
}

#define D ((cy_israddress)Default_Handler)
const cy_israddress __VECTOR_TABLE[CY_VECTOR_TABLE_SIZE]
    __attribute__((used, section(".vectors"))) = {
        [0] = (cy_israddress)(uintptr_t)0x20002000u, /* stock word 0 */
        [1] = Reset_Handler,
        [2] = D,
        [3] = touch_hardfault_halt_handler,
        [11] = D,
        [14] = D, [15] = D,
        [16] = D, [17] = D, [18] = D, [19] = D, [20] = D, [21] = D, [22] = D,
        [23] = D, [24] = D, [25] = D, [26] = D, [27] = D, [28] = D,
};
#undef D
const cy_israddress * const __Vectors = __VECTOR_TABLE;

/* CapSense tails not provided by composed upstream units.
 * Evidence: Cy_CapSense_TuInitialize removed — supplied by upstream
 * third-party/reference/infineon-capsense-v5/cy_capsense_tuner.c (v5). */
typedef struct cy_stc_capsense_context cy_stc_capsense_context_t;

/* Evidence (wave 10): Cy_CapSense_UpdateThresholds_Lib and
 * Cy_CapSense_CalculateRawTarget have no definition here. Their only callers,
 * Cy_CapSense_DpUpdateThresholds (cy_capsense_processing.c v5:813) and
 * Cy_CapSense_CdacSuccessAppr (cy_capsense_sensing_lp.c v5:2209), have no
 * callers in the w9 final ELF (objdump call scan), and the closed
 * libcy_capsense.a 5.0.0.6806 UpdateThresholds_Lib body (70 bytes,
 * position-independent) is absent from all 18 stock firmware_touch.bin
 * images (2.0.1.14..2.3.2.14). sources.json "retain" now gc-strips both dead
 * callers from those two units, so neither symbol is referenced. */
