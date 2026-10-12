/* SPDX-License-Identifier: MIT
 * IAR DLIB thread-pointer leaf at locked bootloader address 0x422874.
 * The native body loads the literal 0x20000518 into r0 and returns.
 * This address denotes the bootloader's SRAM TLS anchor, not initialized
 * data owned by this translation unit.
 */
#include <stdint.h>

void *opencfw_boot_iar_thread_pointer_anchor(void)
{
    return (void *)(uintptr_t)UINT32_C(0x20000518);
}
