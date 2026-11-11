/* SPDX-License-Identifier: MIT
 * UART stage-1 _clk_get_module_frequence (clk_priv.h, NationalChip lvp_kws
 * 8bf9ee5c) at stock 0x10000ea0 (0x10000eb8 is a shared return inside it).
 * Returns the module clock in Hz, 0 when it has none, -1 for a PLL input
 * outside the known ranges. All arithmetic is unsigned 32-bit as in the
 * stock body; the DTO scaling uses the 64-bit product >> 25.
 */
#include <stdint.h>
#include <stddef.h>
#include "uart_stage1_pmu.h"

#define PLL_REG(offset) (*(volatile uint32_t *)(uintptr_t)(UINT32_C(0xa0005000) + (offset)))

/* Stock 0x10000EA0 */
int32_t gx8002_uart_stage1_pmu_clock_rate(uint32_t selector)
{
    uint32_t module = selector;
    if (selector == 20u || selector == 21u)
        module = 19;                          /* I2C0/1 -> I2C0_I2C1 */
    else if (selector == 17u || selector == 18u)
        module = 16;                          /* UART0/1 -> UART0_UART1 */
    else if (selector == 23u || selector == 24u)
        module = 22;                          /* TIMER/WDT -> TIMER_WDT */
    else if (selector == 25u)
        module = 10;                          /* DMA -> SCPU */
    else if (selector == 7u || selector == 8u)
        return 0;                             /* AUDIO_IN_ADC/PDM */

    struct stage1_pmu_view view;
    if (gx8002_uart_stage1_pmu_fill_desc(module, &view) != 0)
        return 0;
    const volatile struct stage1_pmu_entry *const entry =
        (const volatile struct stage1_pmu_entry *)view.entry;
    const int32_t offs = (int8_t)entry->gate_bit;
    if (offs == -1)
        return 0;

    /* RTC, PMU, SRAM, OSC_REF also have a 32K select one bit up. */
    const int32_t offs_w =
        module < 10u && ((UINT32_C(1) << module) & UINT32_C(0x243)) ? offs + 1 : 0;
    const uint32_t source = *(const volatile uint32_t *)(uintptr_t)UINT32_C(0xa001008c);

    uint32_t fre = 0;
    if (offs_w != 0 && gx8002_uart_stage1_bit(*view.status, offs_w) == 1u) {
        fre = 32000;
    } else if (gx8002_uart_stage1_bit(*view.status, offs) == 0u) {
        fre = (source & (UINT32_C(1) << 18)) == 0u ? 12288000u : 1024000u;
        if (module >= 10u || module == 6u || module == 9u || module == 2u)
            return (int32_t)fre;
    } else if (gx8002_uart_stage1_bit(*view.status, offs) == 1u) {
        if ((source & 1u) == 0u) {
            fre = 24576000u;
        } else {
            const uint32_t div_in = (PLL_REG(0x1c) & 0x3fu) + 1u;
            const uint32_t fb_low = PLL_REG(0x20);
            const uint32_t fb_high = PLL_REG(0x24);
            const uint32_t div_out_field = PLL_REG(0x28);
            const uint32_t subband = (PLL_REG(0x30) >> 4) & 3u;
            const uint32_t div_fb = (fb_low | ((fb_high << 8) & 0x1f00u)) + 1u;
            /* Named table (not a switch, which GCC turns into an unnamed
             * .rodata.CSWTCH table placed outside STAGE1). */
            static const uint32_t gx8002_uart_stage1_fvco[4] = {
                61440000u, 73728000u, 86016000u, 98304000u,
            };
            const uint32_t fvco = gx8002_uart_stage1_fvco[subband];
            uint32_t fin = fvco * div_in / div_fb;
            if (fin - 16000u < 32000u)
                fin = 32000u;
            else if (fin - 512000u < 1024000u)
                fin = 1024000u;
            else if (fin - 153600u < 2918400u)
                fin = 2048000u;
            else
                return -1;
            fre = fin / div_in * div_fb / (((div_out_field & 7u) + 1u) * 2u);
        }
        const uint8_t *const dto = entry->special;     /* __module_get_dto */
        if (dto != NULL) {
            const uint32_t word = *(volatile uint32_t *)((uintptr_t)view.base + dto[0]);
            if ((word & UINT32_C(0x08000000)) == 0u)
                fre = (uint32_t)(((uint64_t)(word & UINT32_C(0x01ffffff)) * fre) >> 25);
        }
    }

    const struct stage1_pmu_aux_field *const field = entry->aux;  /* __module_get_div */
    if (field == NULL)
        return (int32_t)fre;
    const uint32_t div = (*(volatile uint32_t *)((uintptr_t)view.base + field->register_offset)
                          >> field->shift) & field->mask;
    return div == 0u ? (int32_t)fre : (int32_t)(fre / (div + 1u));
}
