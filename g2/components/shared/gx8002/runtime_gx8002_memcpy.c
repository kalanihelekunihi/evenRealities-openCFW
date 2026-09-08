/* SPDX-License-Identifier: MIT */
/* Recovered RAM-copy routine at 0x10025738; target admission remains pending.
 * Non-overlapping source and destination are required. Volatile accesses
 * preserve the observed load/store order, not a general MMIO copy contract.
 * GCC may_alias permits word access to ordinary byte-addressable RAM objects.
 */
#include <stddef.h>
#include <stdint.h>

typedef uint32_t copy_word __attribute__((__may_alias__));

void *open_cfw_gx8002_memcpy(void *destination, const void *source, size_t size)
{
    volatile unsigned char *out = destination;
    const volatile unsigned char *in = source;
    if ((((uintptr_t)out | (uintptr_t)in) & 3U) == 0) {
        while (size >= 16) {
            const volatile copy_word *words_in = (const volatile copy_word *)in;
            volatile copy_word *words_out = (volatile copy_word *)out;
            uint32_t a = words_in[0];
            uint32_t b = words_in[1];
            uint32_t c = words_in[2];
            words_out[0] = a;
            uint32_t d = words_in[3];
            words_out[1] = b;
            words_out[2] = c;
            words_out[3] = d;
            in += 16;
            out += 16;
            size -= 16;
        }
        while (size >= 4) {
            *(volatile copy_word *)out = *(const volatile copy_word *)in;
            in += 4;
            out += 4;
            size -= 4;
        }
    }
    while (size != 0) {
        *out++ = *in++;
        --size;
    }
    return destination;
}
