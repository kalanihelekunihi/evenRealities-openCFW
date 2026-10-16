#include <stdint.h>
/* Authenticated native output contracts, not standard-library substitutes.
 * Padding decrements in unsigned arithmetic before the signed test: INT_MIN
 * deliberately wraps to INT_MAX. Callback results are ignored. */
typedef uint32_t (*r1_format_output)(uint32_t, uint32_t);
uint32_t r1_format_left_padding(uint32_t count, uint32_t flags,
                              uint32_t context, r1_format_output output)
{
    uint32_t emitted=0;
    if (flags & UINT32_C(0x2000))
        while ((int32_t)--count>=0) { output(32,context); ++emitted; }
    return emitted;
}
uint32_t r1_format_width_padding(uint32_t count, uint32_t flags,
                               uint32_t context, r1_format_output output)
{
    uint32_t emitted=0,byte=(flags & UINT32_C(0x10000)) ? 48 : 32;
    if (!(flags & UINT32_C(0x2000)))
        while ((int32_t)--count>=0) { output(byte,context); ++emitted; }
    return emitted;
}
/* Stores must stay in native order: destination may alias either context word.
 * Capacity is reloaded after the byte store, not cached before it. */
uint32_t r1_format_bounded_putc(uint32_t byte, volatile uint32_t *context)
{
    if (context[1]) {
        uint32_t destination=context[0];
        context[0]=destination+1u;
        *(volatile uint8_t *)(uintptr_t)destination=(uint8_t)byte;
        byte=context[1]-1u;
        context[1]=byte;
    }
    return byte;
}
