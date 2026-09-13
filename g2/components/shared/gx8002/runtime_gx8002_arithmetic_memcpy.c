/* SPDX-License-Identifier: MIT */
/* Internal libgcc structure copy. Source and destination must not overlap.
 * This ordinary RAM copy has no MMIO or ordered word-access contract. */
#include <stddef.h>
void *open_cfw_gx8002_arithmetic_memcpy(void *destination,
                                      const void *source, size_t count)
{
    unsigned char *out = destination;
    const unsigned char *in = source;
    for (size_t i = 0; i < count; ++i)
        out[i] = in[i];
    return destination;
}
