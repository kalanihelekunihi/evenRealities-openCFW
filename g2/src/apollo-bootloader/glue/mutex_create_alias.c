/* SPDX-License-Identifier: MIT
 * Initializer callback mutex creator binds to stock Thumb 0x416611.
 */
#include <stdint.h>

__attribute__((naked)) uintptr_t opencfw_bl_mutex_create(const void *attributes)
{
    __asm__ volatile("b.w opencfw_provider_416610");
}
