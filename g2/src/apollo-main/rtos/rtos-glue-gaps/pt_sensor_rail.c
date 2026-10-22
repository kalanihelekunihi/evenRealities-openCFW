/* Product-test sensor rail switch-on, native 0x58f936..0x58f94f (literals 0x58f964/0x58f968).
 * Called from pt_cmd_47_handler (0x574808) before it talks to the ambient light
 * sensor. GPIO134 is the shared codec/sensor rail (see findings-hardware-drivers.md);
 * the neighbour 0x58f950 drives it low through WTC4. */
#include <stdint.h>

#define SENSOR_RAIL_PIN 134u
#define GPIO_WTS4 0x4001044cu /* output set, pins 128..159 */
#define SENSOR_RAIL_SETTLE_MS 10u

extern const uint32_t g2_sensor_rail_pin_config; /* ROM 0x78ee40, value 0x183 (push-pull output) */
extern uint32_t am_hal_gpio_pinconfig_480f0c(uint32_t pin, uint32_t config);
extern int32_t osDelay(uint32_t ticks); /* 0x449376 */

void pt_sensor_rail_power_on_58f936(void)
{
    (void)am_hal_gpio_pinconfig_480f0c(SENSOR_RAIL_PIN, g2_sensor_rail_pin_config);
    *(volatile uint32_t *)(uintptr_t)GPIO_WTS4 = 1u << (SENSOR_RAIL_PIN - 128u);
    (void)osDelay(SENSOR_RAIL_SETTLE_MS);
}
