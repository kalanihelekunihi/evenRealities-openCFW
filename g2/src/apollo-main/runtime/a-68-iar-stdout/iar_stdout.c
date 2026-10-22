/* IAR DLIB stdout path to SEGGER RTT.
 * putchar   native 0x5f9fa4..0x5f9fdb, literal pool 0x5f9fdc..0x5f9fe7 (IAR DLIB);
 * __write   native 0x5f9fe8..0x5f9ff7 (SEGGER_RTT_Syscalls_IAR.c retarget).
 * The IAR runtime and SEGGER syscall sources are not pinned; these are clean
 * freestanding equivalents. putchar is reached from the printf _Prout
 * callback 0x5fa008 (runtime/iar-dlib-gaps/iar_printf.c). */
#include <stdint.h>
#include <stddef.h>
#include "g2_segger_rtt.h" /* segger_rtt_write_5d9b28 = SEGGER_RTT_Write */

/* Two link-time weak references compared PC-relatively (pool words
 * 0xffa06024/0xffa06020 + 0x30/0x2e). Both are undefined in the stock link and
 * resolve to 0, so the direct __write path is always taken. */
extern const char g2_iar_putchar_select_a __attribute__((weak));
extern const char g2_iar_putchar_select_b __attribute__((weak));
/* Buffered fallback: fputc(c, stdout). Weak and undefined in the stock link,
 * where its BL was relaxed to NOP.W (0x5f9fb8), so c is returned unchanged. */
extern int g2_iar_fputc_weak(int c, void *stream) __attribute__((weak));
extern uint8_t g2_iar_stdout_200043f8[]; /* RAM 0x200043f8 IAR __iar_Stdout FILE */

/* __write(handle, buffer, size): handle ignored, always RTT up-channel 0;
 * returns size regardless of how many bytes RTT accepted. */
size_t segger_rtt_iar_write_5f9fe8(int handle, const unsigned char *buffer, size_t size)
{
    (void)handle;
    (void)segger_rtt_write_5d9b28(0u, buffer, size);
    return size;
}

/* putchar(c): returns the written byte, or -1 (EOF) on a short write. */
int putchar_5f9fa4(int c)
{
    unsigned char ch;

    if (&g2_iar_putchar_select_a != &g2_iar_putchar_select_b)
        return g2_iar_fputc_weak(c, g2_iar_stdout_200043f8);
    ch = (unsigned char)c;
    if (segger_rtt_iar_write_5f9fe8(1, &ch, 1u) == 1u)
        return ch;
    return -1;
}
