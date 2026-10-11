/* SPDX-License-Identifier: MIT
 * Unseeded image-B native body 0x10004fac: enable memory controller and
 * wait for its status field to reach 2. The native loop has no timeout.
 */
#include <stdint.h>

void gx8002_image_b_memory_controller_enable_10004fac(void)
{
    volatile uint32_t *controller =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xb0000000);
    controller[0] = 0u;
    uint32_t control = controller[0];
    controller[0] = control | 1u;
    while ((controller[1] & 3u) != 2u) { }
}
