/* SPDX-License-Identifier: MIT
 * Stock CASE0x08009ebc battery measurement ABI: success0 with uint32percent
 * output, failure-1 with calleroutput untouched. Input query is register4;
 * raw Q8.8 SOC scales by100/0x6300 and saturates at100. Query hardware
 * effects remain its separate source/provider contract.
 */
#ifndef CASE_BATTERY_MEASUREMENT_CONTRACT_H
#define CASE_BATTERY_MEASUREMENT_CONTRACT_H
#include <stdint.h>
int32_t case_boot_battery_percent(uint32_t *out);
int32_t case_init_read_product_byte(uint32_t *out);
#endif
