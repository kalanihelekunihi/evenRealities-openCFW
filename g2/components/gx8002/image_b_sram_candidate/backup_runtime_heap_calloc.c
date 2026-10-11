/* SPDX-License-Identifier: Apache-2.0
 * Image-B 0x10009c0c RT-Thread calloc: pinned rt_mem.c, native call order.
 */
#include <stdint.h>

extern void *gx8002_image_b_heap_alloc_10009ab8(uint32_t bytes);
extern void gx8002_image_b_zero_100113c4(
    void *destination, uint32_t byte_value, uint32_t bytes);

void *gx8002_image_b_heap_calloc_10009c0c(uint32_t count, uint32_t size)
{
    uint32_t bytes = count * size;
    void *result = gx8002_image_b_heap_alloc_10009ab8(bytes);
    if (result != 0)
        gx8002_image_b_zero_100113c4(result, 0u, bytes);
    return result;
}
