/* Stock image-B 0x100035a0..0x100035bd: apply one 8-byte board clock
 * record to the a001008c register. Native reads record word at +0 and byte
 * at +4, rotates -2 left by the word, then merges the shifted byte.
 * Exact record contents/producer remain separate source-data obligations.
 */
#include <stdint.h>

void gx8002_image_b_clock_register_apply_100035a0(const void *record)
{
    const volatile uint8_t *const bytes = (const volatile uint8_t *)record;
    const uint32_t shift = (*(const volatile uint32_t *)bytes) & 31u;
    volatile uint32_t *const reg = (volatile uint32_t *)(uintptr_t)0xa001008cu;
    const uint32_t current = *reg;
    const uint32_t value = bytes[4];
    const uint32_t clear = (0xfffffffeu << shift) |
                           (0xfffffffeu >> ((32u - shift) & 31u));
    *reg = (current & clear) | (value << shift);
}
