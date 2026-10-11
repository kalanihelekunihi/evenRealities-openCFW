/* SPDX-License-Identifier: MIT
 * Native CASE 0x2888 power GPIO descriptor and 0xa4dc sensor-line preamble.
 */
#include <stdint.h>
extern void case_bus_gpio_config(uint32_t base,volatile uint32_t *state); /* 0x4d30 */
extern void case_binary_sensor_line_a(uint32_t level); /* 0xa550 */
extern void case_binary_sensor_line_b(uint32_t level); /* 0xa574 */
static void settle10(void)
{volatile uint32_t n=0u;do{n=(uint8_t)(n+1u);}while(n<10u);}
void case_boot_power_initialize(void)
{
    volatile uint32_t config[5]={24u,17u,0u,0u,0u};
    case_bus_gpio_config(0x50000400u,config);
    case_binary_sensor_line_b(0u);
    case_binary_sensor_line_a(1u);
    settle10();
    case_binary_sensor_line_b(1u);
    settle10();
}
