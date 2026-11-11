#include <stdint.h>

/* Native 0x3159bc..0x3159e8: encryption action; clear bit 1 of the record
 * flag byte +13, then run the five follow-up steps on the record. */
extern uint32_t opencfw_em9305_child_32cb2c(uintptr_t);
extern uint32_t opencfw_em9305_child_317c40(uintptr_t);
extern uint32_t opencfw_em9305_child_3197d8(uintptr_t);
extern uint32_t opencfw_em9305_child_326a2c(uintptr_t);
extern uint32_t opencfw_em9305_phy_timer_start_32c7e4(uintptr_t);

uint32_t opencfw_em9305_enc_action_3159bc(uintptr_t record)
{
    volatile uint8_t *flags = (volatile uint8_t *)(record + 13u);
    *flags = (uint8_t)(*flags & ~2u);
    (void)opencfw_em9305_child_32cb2c(record);
    (void)opencfw_em9305_child_317c40(record);
    (void)opencfw_em9305_child_3197d8(record);
    (void)opencfw_em9305_child_326a2c(record);
    return opencfw_em9305_phy_timer_start_32c7e4(record);
}
