/* SPDX-License-Identifier: MIT
 * Connected clock leaf bodies from image-A SRAM native instructions.
 */
#include <stdint.h>
#include "resident_product_data.h"

extern void gx8002_resident_platform_gate_25080(uint32_t module,
                                                 uint32_t enabled);

/* 0x10024a10/0x10024a1c: trim gate then status bit at PMU +0x30. */
/* Stock 0x10024A10 (gx8002_trim_clock_enable) */
void gx8002_resident_trim_clock_enable_24a10(void)
{
    gx8002_resident_platform_gate_25080(9u, 1u);
}

/* Stock 0x10024A1C (gx8002_trim_state) */
uint32_t gx8002_resident_trim_state_24a1c(void)
{
    gx8002_resident_trim_clock_enable_24a10();
    volatile uint32_t *const pmu =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0010000);
    return pmu[0x30u / 4u] & 1u;
}

/* 0x10024a30: native ANDN and OR register-field update. */
/* Stock 0x10024A30 (__reg_set_val) */
void gx8002_resident_reg_set_val_24a30(volatile uint32_t *reg,
                                        uint32_t shift, uint32_t value,
                                        uint32_t mask)
{
    uint32_t amount = shift & 31u;
    uint32_t previous = *reg;
    *reg = (previous & ~(mask << amount)) | (value << amount);
}

struct gx8002_clock_source_record {
    uint32_t selector;
    uint32_t value;
};

/* 0x10024ae8: the entry's config points to packed
 * {register-byte-offset, shift, 16-bit mask} in source-owned module data.
 */
/* Stock 0x10024AE8 (__module_get_div.isra.1) */
uint32_t gx8002_resident_module_div_read_24ae8(
    const struct gx8002_module_entry *entry, volatile uint8_t *base)
{
    if (entry->config == 0) return 0u;
    const uint8_t *const packed = (const uint8_t *)entry->config;
    volatile uint32_t *const reg =
        (volatile uint32_t *)(void *)(base + packed[0]);
    uint32_t mask = (uint32_t)packed[2] | ((uint32_t)packed[3] << 8);
    uint32_t value = (*reg >> (packed[1] & 31u)) & mask;
    return value + (value != 0u);
}

/* 0x10024bcc reads only the low byte of the record's value word. */
/* Stock 0x10024BCC (gx8002_clock_source_select) */
void gx8002_resident_clock_source_select_24bcc(
    const struct gx8002_clock_source_record *record)
{
    volatile uint32_t *const status =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa001008c);
    gx8002_resident_reg_set_val_24a30(
        status, record->selector, (uint8_t)record->value, 1u);
}
