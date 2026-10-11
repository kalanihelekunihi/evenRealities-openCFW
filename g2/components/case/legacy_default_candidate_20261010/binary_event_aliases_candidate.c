/* SPDX-License-Identifier: MIT
 * Exact stock-address aliases of the selected CASE event-forwarding wrapper.
 * Both sides use an event pointer and a 32-bit mask, returning a 32-bit word.
 * Event-group/task effects remain the selected provider's lower contract.
 */
#include <stdint.h>

extern uint32_t case_forward_event(void *event, uint32_t flags);

uint32_t case_binary_3d_control(uint32_t object, uint32_t mask)
{
    return case_forward_event((void *)(uintptr_t)object, mask);
}
uint32_t case_binary_3e_control(uint32_t object, uint32_t mask)
{
    return case_forward_event((void *)(uintptr_t)object, mask);
}
uint32_t case_binary_forward_control(uint32_t object, uint32_t mask)
{
    return case_forward_event((void *)(uintptr_t)object, mask);
}
uint32_t case_legacy_b0_child(uint32_t object, uint32_t mask)
{
    return case_forward_event((void *)(uintptr_t)object, mask);
}
