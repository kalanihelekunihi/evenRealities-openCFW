/* SPDX-License-Identifier: MIT
 * Shell line-input wrapper 0x10005e60 and bounded string copy
 * 0x100064dc. The latter returns full source length even when truncated.
 */
#include <stdint.h>

extern int32_t gx8002_uart_stage2_read_line_core_5d1c(
    const char *prompt, char *buffer, uint32_t mode);

int32_t gx8002_uart_stage2_read_line_5e60(const char *prompt)
{
    char *buffer = (char *)(uintptr_t)UINT32_C(0x2000a158);
    buffer[0] = '\0';
    return gx8002_uart_stage2_read_line_core_5d1c(prompt, buffer, 0u);
}

uint32_t gx8002_uart_stage2_copy_bounded_64dc(
    char *destination, const char *source, uint32_t capacity)
{
    uint32_t length = 0;
    while (source[length] != '\0') ++length;
    if (capacity != 0u) {
        uint32_t copied = length < capacity ? length : capacity - 1u;
        for (uint32_t i = 0; i < copied; ++i)
            destination[i] = source[i];
        destination[copied] = '\0';
    }
    return length;
}
