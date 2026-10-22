/* IAR DLIB printf, native 0x595a34..0x595a57 (PC-relative literal 0x595a58).
 * The original is IAR DLIB; this is a clean freestanding equivalent. It runs
 * the full formatter g2_iar_general_format (0x481836) with the _Prout callback
 * at 0x5fa008 (putchar 0x5f9fa4, NULL on a short write) and context 1.
 * Callers: 0x581478 and 0x5814c6. */
#include <stdint.h>
#include <stdarg.h>

typedef void *(*g2_format_put_t)(void *context, uint32_t ch);

extern int32_t g2_iar_general_format(g2_format_put_t put, void *context, const char *format,
                                     uint32_t **cursor, uint32_t mode); /* 0x481836 */
extern void *prout_5fa008(void *context, uint32_t ch);

int32_t printf_595a34(const char *format, ...)
{
    va_list ap;
    uint32_t *cursor;
    int32_t result;

    va_start(ap, format);
    _Static_assert(sizeof(va_list) == sizeof(uint32_t *), "ARM32 va_list is one pointer");
    __builtin_memcpy(&cursor, &ap, sizeof cursor);
    result = g2_iar_general_format(prout_5fa008, (void *)(uintptr_t)1u, format, &cursor, 0u);
    va_end(ap);
    return result;
}
