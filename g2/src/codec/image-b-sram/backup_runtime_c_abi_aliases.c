/* Compiler-generated C ABI calls at -Os use ordinary memcpy/memset names.
 * Bind them to already source-owned image-B copy/fill bodies. */
#include <stddef.h>
#include <stdint.h>

extern void gx8002_image_b_copy_10011344(void *, const void *, uint32_t);
extern void gx8002_image_b_zero_100113c4(void *, uint32_t, uint32_t);

void *memcpy(void *destination, const void *source, size_t bytes)
{
    gx8002_image_b_copy_10011344(destination, source, (uint32_t)bytes);
    return destination;
}

void *memset(void *destination, int value, size_t bytes)
{
    gx8002_image_b_zero_100113c4(destination, (uint32_t)(uint8_t)value,
                                 (uint32_t)bytes);
    return destination;
}
