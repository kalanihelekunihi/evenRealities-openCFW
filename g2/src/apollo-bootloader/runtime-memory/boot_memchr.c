/* Native 0x004225d0 bounded byte search. The stock IAR implementation uses
 * aligned-word acceleration; this C body preserves the observable pointer
 * result on valid addressable input extents. */
#include <stddef.h>

void *memchr(const void *buffer, int value, size_t length)
{
    const unsigned char *bytes = (const unsigned char *)buffer;
    const unsigned char target = (unsigned char)value;
    for (size_t index = 0; index < length; ++index) {
        if (bytes[index] == target)
            return (void *)(bytes + index);
    }
    return NULL;
}
