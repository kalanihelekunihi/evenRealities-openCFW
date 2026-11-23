#include "init_lower_native.h"
#include "em9305_ram.h"

/* Stock 0x306c44..0x306c7a. The final state store is the jump-delay slot. */
uint32_t opencfw_em9305_init_lower_306c44(uint32_t incoming)
{
    (void)incoming;
    init_write32(((uintptr_t)&em9305_ram_805688 + 0x1cu), init_code_address(opencfw_em9305_callback_32483c));
    uint32_t old = init_read32(((uintptr_t)&em9305_ram_805af0 + 0x44u));
    init_write32(((uintptr_t)&em9305_ram_803d20 + 0x10u), init_code_address(opencfw_em9305_callback_317f5c));
    init_write32(((uintptr_t)&em9305_ram_801a14 + 0x4u), init_code_address(opencfw_em9305_callback_317ca8));
    uint32_t enabled = old | (1u << 5);
    init_write32(((uintptr_t)&em9305_ram_805af0 + 0x44u), enabled);
    return enabled;
}

/* Stock 0x3077f4..0x307832. The version read follows child 0x317498. */
uint32_t opencfw_em9305_init_lower_3077f4(uint32_t incoming)
{
    (void)incoming;
    init_write32(((uintptr_t)&em9305_ram_802950 + 0x44u), init_code_address(opencfw_em9305_callback_31ce50));
    init_write32(((uintptr_t)&em9305_ram_8051b8 + 0x88u), (uint32_t)(uintptr_t)opencfw_em9305_callback_31d438);
    opencfw_em9305_init_child_317498();
    uint32_t version = init_read8((uintptr_t)init_read32(((uintptr_t)&em9305_ram_805c5c + 0x50u)) + 4u);
    if (version < 11u) return version;
    uint32_t state = init_read32(((uintptr_t)&em9305_ram_805af0 + 0x40u)) | (1u << 31);
    init_write32(((uintptr_t)&em9305_ram_805af0 + 0x40u), state);
    /* Native r0 is the address of the state word at this return. */
    return ((uintptr_t)&em9305_ram_805af0 + 0x40u);
}

/* Stock 0x307834..0x30789e. Lower 0x3078a0 is a true child. */
uint32_t opencfw_em9305_init_lower_307834(uint32_t incoming)
{
    (void)incoming;
    opencfw_em9305_init_child_3078a0();
    uint32_t product = init_read32(((uintptr_t)&em9305_ram_805c5c + 0x50u));
    init_write32(((uintptr_t)&em9305_ram_8027e0 + 0x2cu), (uint32_t)(uintptr_t)opencfw_em9305_callback_31f9b0);
    init_write32(((uintptr_t)&em9305_ram_8052bc + 0x14u), (uint32_t)(uintptr_t)opencfw_em9305_callback_30fc24);
    uint32_t old = init_read32(((uintptr_t)&em9305_ram_805af0 + 0x40u));
    uint8_t version = init_read8((uintptr_t)product + 4u);
    init_write32(((uintptr_t)&em9305_ram_803d20 + 0xcu), init_code_address(opencfw_em9305_callback_319890));
    init_write32(((uintptr_t)&em9305_ram_803d20 + 0x8u), init_code_address(opencfw_em9305_callback_31fa44));
    init_write32(((uintptr_t)&em9305_ram_8052bc + 0x10u), (uint32_t)(uintptr_t)opencfw_em9305_callback_30fc20);
    uint32_t enabled = old | 1u;
    /* The first store executes in the branch-delay slot for either path. */
    init_write32(((uintptr_t)&em9305_ram_805af0 + 0x40u), enabled);
    if (version >= 7u) {
        enabled = old | 0x11u;
        init_write32(((uintptr_t)&em9305_ram_805af0 + 0x40u), enabled);
    }
    return enabled;
}
