/* SPDX-License-Identifier: MIT
 * NOR command caller binds to stock Thumb 0x41fadd mode publisher.
 */
#include <stdint.h>

__attribute__((naked)) uint32_t opencfw_publish_device_mode(uint32_t module,
    uint8_t mode)
{
    __asm__ volatile("b.w opencfw_publish_mspi_mode");
}
