/* SPDX-License-Identifier: MIT
 * Native unsigned parser at stock 0x1000654c. The referenced character
 * class table at 0x10008a88 recognizes ASCII digits and A-F/a-f for
 * numeric input; its high-byte entries do not carry numeric bits.
 * This is the stock parser's control flow, including wraparound math.
 */
#include <stdint.h>

uint32_t gx8002_uart_stage2_parse_unsigned_654c(
    const char *text, char **end, uint32_t base)
{
    const unsigned char *p = (const unsigned char *)text;
    uint32_t value = 0;
    if (*p == (unsigned char)'0') {
        if (p[1] == (unsigned char)'x' ||
            p[1] == (unsigned char)'X') {
            base = 16u;
            p += 2;
        } else if (base == 0u) {
            base = 8u;
        }
    } else if (base == 0u) {
        base = 10u;
    }
    for (;;) {
        unsigned char c = *p;
        uint32_t digit;
        if (c >= (unsigned char)'0' && c <= (unsigned char)'9') {
            digit = (uint32_t)c - (uint32_t)'0';
        } else if (c >= (unsigned char)'A' && c <= (unsigned char)'F') {
            digit = (uint32_t)c + 32u - (uint32_t)'a' + 10u;
        } else if (c >= (unsigned char)'a' && c <= (unsigned char)'f') {
            digit = (uint32_t)c - (uint32_t)'a' + 10u;
        } else if (base > 256u) {
            digit = 256u;
        } else {
            break;
        }
        if (digit >= base) break;
        value = value * base + digit;
        ++p;
    }
    if (end != 0) *end = (char *)p;
    return value;
}
