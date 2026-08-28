/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include "runtime_touch_leaf_primitives.h"

uint32_t touch_host_leaf_passthrough(uint32_t entry, uint32_t value)
{
    switch (entry) {
    case 0x1226u: return open_cfw_touch_leaf_1226_passthrough(value);
    case 0x1236u: return open_cfw_touch_leaf_1236_passthrough(value);
    case 0x12A4u: return open_cfw_touch_leaf_12a4_passthrough(value);
    case 0x1366u: return open_cfw_touch_leaf_1366_passthrough(value);
    case 0x1370u: return open_cfw_touch_leaf_1370_passthrough(value);
    case 0x1418u: return open_cfw_touch_leaf_1418_passthrough(value);
    default: return 0u;
    }
}

uint32_t touch_host_leaf_constant(
    uint32_t entry, uint32_t r0, uint32_t r1, uint32_t r2, uint32_t r3)
{
    switch (entry) {
    case 0x1480u: return open_cfw_touch_leaf_1480_constant_1(r0, r1, r2, r3);
    case 0x1484u: return open_cfw_touch_leaf_1484_constant_128(r0, r1, r2, r3);
    case 0x1488u: return open_cfw_touch_leaf_1488_constant_128(r0, r1, r2, r3);
    case 0x148Cu: return open_cfw_touch_leaf_148c_constant_0(r0, r1, r2, r3);
    case 0x14AAu: return open_cfw_touch_leaf_14aa_constant_0(r0, r1, r2, r3);
    case 0x1AB4u: return open_cfw_touch_leaf_1ab4_constant_0(r0, r1, r2, r3);
    default: return 0xFFFFFFFFu;
    }
}
