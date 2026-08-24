/* SPDX-License-Identifier: GPL-3.0-only */
/* Clean-room OPT3007 field map derived from TI SBOS864. */
#include <stddef.h>
#include <stdint.h>

#ifndef OPEN_CFW_SELECTOR
#define OPEN_CFW_SELECTOR 0
#endif

typedef struct {
    uint8_t msb;
    uint8_t lsb;
    uint8_t register_address;
} open_cfw_opt3007_field;

_Static_assert(sizeof(open_cfw_opt3007_field) == 3u, "OPT3007 field ABI");

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 1
__attribute__((used, noinline, aligned(4)))
void open_cfw_opt3007_assign_register_map(open_cfw_opt3007_field *fields)
{
    if (fields == NULL) {
        return;
    }

#define OPEN_CFW_OPT3007_FIELD(index, high, low, reg) do { \
    fields[(index)].msb = (uint8_t)(high); \
    fields[(index)].lsb = (uint8_t)(low); \
    fields[(index)].register_address = (uint8_t)(reg); \
} while (0)

    OPEN_CFW_OPT3007_FIELD(0u, 11u, 0u, 0x00u);
    OPEN_CFW_OPT3007_FIELD(1u, 15u, 12u, 0x00u);
    OPEN_CFW_OPT3007_FIELD(2u, 15u, 12u, 0x01u);
    OPEN_CFW_OPT3007_FIELD(3u, 11u, 11u, 0x01u);
    OPEN_CFW_OPT3007_FIELD(4u, 10u, 9u, 0x01u);
    OPEN_CFW_OPT3007_FIELD(5u, 8u, 8u, 0x01u);
    OPEN_CFW_OPT3007_FIELD(6u, 7u, 7u, 0x01u);
    OPEN_CFW_OPT3007_FIELD(7u, 6u, 6u, 0x01u);
    OPEN_CFW_OPT3007_FIELD(8u, 5u, 5u, 0x01u);
    OPEN_CFW_OPT3007_FIELD(9u, 4u, 4u, 0x01u);
    OPEN_CFW_OPT3007_FIELD(10u, 3u, 3u, 0x01u);
    OPEN_CFW_OPT3007_FIELD(11u, 2u, 2u, 0x01u);
    OPEN_CFW_OPT3007_FIELD(12u, 1u, 0u, 0x01u);
    OPEN_CFW_OPT3007_FIELD(13u, 15u, 12u, 0x02u);
    OPEN_CFW_OPT3007_FIELD(14u, 11u, 0u, 0x02u);
    OPEN_CFW_OPT3007_FIELD(15u, 15u, 12u, 0x03u);
    OPEN_CFW_OPT3007_FIELD(16u, 11u, 0u, 0x03u);
    OPEN_CFW_OPT3007_FIELD(17u, 15u, 0u, 0x7Eu);
    OPEN_CFW_OPT3007_FIELD(18u, 15u, 0u, 0x7Fu);

#undef OPEN_CFW_OPT3007_FIELD
}
#endif
