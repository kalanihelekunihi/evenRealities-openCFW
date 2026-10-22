/* IAR DLIB printf _Prout output callback, native 0x5fa008..0x5fa01d (followed
 * by __iar_zero_init3 at 0x5fa01e). Reconstructed 2026-10-21 (C3) from the
 * 2.2.6.10 disassembly; the IAR DLIB source is not pinned, so this is a clean
 * freestanding equivalent (compiles; byte identity not established).
 * printf_595a34 (runtime/iar-dlib-gaps/iar_printf.c) passes it to the general
 * formatter with context 1; a short putchar write turns the context into NULL,
 * which stops the formatter. */
#include <stdint.h>

extern int putchar_5f9fa4(int c); /* runtime/a-68-iar-stdout/iar_stdout.c */

void *prout_5fa008(void *context, uint32_t ch);

/* Stock 0x005FA008 (prout_5fa008) */
void *prout_5fa008(void *context, uint32_t ch)
{
    if ((uint32_t)putchar_5f9fa4((int)ch) != ch)
        context = (void *)0;
    return context;
}
