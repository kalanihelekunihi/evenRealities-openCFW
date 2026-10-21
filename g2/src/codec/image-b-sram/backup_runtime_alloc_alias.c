/* SPDX-License-Identifier: Apache-2.0
 * Image-B 0x10009f2c is a native call-through entry into 0x10009ab8.
 */
#include <stdint.h>

extern void *gx8002_image_b_heap_alloc_10009ab8(uint32_t bytes);

void *gx8002_image_b_heap_alloc_alias_10009f2c(uint32_t bytes)
{
    return gx8002_image_b_heap_alloc_10009ab8(bytes);
}
