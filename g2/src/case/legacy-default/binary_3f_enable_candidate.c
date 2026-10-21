/* SPDX-License-Identifier: MIT
 * Isolated stock 0x0800d154 output-enable wrapper. The setter is a lower contract.
 */
#include <stdint.h>

extern uint32_t case_binary_3f_set(uint32_t index, uint32_t value);

uint32_t case_binary_3f_enable(void)
{
    case_binary_3f_set(3u, 0xaeu);
    case_binary_3f_set(4u, 0xaeu);
    case_binary_3f_set(5u, 3u);
    return case_binary_3f_set(6u, 0x81u);
}
