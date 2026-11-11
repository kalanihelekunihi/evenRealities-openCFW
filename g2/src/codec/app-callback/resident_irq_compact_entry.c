/* SPDX-License-Identifier: MIT
 * Image-A SRAM 0x10025574, the external-interrupt entry (gx_irq_handler in
 * NationalChip lvp_kws 8bf9ee5c drivers_lib/intc/vic.o, which is compiled
 * from C). With csky-abiv2-gcc 6.3 -mcpu=ck804ef -mhard-float the isr
 * attribute emits the stock entry and exit exactly: nie, ipush, stm
 * r18-r31, fstms fr0-fr7, push r15 ... fldms fr0-fr7, ldm r18-r31, ipop,
 * nir.
 *
 * The active vector number is read from VIC 0xe000ec00 (0xe000e100 +
 * 0xb00); IRQ n = vector - 32 indexes the {handler, data} table at
 * 0x20026ef4 that gx8002_resident_request_irq_2553c fills.
 */
#include <stdint.h>

struct gx8002_irq_slot {
    int32_t (*handler)(uint32_t irq, uint32_t data);
    uint32_t data;
};

/* Stock 0x10025574 (gx8002_irq_compact_entry) */
__attribute__((isr)) void gx8002_resident_irq_compact_entry_25574(void)
{
    const uint32_t irq =
        (*(const volatile uint32_t *)(uintptr_t)UINT32_C(0xe000ec00) & 511u) - 32u;
    const struct gx8002_irq_slot *const table =
        (const struct gx8002_irq_slot *)(uintptr_t)UINT32_C(0x20026ef4);
    int32_t (*const handler)(uint32_t, uint32_t) = table[irq].handler;
    if (handler != 0)
        (void)handler(irq, table[irq].data);
}
