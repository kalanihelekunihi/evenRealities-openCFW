/* Native image-B 0x10004880..0x100048c4, the external-interrupt entry
 * (gx_irq_handler, NationalChip lvp_kws drivers_lib/intc/vic.o, compiled
 * from C). csky-abiv2-gcc 6.3's isr attribute emits the stock entry and exit
 * exactly: nie, ipush, stm r18-r31, fstms fr0-fr7, push r15 ... fldms,
 * ldm, ipop, nir. The active line (VIC 0xe000ec00 - 32) indexes the
 * {callback, argument} descriptor table.
 */
#include <stdint.h>

extern volatile uint32_t gx8002_image_b_irq_descriptors_200173a8[];

__attribute__((isr, used)) void gx8002_image_b_generic_irq_10004880(void)
{
    const uint32_t line =
        (*(const volatile uint32_t *)(uintptr_t)UINT32_C(0xe000ec00) & 511u) - 32u;
    const uint32_t callback = gx8002_image_b_irq_descriptors_200173a8[line * 2u];
    if (callback != 0u)
        ((void (*)(uint32_t, uint32_t))(uintptr_t)callback)(
            line, gx8002_image_b_irq_descriptors_200173a8[line * 2u + 1u]);
}
