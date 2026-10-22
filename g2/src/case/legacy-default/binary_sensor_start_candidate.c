/* SPDX-License-Identifier: MIT
 * Isolated stock 0x0800a4b4 sensor start pulse sequence.
 * Line setters and delay are controlled lower contracts.
 */
#include <stdint.h>

extern void case_binary_sensor_line_a(uint32_t level);
extern void case_binary_sensor_line_b(uint32_t level);
extern uint32_t case_binary_sensor_delay(void);

/* Stock 0x0800A4B4 (case_serial_start) */
uint32_t case_binary_sensor_start(void)
{
    case_binary_sensor_line_a(1u);
    case_binary_sensor_line_b(1u);
    case_binary_sensor_delay();
    case_binary_sensor_line_b(0u);
    case_binary_sensor_delay();
    case_binary_sensor_line_a(0u);
    return case_binary_sensor_delay();
}
