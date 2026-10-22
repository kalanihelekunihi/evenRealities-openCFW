/* SPDX-License-Identifier: MIT
 * CASE 0x0800be74 two-byte input command probe.
 */
#include <stdint.h>
/* Stock 0x0800BE74 (case_starts_with_de) */
uint32_t case_boot_sensor_finish_probe(const uint8_t *input)
{
    uint8_t first=input[0];
    if(first!='d'&&first!='D')return 0u;
    uint8_t second=input[1];
    return second=='e'||second=='E';
}
