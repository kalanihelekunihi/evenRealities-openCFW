/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_UART_STAGE1_PMU_H
#define OPENCFW_UART_STAGE1_PMU_H
#include <stdint.h>
#include <stddef.h>

struct stage1_pmu_aux_field {
    uint8_t register_offset;
    uint8_t shift;
    uint16_t mask;
};
_Static_assert(sizeof(struct stage1_pmu_aux_field) == 4, "PMU aux ABI");

struct stage1_pmu_entry {
    uint32_t selector;
    uint8_t power_bit;
    uint8_t status_bit;
    uint8_t gate_bit;
    uint8_t reserved;
    const struct stage1_pmu_aux_field *aux;
    const uint8_t *special;
};
_Static_assert(sizeof(struct stage1_pmu_entry) == 16, "PMU table ABI");

struct stage1_pmu_view {
    const volatile uint8_t *entry;
    volatile uint32_t *base;
    volatile uint32_t *status;
    volatile uint32_t *set;
    volatile uint32_t *clear;
    volatile uint32_t *enable;
};
_Static_assert(sizeof(struct stage1_pmu_view) == 24, "PMU view ABI");

int32_t gx8002_uart_stage1_pmu_fill_desc(uint32_t selector,
                                           struct stage1_pmu_view *out);

/* Stage-1 clock helpers (clk_priv.h policies, out of line). Entry fields map
 * to GX_CLOCK_MODULE_PARAM as power_bit = gate_high_offs, status_bit =
 * gate_all_offs, gate_bit = clk_offs (signed bytes, -1 = none), aux = div,
 * special = dto; the view's status/set/clear/enable words are clk_sel,
 * gate_val, gate_set and gate_clr. */
int32_t gx8002_uart_stage1_raila(uint32_t selector, uint32_t setting);   /* _clk_set_module */
void gx8002_uart_stage1_railb(uint32_t selector, uint32_t setting);      /* _clk_set_div */
void gx8002_uart_stage1_railc(uint32_t selector, uint32_t setting,
                              uint32_t mode);                            /* _clk_set_dto */
int32_t gx8002_uart_stage1_pmu_clock_rate(uint32_t selector);            /* _clk_get_module_frequence */

/* The 26-entry table 0x10000780 searches; also indexed by position. */
extern const struct stage1_pmu_entry g2_uart_stage1_pmu_table[26];  /* stock 0x20002018 */
#define STAGE1_CLOCK_TABLE \
    ((const volatile struct stage1_pmu_entry *)g2_uart_stage1_pmu_table)

/* C-SKY lsl/lsr give 0 for a shift count outside 0..31, which is how the
 * stock code treats the -1 ("none") offsets. */
static inline __attribute__((always_inline)) uint32_t
gx8002_uart_stage1_bit(uint32_t word, int32_t shift)
{
    return (uint32_t)shift < 32u ? (word >> shift) & 1u : 0u;
}

static inline __attribute__((always_inline)) uint32_t
gx8002_uart_stage1_mask(int32_t shift)
{
    return (uint32_t)shift < 32u ? UINT32_C(1) << shift : 0u;
}
int32_t gx8002_uart_stage2_pmu_fill_desc(uint32_t selector,
                                           struct stage1_pmu_view *out);
#endif
