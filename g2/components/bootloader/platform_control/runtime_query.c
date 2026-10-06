/* SPDX-License-Identifier: MIT. Reconstructed query table/helpers for
 * stock 0x41b8f8 and 0x41c2d8. Descriptor scalars are read-only data. */
#include "runtime_query.h"
#include <stddef.h>

typedef struct {
    uint32_t command_register;
    uint32_t command_mask;
    uint32_t status_register;
    uint32_t status_mask;
} query_descriptor_t;

static const query_descriptor_t query_descriptors[34] = {
    {0x40021004u, 0x00000001u, 0x40021008u, 0x30000001u},
    {0x40021004u, 0x10000000u, 0x40021008u, 0x30000001u},
    {0x40021004u, 0x20000000u, 0x40021008u, 0x30000001u},
    {0x40021004u, 0x00000002u, 0x40021008u, 0x0000001eu},
    {0x40021004u, 0x00000004u, 0x40021008u, 0x0000001eu},
    {0x40021004u, 0x00000008u, 0x40021008u, 0x0000001eu},
    {0x40021004u, 0x00000010u, 0x40021008u, 0x0000001eu},
    {0x40021004u, 0x00000020u, 0x40021008u, 0x000001e0u},
    {0x40021004u, 0x00000040u, 0x40021008u, 0x000001e0u},
    {0x40021004u, 0x00000080u, 0x40021008u, 0x000001e0u},
    {0x40021004u, 0x00000100u, 0x40021008u, 0x000001e0u},
    {0x40021004u, 0x00000200u, 0x40021008u, 0x00001e00u},
    {0x40021004u, 0x00000400u, 0x40021008u, 0x00001e00u},
    {0x40021004u, 0x00000800u, 0x40021008u, 0x00001e00u},
    {0x40021004u, 0x00001000u, 0x40021008u, 0x00001e00u},
    {0x40021004u, 0x00002000u, 0x40021008u, 0x00002000u},
    {0x40021004u, 0x00004000u, 0x40021008u, 0x00004000u},
    {0x40021004u, 0x00008000u, 0x40021008u, 0x00008000u},
    {0x40021004u, 0x00010000u, 0x40021008u, 0x00010000u},
    {0x40021004u, 0x00020000u, 0x40021008u, 0x00020000u},
    {0x40021004u, 0x00040000u, 0x40021008u, 0x00040000u},
    {0x40021004u, 0x00080000u, 0x40021008u, 0x00080000u},
    {0x40021004u, 0x00100000u, 0x40021008u, 0x00100000u},
    {0x40021004u, 0x00200000u, 0x40021008u, 0x00200000u},
    {0x40021004u, 0x00400000u, 0x40021008u, 0x00400000u},
    {0x40021004u, 0x00800000u, 0x40021008u, 0x00800000u},
    {0x40021004u, 0x01000000u, 0x40021008u, 0x01000000u},
    {0x40021004u, 0x02000000u, 0x40021008u, 0x02000000u},
    {0x40021004u, 0x04000000u, 0x40021008u, 0x04000000u},
    {0x40021004u, 0x08000000u, 0x40021008u, 0x08000000u},
    {0x4002100cu, 0x00000004u, 0x40021010u, 0x00000004u},
    {0x4002100cu, 0x00000040u, 0x40021010u, 0x000000c0u},
    {0x4002100cu, 0x00000080u, 0x40021010u, 0x000000c0u},
    {0x4002100cu, 0x00000400u, 0x40021010u, 0x00000400u}
};

_Static_assert(sizeof(query_descriptor_t) == 16u,
               "stock query descriptor is four 32-bit words");
_Static_assert(sizeof(query_descriptors) / sizeof(query_descriptors[0]) == 34u,
               "stock query descriptor table has 34 selectors");

__attribute__((noinline))
uint32_t opencfw_boot_control_query_descriptor_copy(
    uint32_t *destination, uint32_t selector)
{
    if (destination == NULL || selector >= 34u)
        return 6u;

    const uint32_t *const source =
        (const uint32_t *)(const void *)&query_descriptors[selector];
    for (uint32_t word = 0u; word != 4u; ++word)
        destination[word] = source[word];
    return 0u;
}

uint32_t opencfw_boot_control_query(uint32_t selector, uint8_t *result)
{
    if (result == NULL)
        return 6u;
    *result = 0u;

    uint32_t descriptor[4];
    const uint32_t status = opencfw_boot_control_query_descriptor_copy(
        descriptor, (uint8_t)selector);
    if (status != 0u)
        return status;

    const volatile uint32_t *const status_word =
        (const volatile uint32_t *)(uintptr_t)descriptor[2];
    *result = ((*status_word & descriptor[3]) != 0u) ? 1u : 0u;
    return 0u;
}
