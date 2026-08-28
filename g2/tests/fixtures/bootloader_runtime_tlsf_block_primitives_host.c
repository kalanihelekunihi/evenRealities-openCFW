/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include "../../components/bootloader/core_overlay/runtime_tlsf_block_primitives_4169fc.c"

uint32_t open_cfw_test_tlsf_block_word(const void *block, uint32_t index)
{
    return ((const uint32_t *)block)[index];
}
