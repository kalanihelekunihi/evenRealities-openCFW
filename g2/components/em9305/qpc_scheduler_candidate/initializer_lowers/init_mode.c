#include "init_lower_native.h"

/* Stock 0x3079c4..0x307a16. Parent returns the immediate 704 in r0. */
uint32_t opencfw_em9305_init_lower_3079c4(uint32_t incoming)
{
    (void)incoming;
    uint8_t version = init_read8((uintptr_t)init_read32(0x805cacu) + 4u);
    init_write32(0x802974u, init_code_address(opencfw_em9305_callback_31ff68));
    init_write32(0x805208u, (uint32_t)(uintptr_t)opencfw_em9305_callback_320084);
    init_write32(0x801304u, (uint32_t)(uintptr_t)opencfw_em9305_callback_307a18);
    if (version >= 14u)
        init_write32(0x805b34u, init_read32(0x805b34u) | (1u << 10));
    opencfw_em9305_init_child_307980();
    init_write16(0x805b20u, 704u);
    return 704u;
}

/* Stock 0x307af8..0x307b5e. The halfword store is the return-delay slot. */
uint32_t opencfw_em9305_init_lower_307af8(uint32_t incoming)
{
    (void)incoming;
    uint8_t version = init_read8((uintptr_t)init_read32(0x805cacu) + 4u);
    init_write32(0x80296cu, init_code_address(opencfw_em9305_callback_320434));
    init_write32(0x805218u, (uint32_t)(uintptr_t)opencfw_em9305_callback_32056c);
    init_write32(0x802898u, init_code_address(opencfw_em9305_callback_322a30));
    init_write32(0x801308u, (uint32_t)(uintptr_t)opencfw_em9305_callback_307b60);
    if (version >= 14u)
        init_write32(0x805b34u, init_read32(0x805b34u) | (1u << 10));
    opencfw_em9305_init_child_307a68();
    init_write16(0x805b1eu, 704u);
    return 0x805b0cu;
}
