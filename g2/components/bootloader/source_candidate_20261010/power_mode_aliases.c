/* SPDX-License-Identifier: MIT
 * Post-b bringup mode-one and startup mode-two exact stock entries.
 */
#include <stdint.h>

__attribute__((naked)) uint32_t opencfw_bl_post_record_initialized(uint32_t index)
{
    __asm__ volatile("b.w opencfw_boot_control_mode_one");
}

__attribute__((naked)) int32_t opencfw_provider_41ba80(uint32_t mode)
{
    __asm__ volatile("b.w opencfw_boot_control_mode_two");
}
