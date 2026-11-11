#include <stdint.h>

/* Native 0x319990..0x3199b2: if the record's associated state byte (+368)
 * is 1, run the associated action and release; then clear the command
 * record. */
extern uint32_t opencfw_em9305_associated_action_324aa8(uintptr_t record);
extern uint32_t opencfw_em9305_associated_release_324a60(uintptr_t record);
extern void opencfw_em9305_command_record_clear_31ac54(uintptr_t record);

void opencfw_em9305_child_319990(uintptr_t record)
{
    if(*(volatile uint8_t *)(record+368u)==1u){
        (void)opencfw_em9305_associated_action_324aa8(record);
        (void)opencfw_em9305_associated_release_324a60(record);
    }
    opencfw_em9305_command_record_clear_31ac54(record);
}
