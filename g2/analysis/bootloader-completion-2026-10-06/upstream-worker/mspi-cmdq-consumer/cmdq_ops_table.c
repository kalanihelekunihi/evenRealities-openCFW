/* Source-owned reconstruction of the 12×0x28-byte MMIO descriptor table at
 * 0x00430880. Values/row families are derived from the locked image bytes. */
#include <stddef.h>
#include <stdint.h>

struct cmdq_ops_data32 {
    uint32_t option_register;
    uint32_t buffer_register;
    uint32_t reset_register_a;
    uint32_t reset_register_b;
    uint32_t control_register;
    uint32_t control_mask;
    uint32_t auxiliary_register;
    uint32_t constant_one;
    uint32_t constant_four;
    uint32_t interface_tag;
};

_Static_assert(sizeof(struct cmdq_ops_data32) == 0x28u,
               "stock command-queue ops row size");

#define LEGACY_ROW(base_) { \
    (base_) + 0x228u, (base_) + 0x22cu, \
    (base_) + 0x240u, (base_) + 0x244u, \
    (base_) + 0x23cu, 0x8000u, (base_) + 0x230u, \
    1u, 4u, 2u \
}

#define MSPI_ROW(base_) { \
    (base_) + 0x2a0u, (base_) + 0x2a8u, \
    (base_) + 0x2c0u, (base_) + 0x2c4u, \
    (base_) + 0x2b8u, 0x4000u, (base_) + 0x2acu, \
    1u, 4u, 8u \
}

__attribute__((section(".cmdq_ops"), used, aligned(4)))
const struct cmdq_ops_data32 opencfw_cmdq_ops_table[12] = {
    LEGACY_ROW(0x40050000u),
    LEGACY_ROW(0x40051000u),
    LEGACY_ROW(0x40052000u),
    LEGACY_ROW(0x40053000u),
    LEGACY_ROW(0x40054000u),
    LEGACY_ROW(0x40055000u),
    LEGACY_ROW(0x40056000u),
    LEGACY_ROW(0x40057000u),
    MSPI_ROW(0x40060000u),
    MSPI_ROW(0x40061000u),
    MSPI_ROW(0x40062000u),
    MSPI_ROW(0x40063000u),
};

_Static_assert(sizeof(opencfw_cmdq_ops_table) == 12u * 0x28u,
               "stock table extent");
