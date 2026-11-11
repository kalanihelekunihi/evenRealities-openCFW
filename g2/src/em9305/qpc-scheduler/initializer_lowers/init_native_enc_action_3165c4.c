#include <stdint.h>

/* Native 0x3165c4..0x3165f2: encryption start action. Runs the 3197d0,
 * 3197c8, 31af80 and 325e4c steps, starts the PHY timer, sets bit 1 of
 * the flag byte at +13 and reports through 3197f8. */
extern uint32_t opencfw_em9305_enc_action_3197d0(uintptr_t record);
extern uint32_t opencfw_em9305_child_3197c8(uintptr_t record);
extern uint32_t opencfw_em9305_child_31af80(uintptr_t record);
extern uint32_t opencfw_em9305_child_325e4c(uintptr_t record);
extern uint32_t opencfw_em9305_phy_timer_start_32c7e4(uintptr_t record);
extern uint32_t opencfw_em9305_child_3197f8(uintptr_t record);

uint32_t opencfw_em9305_enc_action_3165c4(uintptr_t record)
{
    (void)opencfw_em9305_enc_action_3197d0(record);
    (void)opencfw_em9305_child_3197c8(record);
    (void)opencfw_em9305_child_31af80(record);
    (void)opencfw_em9305_child_325e4c(record);
    (void)opencfw_em9305_phy_timer_start_32c7e4(record);
    *(volatile uint8_t *)(record+13u)|=2u;
    return opencfw_em9305_child_3197f8(record);
}
