#include <stdint.h>

/* Native 0x3199b4..0x3199d6: when the record state byte at +368 is 1, run
 * the associated action and release first; always finish with 319de8. */
extern uint32_t opencfw_em9305_associated_action_324aa8(uintptr_t record);
extern uint32_t opencfw_em9305_associated_release_324a60(uintptr_t record);
extern uint32_t opencfw_em9305_child_319de8(uintptr_t record);

uint32_t opencfw_em9305_child_3199b4(uintptr_t record)
{
    if(*(volatile uint8_t *)(record+368u)==1u){
        (void)opencfw_em9305_associated_action_324aa8(record);
        (void)opencfw_em9305_associated_release_324a60(record);
    }
    return opencfw_em9305_child_319de8(record);
}
