#include <stdint.h>

/* Fixed logger call of stock snprintf at 0x44b728: capacity 5, "%ld",
 * 32-bit signed value. Returns the full decimal length, writes at most four
 * characters and one terminator. This is not a general printf provider. */
uint32_t g2_log_candidate_timestamp_5(uint8_t *destination, uint32_t value)
{
    uint8_t reversed[10];
    uint32_t negative = (value & 0x80000000u) != 0u;
    uint32_t magnitude = negative ? 0u - value : value;
    uint32_t digits = 0;
    do {
        reversed[digits++] = (uint8_t)('0' + magnitude % 10u);
        magnitude /= 10u;
    } while (magnitude != 0u);
    uint32_t full_length = digits + negative;
    uint32_t cursor = 0;
    if (negative && cursor < 4u) destination[cursor++] = '-';
    while (digits != 0u && cursor < 4u)
        destination[cursor++] = reversed[--digits];
    destination[cursor] = 0u;
    return full_length;
}
