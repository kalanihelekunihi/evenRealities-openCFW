/* SPDX-License-Identifier: MIT
 * Source-defined callback records for the locked 0x433440 table.
 * The callback order and priorities are reconstructed data; the pointers are
 * relocations to source functions, never copied stock code addresses.
 */
#include <stdint.h>

#include "../allocator/allocator.h"
#include "../init-table/init_table.h"
#include "initializer_callbacks.h"

__attribute__((section(".boot_initializer_callbacks"), used, aligned(4)))
const struct opencfw_boot_init_record opencfw_boot_initializer_callback_records[4] = {
    {(uintptr_t)opencfw_boot_init_callback_platform_sequence, 1u},
    {(uintptr_t)opencfw_boot_init_callback_services, 1u},
    {(uintptr_t)opencfw_boot_init_callback_redirect, 25u},
    {(uintptr_t)opencfw_boot_allocator_init, 26u},
};

/* Source-defined 4x16-byte platform-context config records. Values are the
 * authenticated scalar data consumed through pointers in scatter RAM. */
__attribute__((section(".boot_context_config"), used, aligned(4)))
const uint32_t opencfw_boot_context_config_records[16] = {
    0x19u, 0x1au, 0x4200u, 0x4200u,
    0x22u, 0x23u, 0x4200u, 0x4200u,
    0x2fu, 0x30u, 0x4200u, 0x4200u,
    0x16u, 0x17u, 0x4200u, 0x4200u,
};
