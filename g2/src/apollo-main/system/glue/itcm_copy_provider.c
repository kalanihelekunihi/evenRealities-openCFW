#include <stdint.h>

/* Original 0x48086a calls the authenticated startup-installed ITCM helper
 * at 0x48. Its selected contract copies a positive word count. The sole
 * current caller ignores this wrapper's return register. */
uint32_t platform_copy_words(uint32_t source, uint32_t *destination, uint32_t words) {
    const volatile uint32_t *read = (const volatile uint32_t *)(uintptr_t)source;
    volatile uint32_t *write = (volatile uint32_t *)destination;
    do {
        *write++ = *read++;
    } while (--words);
    return (uint32_t)(uintptr_t)read;
}
