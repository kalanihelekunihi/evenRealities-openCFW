#include <stdint.h>

/* Stock 0x44b63a..0x44b666: find a config token as a substring. Non-null
 * NUL-terminated input domain used by the logger. */
uint32_t g2_log_candidate_find_token(const uint8_t *haystack,
                                     const uint8_t *needle)
{
    if (needle[0] == 0u) return (uint32_t)(uintptr_t)haystack;
    for (const uint8_t *start = haystack; *start != 0u; start++) {
        const uint8_t *a = start, *b = needle;
        while (*a != 0u && *a == *b) { a++; b++; }
        if (*b == 0u) return (uint32_t)(uintptr_t)start;
    }
    return 0u;
}
