/* Diagnostic print entry. Formatter, output sink and shared buffer are lower. */
#include <stdint.h>
#include <stdarg.h>

extern volatile uint32_t g2_flashdb_print_sink;
extern unsigned char g2_flashdb_print_buffer[];
extern int32_t g2_flashdb_vformat(uint32_t buffer, uint32_t format,
                                  uint32_t arguments);

int32_t g2_flashdb_print(const char *format, ...)
{
    if (g2_flashdb_print_sink == 0u) return 0;
    va_list arguments;
    va_start(arguments, format);
    int32_t result = g2_flashdb_vformat(
        (uint32_t)(uintptr_t)g2_flashdb_print_buffer,
        (uint32_t)(uintptr_t)format,
        (uint32_t)(uintptr_t)*(const uint32_t * const *)(const void *)&arguments);
    va_end(arguments);
    const uint32_t sink = g2_flashdb_print_sink;
    void (*output)(uint32_t) = (void (*)(uint32_t))(uintptr_t)sink;
    output((uint32_t)(uintptr_t)g2_flashdb_print_buffer);
    return result;
}
