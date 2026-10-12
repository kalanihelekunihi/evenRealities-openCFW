/* Stock image-B 0x1000ada6 unconditionally reads a word through r9, the
 * caller's input-pointer argument. When that pointer is null, this is an
 * actual address-zero load. Keep the hardware read instruction rather than
 * substituting a C null dereference or a manufactured value. */
#include <stdint.h>

uint32_t gx8002_image_b_native_word_at_zero_1000ada6(void)
{
    uint32_t value;
    __asm__ volatile ("movi %0, 0\n\tld.w %0, (%0, 0)"
                      : "=&r"(value) : : "memory");
    return value;
}
