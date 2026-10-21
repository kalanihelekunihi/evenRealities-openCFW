/* SPDX-License-Identifier: MIT
 * Image-B 0x10007f80: bind the three RAM protection records and selectors.
 * The pointed-to records are separate initialized-data obligations.
 */
#include <stdint.h>

void gx8002_image_b_flash_protection_initialize_10007f80(void)
{
    volatile uint32_t *const bindings =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20017644);
    bindings[0] = UINT32_C(0x20016dfc);
    bindings[1] = 5u;
    bindings[2] = UINT32_C(0x20016e24);
    bindings[3] = 7u;
    bindings[4] = UINT32_C(0x20016e5c);
    bindings[5] = 9u;
}
