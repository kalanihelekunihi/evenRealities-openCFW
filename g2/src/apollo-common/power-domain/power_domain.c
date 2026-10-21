/* SPDX-License-Identifier: MIT */
/* Reconstructed 47ef18 lookup and 55ca72 domain selection; no power writes. */
#include "power_domain.h"
static const opencfw_power_domain_descriptor_t domains[34] = {
    { 0x40021004u, 0x00000001u, 0x40021008u, 0x30000001u },
    { 0x40021004u, 0x10000000u, 0x40021008u, 0x30000001u },
    { 0x40021004u, 0x20000000u, 0x40021008u, 0x30000001u },
    { 0x40021004u, 0x00000002u, 0x40021008u, 0x0000001eu },
    { 0x40021004u, 0x00000004u, 0x40021008u, 0x0000001eu },
    { 0x40021004u, 0x00000008u, 0x40021008u, 0x0000001eu },
    { 0x40021004u, 0x00000010u, 0x40021008u, 0x0000001eu },
    { 0x40021004u, 0x00000020u, 0x40021008u, 0x000001e0u },
    { 0x40021004u, 0x00000040u, 0x40021008u, 0x000001e0u },
    { 0x40021004u, 0x00000080u, 0x40021008u, 0x000001e0u },
    { 0x40021004u, 0x00000100u, 0x40021008u, 0x000001e0u },
    { 0x40021004u, 0x00000200u, 0x40021008u, 0x00001e00u },
    { 0x40021004u, 0x00000400u, 0x40021008u, 0x00001e00u },
    { 0x40021004u, 0x00000800u, 0x40021008u, 0x00001e00u },
    { 0x40021004u, 0x00001000u, 0x40021008u, 0x00001e00u },
    { 0x40021004u, 0x00002000u, 0x40021008u, 0x00002000u },
    { 0x40021004u, 0x00004000u, 0x40021008u, 0x00004000u },
    { 0x40021004u, 0x00008000u, 0x40021008u, 0x00008000u },
    { 0x40021004u, 0x00010000u, 0x40021008u, 0x00010000u },
    { 0x40021004u, 0x00020000u, 0x40021008u, 0x00020000u },
    { 0x40021004u, 0x00040000u, 0x40021008u, 0x00040000u },
    { 0x40021004u, 0x00080000u, 0x40021008u, 0x00080000u },
    { 0x40021004u, 0x00100000u, 0x40021008u, 0x00100000u },
    { 0x40021004u, 0x00200000u, 0x40021008u, 0x00200000u },
    { 0x40021004u, 0x00400000u, 0x40021008u, 0x00400000u },
    { 0x40021004u, 0x00800000u, 0x40021008u, 0x00800000u },
    { 0x40021004u, 0x01000000u, 0x40021008u, 0x01000000u },
    { 0x40021004u, 0x02000000u, 0x40021008u, 0x02000000u },
    { 0x40021004u, 0x04000000u, 0x40021008u, 0x04000000u },
    { 0x40021004u, 0x08000000u, 0x40021008u, 0x08000000u },
    { 0x4002100cu, 0x00000004u, 0x40021010u, 0x00000004u },
    { 0x4002100cu, 0x00000040u, 0x40021010u, 0x000000c0u },
    { 0x4002100cu, 0x00000080u, 0x40021010u, 0x000000c0u },
    { 0x4002100cu, 0x00000400u, 0x40021010u, 0x00000400u },
};
uint32_t opencfw_power_domain_descriptor(opencfw_power_domain_descriptor_t *out, uint32_t domain)
{
    if (!out || domain >= 34u) return 6;
    const opencfw_power_domain_descriptor_t *row = &domains[domain];
    out->enable_register = row->enable_register;
    out->enable_mask = row->enable_mask;
    out->status_register = row->status_register;
    out->status_mask = row->status_mask;
    return 0;
}
uint32_t opencfw_iom_domain_descriptor(opencfw_power_domain_descriptor_t *out, uint32_t module)
{
    return opencfw_power_domain_descriptor(out, (uint8_t)(module + 3u));
}
