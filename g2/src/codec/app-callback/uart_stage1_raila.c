/* SPDX-License-Identifier: MIT
 * UART stage-1 _clk_set_module (clk_priv.h, NationalChip lvp_kws 8bf9ee5c)
 * at stock 0x10000860. Written from the stock body, which differs from that
 * header in two places kept here: AUDIO_IN_PDM converts source / 6 (the
 * header has source - 5 and a two-bit field), and the field is one bit for
 * every module. Clock-select writes keep the whole source value << offset.
 */
#include <stdint.h>
#include "uart_stage1_pmu.h"

/* Stock 0x10000860 */
int32_t gx8002_uart_stage1_raila(uint32_t selector, uint32_t setting)
{
    int32_t source = (int32_t)setting;
    if (selector > 25u)
        return -1;
    if (source == 2) {                        /* MODULE_SOURCE_32K */
        if (selector >= 10u || ((UINT32_C(1) << selector) & UINT32_C(0x247)) == 0u)
            return -1;                        /* RTC, PMU, AUDIO_IN_SYS, SRAM, OSC_REF */
    } else if (source > 2) {
        if (selector == 7u)                   /* AUDIO_IN_ADC */
            source >>= 2;
        else if (selector == 8u)              /* AUDIO_IN_PDM */
            source /= 6;
        else
            return -1;
    }

    struct stage1_pmu_view view;
    if (gx8002_uart_stage1_pmu_fill_desc(selector, &view) != 0)
        return -1;
    const volatile struct stage1_pmu_entry *const entry =
        (const volatile struct stage1_pmu_entry *)view.entry;
    int32_t clk_offs = (int8_t)entry->gate_bit;
    if (clk_offs == -1)
        return -1;
    if (source == 2) {                        /* 32K: next bit, value 1 */
        clk_offs = (int8_t)(clk_offs + 1);
        source = 1;
    }
    if ((int32_t)gx8002_uart_stage1_bit(*view.status, clk_offs) == source)
        return 0;

    const uint32_t clk_mask = gx8002_uart_stage1_mask(clk_offs);
    const uint32_t clk_value = (uint32_t)source << (clk_offs & 31);
    uint32_t gate_all_enable;
    if (selector == 16u || selector == 19u || selector == 22u) {
        /* UART0_UART1, I2C0_I2C1, TIMER_WDT: either child enabled. As in
         * clk_priv.h the children are table positions selector + 1, + 2. */
        const volatile struct stage1_pmu_entry *const table = STAGE1_CLOCK_TABLE;
        const uint32_t gate = *view.set;
        gate_all_enable =
            !(gx8002_uart_stage1_bit(gate, (int8_t)table[selector + 1u].status_bit) &
              gx8002_uart_stage1_bit(gate, (int8_t)table[selector + 2u].status_bit));
    } else {
        gate_all_enable =
            !gx8002_uart_stage1_bit(*view.set, (int8_t)entry->status_bit);
    }
    if (!gate_all_enable) {
        *view.status = (*view.status & ~clk_mask) | clk_value;
        return 0;
    }

    const uint32_t gate_high = gx8002_uart_stage1_mask((int8_t)entry->power_bit);
    if (selector == 7u || selector == 8u) {
        *view.status = (*view.status & ~clk_mask) | clk_value;
        *view.clear = gate_high;
        /* Reopen the shared AUDIO_IN gate while ADC or PDM still runs. */
        const volatile struct stage1_pmu_entry *const table = STAGE1_CLOCK_TABLE;
        const uint32_t gate = *view.set;
        const uint32_t clk_sel = *view.status;
        if (!gx8002_uart_stage1_bit(clk_sel, (int8_t)table[2].gate_bit))
            return 0;
        if (!gx8002_uart_stage1_bit(gate, (int8_t)table[2].status_bit))
            return 0;
        const uint32_t pdm_off =
            gx8002_uart_stage1_bit(clk_sel, (int8_t)table[8].gate_bit) |
            gx8002_uart_stage1_bit(gate, (int8_t)table[8].status_bit);
        const uint32_t adc_off =
            gx8002_uart_stage1_bit(clk_sel, (int8_t)table[7].gate_bit) |
            gx8002_uart_stage1_bit(gate, (int8_t)table[7].status_bit);
        if (!pdm_off || !adc_off)
            *view.enable = gate_high;
    } else if (source == 1) {
        *view.enable = gate_high;
        *view.status = (*view.status & ~clk_mask) | clk_mask;
    } else {
        *view.status = (*view.status & ~clk_mask) | clk_value;
        *view.clear = gate_high;
    }
    return 0;
}
