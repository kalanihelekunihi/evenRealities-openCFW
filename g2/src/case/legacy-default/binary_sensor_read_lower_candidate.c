/* SPDX-License-Identifier: MIT
 * Stock 0x0800a124 byte and 0x0800a130 counted read adapters.
 * Guarded sensor transaction remains a lower contract.
 */
#include <stdint.h>

extern uint32_t case_binary_guarded_sensor_read(uint32_t selector,
                                                 void *destination,
                                                 uint32_t length);

/* Dedup (0x0800a124): case_binary_read_byte_lower is an alias of case_init_pmic_read_register (startup/application_init_pmic_probe_candidate.c). */
extern uint32_t case_binary_read_byte_lower(uint32_t selector, uint8_t *destination);

/* Stock 0x0800A130 (case_run_guarded_status) */
uint32_t case_binary_sensor_read_adapter(uint32_t selector,
                                         uint8_t *destination,
                                         uint32_t length)
{
    case_binary_guarded_sensor_read(selector, destination, length);
    return 0u;
}

