#include <stdint.h>

/* Native 0x315974..0x3159ba: encryption pause/finish action. Clear bit 1 of
 * the flag byte +13 and complete the PHY step; when flag +515 is set run
 * native 0x32cb24 and post mode event 0x6a, otherwise reject with reason 6.
 * Then complete the PHY update, run native 0x32e214 and clear +515. */
extern uint32_t opencfw_em9305_phy_complete_32c818(uintptr_t);
extern uint32_t opencfw_em9305_child_32cb24(uintptr_t);
extern uint32_t opencfw_em9305_mode_event_31bd78(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_phy_reject_32698c(uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_phy_update_complete_32e220(uintptr_t);
extern uint32_t opencfw_em9305_child_32e214(uintptr_t);

uint32_t opencfw_em9305_enc_action_315974(uintptr_t record)
{
    volatile uint8_t *flags = (volatile uint8_t *)(record + 13u);
    *flags = (uint8_t)(*flags & ~2u);
    (void)opencfw_em9305_phy_complete_32c818(record);
    volatile uint8_t *pending = (volatile uint8_t *)(record + 515u);
    if (*pending != 0u) {
        (void)opencfw_em9305_child_32cb24(record);
        (void)opencfw_em9305_mode_event_31bd78(record, 0x6au);
    } else {
        (void)opencfw_em9305_phy_reject_32698c(record, 6u, 0u);
    }
    (void)opencfw_em9305_phy_update_complete_32e220(record);
    uint32_t result = opencfw_em9305_child_32e214(record);
    *pending = 0u;
    return result;
}
