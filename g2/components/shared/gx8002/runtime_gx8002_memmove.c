/* SPDX-License-Identifier: MIT */
#include <stddef.h>
#include <stdint.h>
extern void *open_cfw_gx8002_memcpy(void *, const void *, size_t);
void *open_cfw_gx8002_memmove(void *destination, const void *source, size_t count)
{
    unsigned char *out = destination;
    const unsigned char *in = source;
    if ((uintptr_t)out < (uintptr_t)in) {
        open_cfw_gx8002_memcpy(out, in, count);
    } else {
        while (count) {
            --count;
            out[count] = in[count];
        }
    }
    return destination;
}
