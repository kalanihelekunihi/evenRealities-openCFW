/* SPDX-License-Identifier: MIT
 * Native CASE 0x08006b80/0x08006b98 GPIO control leaves.
 */
#include "../source_candidate_20261010/case_gpio_control_contract.h"
void case_boot_transport_stop_clock(uint32_t value)
{
    case_control_a(value);
}
void case_boot_transport_stop_link(uint32_t value)
{
    case_control_b(value);
}
