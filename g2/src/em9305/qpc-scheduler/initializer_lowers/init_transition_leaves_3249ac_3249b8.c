#include <stdint.h>
extern uint32_t opencfw_em9305_ll_schedule_notify_313354(uintptr_t);
extern uint32_t opencfw_em9305_init_secondary_cleanup_321450(uintptr_t);
uint32_t opencfw_em9305_init_transition_3249ac(uintptr_t record)
{
    *(volatile uint8_t *)(record+2u)=1u;
    return opencfw_em9305_ll_schedule_notify_313354(record+48u);
}
uint32_t opencfw_em9305_init_transition_3249b8(uintptr_t record)
{ return opencfw_em9305_init_secondary_cleanup_321450(record); }
