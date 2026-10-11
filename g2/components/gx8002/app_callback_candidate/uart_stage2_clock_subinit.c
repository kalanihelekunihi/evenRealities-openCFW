/* SPDX-License-Identifier: MIT
 * UART stage-2 clock/rail setup at stock 0x100052c4..0x1000542b.
 * The two 10-entry product tables in SRAM are inputs; their values are not
 * synthesized here. Native call order and revision branches are retained.
 */
#include <stdint.h>

extern void gx8002_uart_stage2_dispatch_4a48(uint32_t selector, uint32_t setting);
uint32_t gx8002_uart_stage2_clock_revision_4fd0(void)
{
    gx8002_uart_stage2_dispatch_4a48(9, 1);
    return *(const volatile uint32_t *)(uintptr_t)UINT32_C(0xa0010030) & 1u;
}

uint32_t gx8002_uart_stage2_clock_alternate_4fe8(void)
{
    gx8002_uart_stage2_dispatch_4a48(9, 1);
    return (*(const volatile uint32_t *)(uintptr_t)UINT32_C(0xa0010030) >> 1)
        & 1u;
}
extern void gx8002_uart_stage2_apply_table_entry_45ec(const volatile void *entry);
extern void gx8002_uart_stage2_rail_460c(uint32_t selector, uint32_t setting);
extern void gx8002_uart_stage2_gate_47dc(uint32_t selector, uint32_t setting);
extern void gx8002_uart_stage2_field_493c(uint32_t selector, uint32_t value,
                                            uint32_t mode);

void gx8002_uart_stage2_clock_subinit_52c4(void)
{
    const uintptr_t entries = gx8002_uart_stage2_clock_revision_4fd0() == 1u
        ? UINT32_C(0x2000949c) : UINT32_C(0x200094ec);
    for (uint32_t i = 0; i < 10u; ++i)
        gx8002_uart_stage2_apply_table_entry_45ec(
            (const volatile void *)(entries + i * 8u));

    gx8002_uart_stage2_rail_460c(0, 2);
    gx8002_uart_stage2_rail_460c(1, 0);
    gx8002_uart_stage2_rail_460c(9, 1);
    gx8002_uart_stage2_rail_460c(3, 0);
    gx8002_uart_stage2_rail_460c(4, 0);
    gx8002_uart_stage2_rail_460c(5, 0);
    gx8002_uart_stage2_rail_460c(6, 1);
    gx8002_uart_stage2_rail_460c(2, 0);
    gx8002_uart_stage2_rail_460c(7, 4);
    gx8002_uart_stage2_rail_460c(8, 6);
    gx8002_uart_stage2_field_493c(2, UINT32_C(0x1000000), 0);

    const uint32_t revision = gx8002_uart_stage2_clock_revision_4fd0();
    gx8002_uart_stage2_gate_47dc(6, revision == 1u ? 2u : 0u);
    gx8002_uart_stage2_gate_47dc(0, 4);
    gx8002_uart_stage2_gate_47dc(9, 2);
    gx8002_uart_stage2_rail_460c(10, 1);
    gx8002_uart_stage2_rail_460c(22, 0);
    gx8002_uart_stage2_rail_460c(11, 0);
    gx8002_uart_stage2_rail_460c(19, 1);
    gx8002_uart_stage2_rail_460c(12, 0);
    gx8002_uart_stage2_rail_460c(13, 1);
    gx8002_uart_stage2_rail_460c(14, 1);
    gx8002_uart_stage2_rail_460c(15, 0);

    const uint32_t last_revision = gx8002_uart_stage2_clock_revision_4fd0();
    gx8002_uart_stage2_rail_460c(16, last_revision == 1u ? 1u : 0u);
    gx8002_uart_stage2_field_493c(16, UINT32_C(0x1000000),
                                    last_revision == 1u ? 1u : 0u);
    gx8002_uart_stage2_field_493c(11, UINT32_C(0x1000000), 0);
    gx8002_uart_stage2_gate_47dc(10, 3);
    gx8002_uart_stage2_gate_47dc(19, 2);
    gx8002_uart_stage2_gate_47dc(14, 2);
    gx8002_uart_stage2_gate_47dc(12, 2);
    for (uint32_t i = 0; i < 26u; ++i)
        gx8002_uart_stage2_dispatch_4a48(i, 1);
}
