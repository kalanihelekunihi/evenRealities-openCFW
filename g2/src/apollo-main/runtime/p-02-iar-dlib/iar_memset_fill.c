/* IAR DLIB memset core, native 0x43c0ec..0x43c14a (firmware 2.2.6.10).
 *
 * __aeabi_memset (0x43c0e4, defined as audio_uart_buffer_zero in
 * drivers/peripherals/ring-init/ring_init.c) copies the fill byte into all four
 * bytes of r2 and falls through to this entry. __aeabi_memclr-style stubs (for
 * example 0x4d4ccc: movs r2,#0; b.w 0x43c0ec) branch here directly with an
 * already-replicated pattern.
 *
 * The fill runs backwards from dst+len: first up to 3 bytes to reach a word
 * boundary, then 16-byte blocks, then 8/4/2/1-byte tails. Stock returns the
 * final write pointer (== dst) in r0; no caller uses it. */
#include <stddef.h>
#include <stdint.h>

void iar_memset_fill_43c0ec(void *destination, uint32_t length, uint32_t pattern)
{
    uint8_t *end = (uint8_t *)destination + length;
    uint32_t misalign = (uint32_t)(uintptr_t)end & 3u;

    if (misalign != 0u) {
        if (length < misalign) {
            /* Only 1 or 2 bytes remain and they cannot reach a word boundary. */
            if (length != 0u)
                *--end = (uint8_t)pattern;
            if (length & 2u)
                *--end = (uint8_t)pattern;
            return;
        }
        length -= misalign;
        if (misalign & 1u)
            *--end = (uint8_t)pattern;
        if (misalign & 2u) {
            end -= 2;
            *(uint16_t *)(void *)end = (uint16_t)pattern;
        }
    }
    while (length >= 16u) {
        end -= 16;
        ((uint32_t *)(void *)end)[0] = pattern;
        ((uint32_t *)(void *)end)[1] = pattern;
        ((uint32_t *)(void *)end)[2] = pattern;
        ((uint32_t *)(void *)end)[3] = pattern;
        length -= 16u;
    }
    if (length & 8u) {
        end -= 8;
        ((uint32_t *)(void *)end)[0] = pattern;
        ((uint32_t *)(void *)end)[1] = pattern;
    }
    if (length & 4u) {
        end -= 4;
        *(uint32_t *)(void *)end = pattern;
    }
    if (length & 2u) {
        end -= 2;
        *(uint16_t *)(void *)end = (uint16_t)pattern;
    }
    if (length & 1u)
        *--end = (uint8_t)pattern;
}
