/* SPDX-License-Identifier: MIT
 * Source form of the locked 0x41d90e indexed register read.
 * The register block meaning is not named here: stock supplies its base as
 * the literal 0x40010000 and accepts register IDs below 0xe0.
 */
#include "register_id.h"

#define REGISTER_BLOCK_BASE UINT32_C(0x40010000)
#define REGISTER_ID_LIMIT   UINT32_C(0xe0)

uint32_t opencfw_read_mspi_register_id(uint32_t register_id,
                                       uint32_t *out_value)
{
    if (register_id >= REGISTER_ID_LIMIT)
        return 5u;
    if (out_value == 0)
        return 6u;

    *out_value = *(volatile const uint32_t *)(uintptr_t)
        (REGISTER_BLOCK_BASE + register_id * sizeof(uint32_t));
    return 0u;
}
