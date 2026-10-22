/* IAR DLIB (EWARM 9.x) runtime leaves, firmware 2.2.6.10. IAR DLIB has no
 * public source; these are freestanding equivalents written from the
 * disassembly.
 *   0x4d15e8..0x4d15f9  scanf "get one more character" helper (no field limit)
 *   0x4d40e0..0x4d4137  memchr (hand-written word-at-a-time scan)
 *   0x4d43a4..0x4d43a7  current ctype locale table getter -> RAM 0x200044c0
 *   0x4d43a8..0x4d43ab  current lconv getter              -> RAM 0x20004488
 * The neighbouring scanf helpers g2_getn (0x4d15fa) and g2_ungetn (0x4d161c)
 * are in runtime/iar-runtime/runtime.c. */
#include <stdint.h>
#include <stddef.h>

typedef int32_t (*iar_scan_get_t)(void *arg, int32_t ch, uint32_t advance); /* advance 0 = push back ch */

/* Prefix of the _Sft scan state used here (full 32-byte layout in
 * runtime/iar-dlib-gaps/iar_scanf.c). */
typedef struct {
    void *arg;     /* +0x00 callback context */
    uint32_t *ap;  /* +0x04 */
    const uint8_t *s; /* +0x08 */
    int32_t nchar; /* +0x0c characters consumed (%n) */
} iar_scan_state_t;

extern uint8_t audio_uart_ring_locale_dispatch_200044c0[]; /* RAM 0x200044c0, ctype table + callbacks */
extern uint8_t g2_iar_lconv_20004488[];                    /* RAM 0x20004488, +0x24 decimal point string */

/* Counts the character and fetches it; unlike g2_getn there is no width check. */
int32_t scan_get_counted_4d15e8(iar_scan_get_t get, iar_scan_state_t *px)
{
    px->nchar++;
    return get(px->arg, 0, 1u);
}

/* Stock aligns to a word, then tests four bytes at a time with the
 * (w - 0x01010101) & ~w & 0x80808080 zero-byte test on w ^ c*0x01010101 and
 * rescans the hit word bytewise; the result is the first matching byte. */
void *memchr_4d40e0(const void *s, int32_t c, uint32_t n)
{
    const uint8_t *p = (const uint8_t *)s;
    const uint8_t ch = (uint8_t)c;

    while (((uintptr_t)p & 3u) != 0u) {
        if (n-- == 0u)
            return NULL;
        if (*p++ == ch)
            return (void *)(uintptr_t)(p - 1);
    }
    if (n >= 8u) {
        const uint32_t pattern = ch * 0x01010101u;

        while (n >= 4u) {
            uint32_t w = *(const uint32_t *)(const void *)p ^ pattern;

            if (((w - 0x01010101u) & ~w & 0x80808080u) != 0u)
                break;
            p += 4;
            n -= 4u;
        }
    }
    for (; n != 0u; n--, p++)
        if (*p == ch)
            return (void *)(uintptr_t)p;
    return NULL;
}

void *iar_ctype_locale_4d43a4(void)
{
    return audio_uart_ring_locale_dispatch_200044c0;
}

const uint8_t *iar_locale_4d43a8(void)
{
    return g2_iar_lconv_20004488;
}
