/* Product-test helpers for the TI OPT3007 ambient light sensor and the shared
 * sensor rail, used by pt_protocol_procsr (stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\product_test\pt_protocol_procsr.c,
 * get_device_id case 6 at 0x574808). Native 0x58f8cc..0x58f935 and
 * 0x58f950..0x58f963 (literals 0x58f964 config pointer, 0x58f96c WTC4).
 *
 * The OPT3007 register map (g2_als.h) is filled by ti_opt3007_assignRegistermap;
 * fields are written with the read-modify-write helper 0x51357c and whole
 * registers read through 0x5135d2 (I2C bus 2, address 0x45). The rail on
 * GPIO134 is switched on by pt_sensor_rail_power_on_58f936 (rtos-glue-gaps). */
#include <stdint.h>
#include "g2_als.h"

#define SENSOR_RAIL_PIN 134u
#define GPIO_WTC4 0x40010468u /* output clear, pins 128..159 */
#define OPT3007_MODE_CONTINUOUS 3u
#define OPT3007_CONVERSION_100MS 0u

extern const uint32_t g2_sensor_rail_pin_config; /* ROM 0x78ee40, value 0x183 (push-pull output) */
extern uint32_t am_hal_gpio_pinconfig_480f0c(uint32_t pin, uint32_t config);
extern void opt3007_field_write_51357c(const g2_opt3007_field_t *field, uint32_t value);
extern uint16_t opt3007_register_get_5135d2(const g2_opt3007_field_t *field);

/* M[10:9] = 3: continuous conversions. */
void opt3007_mode_continuous_set_58f8cc(g2_opt3007_regmap_t *map)
{
    opt3007_field_write_51357c(&map->mode, OPT3007_MODE_CONTINUOUS);
}

/* CT[11] = 0: 100 ms conversion time. */
void opt3007_conversion_100ms_set_58f8d8(g2_opt3007_regmap_t *map)
{
    opt3007_field_write_51357c(&map->conversion_time, OPT3007_CONVERSION_100MS);
}

/* Register 0x7e, expected 0x5449 ("TI"). */
uint16_t opt3007_manufacturer_id_get_58f922(g2_opt3007_regmap_t *map)
{
    return opt3007_register_get_5135d2(&map->manufacturer_id);
}

/* Register 0x7f, expected 0x3001. */
uint16_t opt3007_device_id_get_58f92c(g2_opt3007_regmap_t *map)
{
    return opt3007_register_get_5135d2(&map->device_id);
}

/* Drive the sensor rail low; no settle delay (the power-on twin waits 10 ms). */
void pt_sensor_rail_power_off_58f950(void)
{
    (void)am_hal_gpio_pinconfig_480f0c(SENSOR_RAIL_PIN, g2_sensor_rail_pin_config);
    *(volatile uint32_t *)(uintptr_t)GPIO_WTC4 = 1u << (SENSOR_RAIL_PIN - 128u);
}
