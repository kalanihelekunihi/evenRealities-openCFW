#include "init_lower_native.h"

/* Stock 0x306c44..0x306c7a. The final state store is the jump-delay slot. */
uint32_t opencfw_em9305_init_lower_306c44(uint32_t incoming)
{
    (void)incoming;
    init_write32(0x8056a4u, init_code_address(opencfw_em9305_callback_32483c));
    uint32_t old = init_read32(0x805b34u);
    init_write32(0x803d30u, init_code_address(opencfw_em9305_callback_317f5c));
    init_write32(0x801a18u, init_code_address(opencfw_em9305_callback_317ca8));
    uint32_t enabled = old | (1u << 5);
    init_write32(0x805b34u, enabled);
    return enabled;
}

/* Stock 0x3077f4..0x307832. The version read follows child 0x317498. */
uint32_t opencfw_em9305_init_lower_3077f4(uint32_t incoming)
{
    (void)incoming;
    init_write32(0x802994u, init_code_address(opencfw_em9305_callback_31ce50));
    init_write32(0x805240u, (uint32_t)(uintptr_t)opencfw_em9305_callback_31d438);
    opencfw_em9305_init_child_317498();
    uint32_t version = init_read8((uintptr_t)init_read32(0x805cacu) + 4u);
    if (version < 11u) return version;
    uint32_t state = init_read32(0x805b30u) | (1u << 31);
    init_write32(0x805b30u, state);
    /* Native r0 is the address of the state word at this return. */
    return 0x805b30u;
}

/* Stock 0x307834..0x30789e. Lower 0x3078a0 is a true child. */
uint32_t opencfw_em9305_init_lower_307834(uint32_t incoming)
{
    (void)incoming;
    opencfw_em9305_init_child_3078a0();
    uint32_t product = init_read32(0x805cacu);
    init_write32(0x80280cu, init_code_address(opencfw_em9305_callback_31f9b0));
    init_write32(0x8052d0u, (uint32_t)(uintptr_t)opencfw_em9305_callback_30fc24);
    uint32_t old = init_read32(0x805b30u);
    uint8_t version = init_read8((uintptr_t)product + 4u);
    init_write32(0x803d2cu, init_code_address(opencfw_em9305_callback_319890));
    init_write32(0x803d28u, init_code_address(opencfw_em9305_callback_31fa44));
    init_write32(0x8052ccu, (uint32_t)(uintptr_t)opencfw_em9305_callback_30fc20);
    uint32_t enabled = old | 1u;
    /* The first store executes in the branch-delay slot for either path. */
    init_write32(0x805b30u, enabled);
    if (version >= 7u) {
        enabled = old | 0x11u;
        init_write32(0x805b30u, enabled);
    }
    return enabled;
}
