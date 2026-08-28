/*
 * SPDX-License-Identifier: MIT
 *
 * RTOS event-group wait-condition predicate matched to stock entry
 * 0x0047EE30.
 */

__attribute__((used, noinline))
unsigned int open_cfw_rtos_event_group_test_wait_condition(
    unsigned int current_bits,
    unsigned int bits_to_wait_for,
    unsigned int wait_for_all
)
{
    unsigned int condition_met = 0U;

    if (wait_for_all == 0U) {
        if ((current_bits & bits_to_wait_for) != 0U) {
            condition_met = 1U;
        }
    } else if (
        (current_bits & bits_to_wait_for) == bits_to_wait_for
    ) {
        condition_met = 1U;
    }

    return condition_met;
}
