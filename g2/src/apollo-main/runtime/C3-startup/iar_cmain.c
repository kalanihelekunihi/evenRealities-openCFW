/* IAR __cmain, __low_level_init and __iar_data_init3 for the Apollo main
 * image, reconstructed from the 2.2.6.10 disassembly (IAR cstartup_M /
 * low_level_init.c / data_init.c; no source path is retained).
 *
 * Stock ranges:
 *   0x005e4228..0x005e4231  __low_level_init (literals 0x5e4244 = 0x438000,
 *                           0x5e4248 = 0xe000ed08)
 *   0x005e4294..0x005e42b1  __cmain (0x5e42b2 is padding; never returns)
 *   0x005e42b4..0x005e42d3  __iar_data_init3 (literals 0x5e42d4/0x5e42d8 are
 *                           PC-relative offsets to the region table bounds)
 *   0x005fa01e..0x005fa055  __iar_zero_init3 ABI adapter (body is the shared
 *                           g2_zero_init3, runtime/iar-runtime/runtime.c)
 *
 * __cmain: __low_level_init; if it returns nonzero, __iar_data_init3; then
 * main 0x5ce01e and exit 0x5e42dc with main's result. The two nop.w slots
 * (0x5e42a0, 0x5e42a6) are unused IAR linker call sites, and r0 = 0 before
 * main is the argc IAR passes. main_5ce01e is defined void and never returns
 * (FreeRTOS scheduler start, then `for (;;)`), so status 0 is passed here.
 *
 * __iar_data_init3 walks the linker region table ROM 0x75d3c8..0x75d40f
 * (IAR Region$$Table$$Base / Region$$Table$$Limit). Each row starts with a
 * handler offset relative to the row itself (Thumb bit set); the handler
 * receives the word after it and returns the next row. Rows decoded from the
 * image:
 *   0x75d3c8 -> 0x5fa01f zero init: {0x70af0 @ 0x20004558},
 *                         {0x240fd4 @ 0x2013be70}, 0 terminator
 *   0x75d3e0, 0x75d3f0, 0x75d400 -> 0x43a11f LZ77 copy
 *                         (iar_lz77_init_single3_43a11e, p-01-iar-runtime)
 * No g2/src unit defines the table itself yet; its bounds are referenced by
 * provisional names below.
 *
 * Profile g2-apollo-main-2. */
#include <stdint.h>

typedef const uint32_t *(*g2_iar_init_handler_t)(const uint32_t *record);

/* ROM 0x75d3c8 / 0x75d410: region table bounds (no definition in g2/src). */
extern const uint32_t iar_region_table_base_75d3c8[];
extern const uint32_t iar_region_table_limit_75d410[];

/* runtime/iar-runtime/runtime.c: zero-init body with r9 passed explicitly. */
extern const uint32_t *g2_zero_init3(const uint32_t *record, uint32_t static_base);

/* system/a-67-main-config/main_config.c (stock 0x5ce01e). */
extern void main_5ce01e(void);
/* runtime/C3-startup/iar_exit.c (stock 0x5e42dc). */
extern void iar_exit_5e42dc(int32_t status) __attribute__((noreturn));

int32_t low_level_init_5e4228(void);
void iar_data_init3_5e42b4(void);
const uint32_t *iar_zero_init3_5fa01e(const uint32_t *record);
void iar_cmain_5e4294(void) __attribute__((noreturn));

/* Stock 0x005e4228 (__low_level_init): VTOR = main vector table 0x438000. */
int32_t low_level_init_5e4228(void)
{
    *(volatile uint32_t *)(uintptr_t)0xe000ed08u = 0x00438000u;
    return 1;
}

/* Stock 0x005fa01e (__iar_zero_init3): table handler ABI is r0 = record and
 * an implicit r9 static base; the shared body takes the base explicitly. */
const uint32_t *iar_zero_init3_5fa01e(const uint32_t *record)
{
    uint32_t static_base;

    __asm volatile("mov %0, r9" : "=r"(static_base));
    return g2_zero_init3(record, static_base);
}

/* Stock 0x005e42b4 (__iar_data_init3) */
void iar_data_init3_5e42b4(void)
{
    const uint32_t *row = iar_region_table_base_75d3c8;

    while (row != iar_region_table_limit_75d410) {
        g2_iar_init_handler_t handler =
            (g2_iar_init_handler_t)((uintptr_t)row + *row);
        row = handler(row + 1);
    }
}

/* Stock 0x005e4294 (__cmain) */
void iar_cmain_5e4294(void)
{
    if (low_level_init_5e4228() != 0)
        iar_data_init3_5e42b4();
    main_5ce01e();
    iar_exit_5e42dc(0);
}
