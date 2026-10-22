/* Nordic nPM1300 PMIC glue (stock driver/npmx_driver_transplant/src/npmx_main_driver.c,
 * native 0x511002..0x512bb1), used on charger family 1 boards.
 *
 * The PMIC sits on product I2C bus 7 at 7-bit address 0x6b (same bus as the
 * family-2 BQ25180 at 0x6a and BQ27427 at 0x55). Registers are 16-bit,
 * sent high byte first. The npmx v1.0.1 library and nrf_fuel_gauge are linked
 * unchanged; see drivers/power/npm1300/npmx_main_driver.c. */
#ifndef G2_NPM1300_H
#define G2_NPM1300_H

#include <stddef.h>
#include <stdint.h>

#define G2_NPM1300_I2C_BUS  7u
#define G2_NPM1300_I2C_ADDR 0x6bu

struct npmx_instance;

uint32_t npmx_backend_i2c_read_511002(void *p_context, uint32_t register_address,
                                      uint8_t *p_data, size_t len);
uint32_t npmx_backend_i2c_write_511084(void *p_context, uint32_t register_address,
                                       uint8_t *p_data, size_t len);
void npmx_backend_init_511108(void);
void npmx_int_pin_configure_5111e6(void);
void watchdog_timer_callback_51124c(struct npmx_instance *p_pm, uint32_t type, uint8_t mask);
void vbusin_voltage_callback_511294(struct npmx_instance *p_pm, uint32_t type, uint8_t mask);
void npmx_application_configure_511342(void);
void npmx_watchdog_enable_511882(void);
uint32_t npmx_get_adc_measurements_511990(float *voltage, float *current, float *temp,
                                          uint8_t *charger_status);
void initialize_fuel_gauge_511c24(void);
__attribute__((pcs("aapcs-vfp"))) void process_fuel_gauge_51201c(float t_delta); /* stock takes t_delta in s0 */
void configure_buck2_voltage_51238c(void);
void configure_lsdw1_voltage_51247c(void);
void npmx_main_driver_init_512644(void);
void check_fuel_gauge_init_51283c(void);
void fuel_gauge_ref_time_update_512892(void);
void npmx_charger_disable_5128f8(void);
void npmx_charger_enable_51299c(void);
void npmx_bchg_vbat_low_charge_enable_512a34(void);
void npmx_bchg_ntc_enable_512a4c(void);
int32_t npmx_enter_ship_mode_512a70(void);
int32_t npmx_get_device_id_512b20(uint32_t *device_id);

#endif
