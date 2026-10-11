/* SPDX-License-Identifier: MIT
 * Stock 0x08002f46 mode selector. The 0x08004a00 register snapshot remains
 * an imported flash-controller contract and must populate word six.
 */
#include <stdint.h>
extern void case_flash_mode_registers(uint32_t snapshot[7]);

uint32_t case_binary_5e_flash_mode(void)
{
    uint32_t snapshot[7];
    case_flash_mode_registers(snapshot);
    return (snapshot[6] & (1u<<20)) ? 1u : 2u;
}
