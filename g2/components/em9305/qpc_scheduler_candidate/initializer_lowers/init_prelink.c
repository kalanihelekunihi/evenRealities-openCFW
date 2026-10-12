#include "init_lower_native.h"

/* Native 0x3251dc and 0x318ab8 are genuine side-effect children. The
 * latter receives the former's R0 without an intervening move. */
extern uint32_t opencfw_em9305_init_child_3251dc(uint32_t callback);
extern uint32_t opencfw_em9305_init_child_318ab8(uint32_t previous_result);

/* Stock 0x3078a0..0x30796e. GNU ARC condition aliases identify BC as LO;
 * after CMP version,7 the first exit is therefore for version<7.
 * All stores below preserve the native repeated state writes. */
void opencfw_em9305_init_child_3078a0(void)
{
    init_write32(0x802880u, (uint32_t)(uintptr_t)opencfw_em9305_callback_31e7fc);
    init_write32(0x80287cu, init_code_address(opencfw_em9305_callback_318c1c));
    init_write32(0x802878u, init_code_address(opencfw_em9305_callback_318f2c));
    init_write32(0x802954u, init_code_address(opencfw_em9305_callback_31df8c));
    init_write32(0x805200u, (uint32_t)(uintptr_t)opencfw_em9305_callback_31e604);
    init_write32(0x803d54u, (uint32_t)(uintptr_t)opencfw_em9305_mode_event_31bd78);
    init_write32(0x803d34u, init_code_address(opencfw_em9305_callback_320f78));
    init_write32(0x80280cu, init_code_address(opencfw_em9305_callback_322754));
    init_write32(0x8027e0u, init_code_address(opencfw_em9305_callback_325984));
    uint32_t previous = opencfw_em9305_init_child_3251dc(
        init_code_address(opencfw_em9305_callback_3189f4));
    (void)opencfw_em9305_init_child_318ab8(previous);
    uintptr_t product = (uintptr_t)init_read32(0x805cacu);
    uint8_t version = init_read8(product + 4u);
    if (version < 7u) return;
    uint32_t old = init_read32(0x805b30u);
    init_write32(0x805b30u, old | 0xeu);
    if (version == 7u) return;
    uint32_t second = init_read32(0x805b34u);
    init_write32(0x805b30u, old | 0x2eu);
    if (version < 9u) return;
    init_write32(0x805b34u, second);
    init_write32(0x805b30u, old | 0x1002eu);
    if (version == 9u) return;
    init_write32(0x805b34u, second);
    init_write32(0x805b30u, old | 0x501002eu);
    if (version < 12u) return;
    init_write32(0x805b30u, old | 0x501002eu);
    init_write32(0x805b34u, second | (1u << 7));
}
