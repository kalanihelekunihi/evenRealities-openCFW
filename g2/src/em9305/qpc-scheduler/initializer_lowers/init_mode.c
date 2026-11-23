#include "init_lower_native.h"
#include "em9305_ram.h"

/* Stock 0x3079c4..0x307a16. Parent returns the immediate 704 in r0. */
uint32_t opencfw_em9305_init_lower_3079c4(uint32_t incoming)
{
    (void)incoming;
    uint8_t version = init_read8((uintptr_t)init_read32(((uintptr_t)&em9305_ram_805c5c + 0x50u)) + 4u);
    init_write32(((uintptr_t)&em9305_ram_802950 + 0x24u), init_code_address(opencfw_em9305_callback_31ff68));
    init_write32(((uintptr_t)&em9305_ram_8051b8 + 0x50u), (uint32_t)(uintptr_t)opencfw_em9305_callback_320084);
    init_write32(((uintptr_t)&em9305_ram_8012c0 + 0x44u), (uint32_t)(uintptr_t)opencfw_em9305_callback_307a18);
    if (version >= 14u)
        init_write32(((uintptr_t)&em9305_ram_805af0 + 0x44u), init_read32(((uintptr_t)&em9305_ram_805af0 + 0x44u)) | (1u << 10));
    opencfw_em9305_init_child_307980();
    init_write16(((uintptr_t)&em9305_ram_805af0 + 0x30u), 704u);
    return 704u;
}

/* Stock 0x307af8..0x307b5e. The halfword store is the return-delay slot. */
uint32_t opencfw_em9305_init_lower_307af8(uint32_t incoming)
{
    (void)incoming;
    uint8_t version = init_read8((uintptr_t)init_read32(((uintptr_t)&em9305_ram_805c5c + 0x50u)) + 4u);
    init_write32(((uintptr_t)&em9305_ram_802950 + 0x1cu), init_code_address(opencfw_em9305_callback_320434));
    init_write32(((uintptr_t)&em9305_ram_8051b8 + 0x60u), (uint32_t)(uintptr_t)opencfw_em9305_callback_32056c);
    init_write32(((uintptr_t)&em9305_ram_802878 + 0x20u), init_code_address(opencfw_em9305_callback_322a30));
    init_write32(((uintptr_t)&em9305_ram_8012c0 + 0x48u), (uint32_t)(uintptr_t)opencfw_em9305_callback_307b60);
    if (version >= 14u)
        init_write32(((uintptr_t)&em9305_ram_805af0 + 0x44u), init_read32(((uintptr_t)&em9305_ram_805af0 + 0x44u)) | (1u << 10));
    opencfw_em9305_init_child_307a68();
    init_write16(((uintptr_t)&em9305_ram_805af0 + 0x2eu), 704u);
    return ((uintptr_t)&em9305_ram_805af0 + 0x1cu);
}
