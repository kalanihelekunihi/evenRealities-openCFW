/* SPDX-License-Identifier: MIT
 * Native CASE 0x08009ebc: product measurement register 4 scaled to 0..100.
 */
#include "case_battery_measurement_contract.h"
int32_t case_init_read_product_byte(uint32_t *out)
{
    return case_boot_battery_percent(out);
}
