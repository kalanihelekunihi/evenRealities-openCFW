/* SPDX-License-Identifier: MIT */
/* Exact gxNPU command-byte provider; no proprietary command content included. */
#include "runtime_gx8002_kws_command_boundary.h"
int32_t open_cfw_gx8002_kws_command_load(const open_cfw_gx8002_kws_command_ports *ports,
                                         uint8_t *destination, size_t capacity)
{
    static const uint8_t expected[32] = {
        0xc3U,0x8eU,0xd6U,0xd2U,0x2cU,0x7cU,0x0bU,0x61U,
        0x78U,0x28U,0x86U,0x78U,0x36U,0x4aU,0xcdU,0x10U,
        0xbdU,0x57U,0x30U,0xaaU,0x38U,0x2cU,0x1eU,0x19U,
        0xa3U,0x2fU,0x6cU,0xf2U,0xbdU,0x14U,0x30U,0xb9U};
    return open_cfw_gx8002_authenticated_segment_load(
        ports,destination,capacity,OPEN_CFW_GX8002_KWS_COMMAND_SIZE,expected);
}
