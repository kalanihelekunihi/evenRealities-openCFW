/* Native optimized fill 0x33301c..0x333062, not presumed libc semantics.
 * Preserve byte alignment writes, 32-bit expansion of full R1, word stores,
 * trailing byte writes and unchanged incoming destination return.
 */
#include <stdint.h>
void *opencfw_em9305_memset(void *destination,uint32_t value,uint32_t bytes)
{
    uintptr_t current = (uintptr_t)destination;
    if ((current & 3u) != 0) {
        uint32_t alignment = 4u - (uint32_t)(current & 3u);
        while (alignment != 0) {
            if (bytes == 0) return destination;
            *(volatile uint8_t *)current = (uint8_t)value;
            current++;
            alignment--;
            bytes--;
        }
    }
    const uint32_t pair = (value << 8) | value;
    const uint32_t word = pair | (pair << 16);
    while (bytes >= 4) {
        bytes -= 4;
        *(volatile uint32_t *)current = word;
        current += 4;
    }
    while (bytes != 0) {
        *(volatile uint8_t *)current = (uint8_t)value;
        current++;
        bytes--;
    }
    return destination;
}
