/* SPDX-License-Identifier: MIT
 * Stock 0x0800a124 byte and 0x0800a130 counted read adapters.
 * Guarded sensor transaction remains a lower contract.
 */
#include <stdint.h>

extern uint32_t case_binary_guarded_sensor_read(uint32_t selector,
                                                 void *destination,
                                                 uint32_t length);

uint32_t case_binary_read_byte_lower(uint32_t selector, uint8_t *destination)
{
    case_binary_guarded_sensor_read(selector, destination, 1u);
    return 0u;
}

uint32_t case_binary_sensor_read_adapter(uint32_t selector,
                                         uint8_t *destination,
                                         uint32_t length)
{
    case_binary_guarded_sensor_read(selector, destination, length);
    return 0u;
}

