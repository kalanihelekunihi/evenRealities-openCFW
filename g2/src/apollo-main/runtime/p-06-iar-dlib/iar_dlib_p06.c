/* IAR DLIB runtime helpers (proprietary library; independent C reconstruction
 * from stock behaviour, no IAR source text). Native 0x481818..0x481836 and
 * 0x482684..0x4826b2 of firmware 2.2.6.10. */
#include <stddef.h>
#include <stdint.h>

/* strchr, native 0x481818..0x48182e. The search byte is truncated to 8 bits;
 * searching for 0 returns the terminator address. */
char *strchr_481818(const char *s, int32_t c)
{
    uint8_t wanted = (uint8_t)c;
    uint8_t ch = (uint8_t)*s;
    while (ch != wanted && ch != 0u)
        ch = (uint8_t)*++s;
    return ch == wanted ? (char *)(uintptr_t)s : NULL;
}

/* ASCII case fold used by the formatter's integer path to test for 'x'/'X',
 * native 0x481830..0x481836 (single caller 0x482518). */
uint32_t iar_ascii_fold_lower_481830(uint32_t c)
{
    return c | 0x20u;
}

/* Formatter output record (layout shared with format_record in
 * system/log/full-formatter/full-formatter-native/record.h). */
typedef struct {
    uint32_t value_low;      /* +0x00 */
    uint32_t value_high;     /* +0x04 */
    void *context;           /* +0x08: output state threaded through the put callback */
    uint32_t words[8];       /* +0x0c..+0x2b */
    uint32_t count;          /* +0x2c: characters emitted */
} iar_format_output_t;
_Static_assert(offsetof(iar_format_output_t, count) == 0x2cu, "stock record layout");

typedef void *(*iar_format_put_t)(void *context, uint32_t ch);

/* Emits n bytes through the put callback, native 0x482684..0x4826b2 (called by
 * the formatter core 0x481836). A NULL context from the callback aborts with -1. */
int32_t iar_format_put_bytes_482684(iar_format_put_t put, iar_format_output_t *out,
                                    const uint8_t *bytes, uint32_t n)
{
    while (n != 0u) {
        out->context = put(out->context, *bytes++);
        if (out->context == NULL)
            return -1;
        out->count++;
        n--;
    }
    return 0;
}
