/* Nordic nPM1300 PMIC glue, stock
 * D:\01_workspace\s200_ap510b_iar_git\driver\npmx_driver_transplant\src\npmx_main_driver.c.
 * Native 0x511002..0x512bb1 (this file: the rows not anchored elsewhere);
 * literal pools 0x511948.., 0x511bc0.., 0x511fd8.., 0x5122c4.., 0x512370..,
 * 0x5123fc.., 0x512470.., 0x5124f0.., 0x512588.., 0x512608.., 0x51282c..,
 * 0x512998, 0x512a64.., 0x512b10.., 0x512bb4..0x512c83.
 *
 * The PMIC is on product I2C bus 7, 7-bit address 0x6b, with 16-bit register
 * addresses sent big-endian (high byte first). The npmx library (v1.0.1) and
 * the closed nrf_fuel_gauge library are linked unchanged; this file is only
 * the board glue: backend callbacks, init sequence, event callbacks, fuel
 * gauge bookkeeping and a few power-rail helpers. npmx calls return
 * npmx_error_t (NPMX_SUCCESS 0x2bad0000, INVALID_PARAM 0x2bad0001, IO
 * 0x2bad0002).
 *
 * Stock functions of this source defined elsewhere in g2/src under other
 * names: 0x5118e8 npmx_watchdog_kick (drivers/power/npmx-watchdog/kick.c),
 * 0x5122ec configure_buck1_voltage, 0x512410 disable_buck1_voltage,
 * 0x5124fc / 0x5125a8 load-switch-2 helpers (drivers/display/display-uled).
 * 0x511b74 (charge_status_inform_fuel_gauge) is called but not written here.
 *
 * Uses single-precision FP: build with profile g2-apollo-main-3. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "g2_hal_i2c.h"
#include "g2_bq27427.h"
#include "g2_npm1300.h"

/* npmx_backend_t (npmx_backend.h). */
typedef uint32_t (*npmx_backend_fn_t)(void *p_context, uint32_t register_address,
                                      uint8_t *p_data, size_t num_of_bytes);
typedef struct {
    npmx_backend_fn_t write; /* +0x0 */
    npmx_backend_fn_t read;  /* +0x4 */
    void *p_context;         /* +0x8 */
} npmx_backend_t;
_Static_assert(sizeof(npmx_backend_t) == 12, "stock backend record is 12 bytes");

/* npmx_timer_config_t as laid out in ROM 0x78b624 (12 bytes copied). */
typedef struct {
    uint32_t mode;          /* +0x0 2 = NPMX_TIMER_MODE_WATCHDOG_RESET */
    uint32_t prescaler;     /* +0x4 1 = NPMX_TIMER_PRESCALER_FAST (2 ms) */
    uint32_t compare_value; /* +0x8 */
} npmx_timer_config_t;

/* npmx_adc_ntc_config_t, template at ROM 0x78de1c. */
typedef struct {
    uint32_t type; /* +0x0 npmx_adc_ntc_type_t */
    uint32_t beta; /* +0x4 */
} npmx_adc_ntc_config_t;

/* npmx_adc_meas_all_t: indices 0 VBAT (mV), 1 battery temperature
 * (milli-degC), 6 IBAT (mA). */
typedef struct {
    int32_t values[8];
} npmx_adc_meas_all_t;

/* nrf_fuel_gauge_init_parameters, template at ROM 0x779c7c (24 bytes). */
typedef struct {
    float v0;               /* +0x00 */
    float i0;               /* +0x04 */
    float t0;               /* +0x08 */
    const void *model;      /* +0x0c battery model, ROM 0x646bf8 */
    const void *opt_params; /* +0x10 */
    const void *state;      /* +0x14 */
} nrf_fuel_gauge_init_parameters_t;
_Static_assert(sizeof(nrf_fuel_gauge_init_parameters_t) == 0x18, "stock init parameters are 24 bytes");

#define NPMX_SUCCESS              0x2bad0000u
#define NPMX_ERROR_INVALID_PARAM  0x2bad0001u
#define NPMX_ERROR_IO             0x2bad0002u
#define NPMX_BACKEND_MAX_LEN      32u

/* npmx_event_group_t / npmx_callback_type_t values used here. */
#define NPMX_EVENT_GROUP_SHIPHOLD        4u
#define NPMX_EVENT_GROUP_VBUSIN_VOLTAGE  5u
#define NPMX_EVENT_GROUP_COUNT           8u
#define NPMX_EVENT_SHIPHOLD_WATCHDOG_WARN 0x08u
#define NPMX_EVENT_VBUSIN_DETECTED       0x01u
#define NPMX_EVENT_VBUSIN_REMOVED        0x02u

/* nrf_fuel_gauge_ext_state_info_type. */
#define FG_EXT_VBUS_CONNECTED        0u
#define FG_EXT_VBUS_DISCONNECTED     1u
#define FG_EXT_CHARGE_CURRENT_LIMIT  5u
#define FG_EXT_TERM_CURRENT          6u

/* Raw nPM1300 registers written through the backend. */
#define NPM1300_BCHGDISABLECLR       0x0307u /* bit 1 clears DISABLENTC */
#define NPM1300_BCHGVBATLOWCHARGE    0x0350u
#define NPM1300_SYSLABEL             0x0101u

extern npmx_backend_t g2_npmx_backend;          /* RAM 0x20074068 */
extern void *g2_npmx_backend_context;           /* RAM 0x2007482c */
extern struct npmx_instance g2_npmx_instance;   /* RAM 0x20070f78 npmx_instance_t */
extern uint32_t g2_fuel_gauge_ref_time;         /* RAM 0x2007481c */
extern uint8_t g2_fuel_gauge_initialized;       /* RAM 0x20074fef */
extern uint8_t g2_npmx_last_charger_status;     /* RAM 0x20074ff0 */
extern g2_charger_telemetry_t g2_charger_telemetry; /* RAM 0x20073b18; +0x15 is the SoC-band flag */
extern const uint8_t nrf_fuel_gauge_variant;    /* ROM 0x78f6f6 (1 in the stock) */
extern const char *nrf_fuel_gauge_version;      /* RAM 0x2000450c */
extern const char *nrf_fuel_gauge_build_date;   /* RAM 0x20004508 */
extern const uint8_t g2_npm1300_battery_model[]; /* ROM 0x646bf8 */

/* npmx v1.0.1 library (upstream). */
extern uint32_t npmx_core_init(struct npmx_instance *p_pm, npmx_backend_t *p_backend,
                                      void *generic_cb, bool restore_values);
extern void npmx_core_register_cb(struct npmx_instance *p_pm, void *cb, uint32_t type);
extern uint32_t npmx_core_event_interrupt_enable(struct npmx_instance *p_pm, uint32_t group, uint32_t mask);
extern uint32_t npmx_core_event_interrupt_disable(struct npmx_instance *p_pm, uint32_t group, uint32_t mask);
extern void *npmx_gpio_get(struct npmx_instance *p_pm, uint8_t idx);
extern uint32_t npmx_gpio_mode_set(void *p_gpio, uint32_t mode);
extern void *npmx_vbusin_get(struct npmx_instance *p_pm, uint8_t idx);
extern uint32_t npmx_vbusin_current_convert(uint32_t milliamperes);
extern uint32_t npmx_vbusin_task_trigger(void *p_vbusin, uint32_t task);
extern uint32_t npmx_vbusin_current_limit_set(void *p_vbusin, uint32_t current);
extern uint32_t npmx_vbusin_vbus_status_get(void *p_vbusin, uint8_t *p_status);
extern void *npmx_timer_get(struct npmx_instance *p_pm, uint8_t idx);
extern uint32_t npmx_timer_task_trigger(void *p_timer, uint32_t task);
extern uint32_t npmx_timer_config_set(void *p_timer, const npmx_timer_config_t *p_config);
extern void *npmx_charger_get(struct npmx_instance *p_pm, uint8_t idx);
extern uint32_t npmx_charger_voltage_convert(uint32_t millivolts);
extern uint32_t npmx_charger_module_enable_set(void *p_charger, uint32_t mask);
extern uint32_t npmx_charger_module_disable_set(void *p_charger, uint32_t mask);
extern uint32_t npmx_charger_charging_current_set(void *p_charger, uint16_t milliamperes);
extern uint32_t npmx_charger_discharging_current_set(void *p_charger, uint16_t milliamperes);
extern uint32_t npmx_charger_termination_normal_voltage_set(void *p_charger, uint32_t voltage);
extern uint32_t npmx_charger_termination_warm_voltage_set(void *p_charger, uint32_t voltage);
extern uint32_t npmx_charger_status_get(void *p_charger, uint8_t *p_status);
extern void *npmx_adc_get(struct npmx_instance *p_pm, uint8_t idx);
extern uint32_t npmx_adc_ntc_type_convert(uint32_t ohms);
extern uint32_t npmx_adc_task_trigger(void *p_adc, uint32_t task);
extern uint32_t npmx_adc_ntc_config_set(void *p_adc, const npmx_adc_ntc_config_t *p_config);
extern uint32_t npmx_adc_meas_all_get(void *p_adc, npmx_adc_meas_all_t *p_meas);
extern uint32_t npmx_adc_ibat_meas_enable_set(void *p_adc, bool enable);
extern void *npmx_buck_get(struct npmx_instance *p_pm, uint8_t idx);        /* npmx_buck_get */
extern uint32_t npmx_buck_task_trigger(void *p_buck, uint32_t task);             /* npmx_buck_task_trigger */
extern uint32_t npmx_buck_normal_voltage_set(void *p_buck, uint32_t voltage);         /* npmx_buck_normal_voltage_set */
extern uint32_t npmx_buck_vout_select_set(void *p_buck, uint32_t mode);             /* npmx_buck_vout_select_set */
extern void *npmx_ldsw_get(struct npmx_instance *p_pm, uint8_t idx);    /* npmx_ldsw_get */
extern uint32_t npmx_ldsw_task_trigger(void *p_ldsw, uint32_t task);         /* npmx_ldsw_task_trigger */
extern uint32_t npmx_ldsw_mode_set(void *p_ldsw, uint32_t mode);         /* npmx_ldsw_mode_set */
extern uint32_t npmx_ldsw_ldo_voltage_set(void *p_ldsw, uint32_t voltage);
extern uint32_t npmx_backend_register_write(const npmx_backend_t *p_backend, uint32_t reg,
                                                      uint8_t *p_data, size_t len); /* npmx_backend_register_write */
extern uint32_t npmx_backend_register_read(const npmx_backend_t *p_backend, uint32_t reg,
                                                     uint8_t *p_data, size_t len);  /* npmx_backend_register_read */
extern void *npmx_ship_get(struct npmx_instance *p_pm, uint8_t idx);
extern uint32_t npmx_ship_task_trigger(void *p_ship, uint32_t task);

/* nrf_fuel_gauge (closed Nordic library). */
extern int32_t nrf_fuel_gauge_init_43c150(const nrf_fuel_gauge_init_parameters_t *params, float *v0);
extern int32_t nrf_fuel_gauge_ext_state_update_55f74c(uint32_t type, const void *info);
extern float nrf_fuel_gauge_process_55f848(float v, float i, float t, float t_delta, void *state);
extern float nrf_fuel_gauge_tte_get_55f994(void);
extern float nrf_fuel_gauge_ttf_get_55f9a0(void);

/* Other first-party callees. */
extern int32_t charge_status_inform_fuel_gauge_511b74(uint8_t charger_status);
extern void box_detect_vbus_connected_4ac130(void);
extern void box_detect_vbus_removed_4ac154(void);
extern const uint8_t *audio_ble_hci_radio_mode_state_50938e(uint32_t index);
extern void display_driver_uled_type0_mode4_finish_5125a8(void);
extern void *audio_uart_display_area_copy_439c04(void *dst, const void *src, uint32_t len); /* memcpy */
extern void g2_delay_ms_4910f4(uint32_t ms);
extern uint32_t osKernelGetTickCount(void);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "npmx_driver"; /* ROM 0x78b618 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\npmx_driver_transplant\\src\\npmx_main_driver.c"; /* ROM 0x6e103c */

static const char fn_i2c_read[] = "npmx_backend_i2c_read"; /* ROM 0x779ab4 */
static const char fn_i2c_write[] = "npmx_backend_i2c_write"; /* ROM 0x779acc */
static const char fn_backend_init[] = "npmx_backend_init"; /* ROM 0x781458 */
static const char fn_int_pin[] = "npmx_int_pin_configure"; /* ROM 0x779ae4 */
static const char fn_wdt_cb[] = "watchdog_timer_callback"; /* ROM 0x779afc */
static const char fn_vbus_cb[] = "vbusin_voltage_callback"; /* ROM 0x779b14 */
static const char fn_app_cfg[] = "npmx_application_configure"; /* ROM 0x76e84c */
static const char fn_wdt_enable[] = "npmx_watchdog_enable"; /* ROM 0x779b2c */
static const char fn_adc_meas[] = "npmx_get_adc_measurements"; /* ROM 0x76e868 */
static const char fn_fg_init[] = "initialize_fuel_gauge"; /* ROM 0x779b44 */
static const char fn_fg_process[] = "process_fuel_gauge"; /* ROM 0x7814a8 */
static const char fn_buck2[] = "configure_buck2_voltage"; /* ROM 0x779ba4 */
static const char fn_lsdw1[] = "configure_lsdw1_voltage"; /* ROM 0x779bd4 */
static const char fn_main_init[] = "npmx_main_driver_init"; /* ROM 0x779c1c */
static const char fn_fg_check[] = "check_fuel_gauge_init"; /* ROM 0x779c34 */
static const char fn_chg_disable[] = "npmx_charger_disable"; /* ROM 0x779c4c */
static const char fn_chg_enable[] = "npmx_charger_enable"; /* ROM 0x781520 */
static const char fn_ship[] = "npmx_enter_ship_mode"; /* ROM 0x779c64 */
static const char fn_device_id[] = "npmx_get_device_id"; /* ROM 0x781534 */

static const char s_i2c_read[] = "ERROR: HAL_I2CMasterRegRead=%lu\n"; /* ROM 0x757080 */
static const char c_i2c_read[] = "[npmx_driver]ERROR: HAL_I2CMasterRegRead=%lu\n"; /* ROM 0x735d74 */
static const char s_i2c_write[] = "ERROR: HAL_I2CMasterRegWrite=%lu\n"; /* ROM 0x7570a4 */
static const char c_i2c_write[] = "[npmx_driver]ERROR: HAL_I2CMasterRegWrite=%lu\n"; /* ROM 0x735da4 */
static const char s_core_init[] = "ERROR: npmx_core_init=%d\n"; /* ROM 0x76e814 */
static const char c_core_init[] = "[npmx_driver]ERROR: npmx_core_init=%d\n"; /* ROM 0x74baf4 */
static const char s_irq_disable[] = "ERROR: npmx_core_event_interrupt_disable=%d\n"; /* ROM 0x735dd4 */
static const char c_irq_disable[] = "[npmx_driver]ERROR: npmx_core_event_interrupt_disable=%d\n"; /* ROM 0x716ccc */
static const char s_gpio_mode[] = "ERROR: npmx_gpio_mode_set=%d\n"; /* ROM 0x7628b0 */
static const char c_gpio_mode[] = "[npmx_driver]ERROR: npmx_gpio_mode_set=%d\n"; /* ROM 0x740868 */
static const char s_wdt_triggered[] = "Watchdog triggered\n"; /* ROM 0x78146c */
static const char c_wdt_triggered[] = "[npmx_driver]Watchdog triggered\n"; /* ROM 0x7570c8 */
static const char s_vbus_on[] = "VBUS detected (connected)\n"; /* ROM 0x76e830 */
static const char c_vbus_on[] = "[npmx_driver]VBUS detected (connected)\n"; /* ROM 0x74bb1c */
static const char s_vbus_off[] = "VBUS removed (disconnected)\n"; /* ROM 0x7628d0 */
static const char c_vbus_off[] = "[npmx_driver]VBUS removed (disconnected)\n"; /* ROM 0x740894 */
static const char s_irq_enable[] = "ERROR: npmx_core_event_interrupt_enable=%d\n"; /* ROM 0x7408c0 */
static const char c_irq_enable[] = "[npmx_driver]ERROR: npmx_core_event_interrupt_enable=%d\n"; /* ROM 0x716d08 */
static const char s_timer_cfg[] = "ERROR: npmx_timer_config_set=%d\n"; /* ROM 0x7570ec */
static const char c_timer_cfg[] = "[npmx_driver]ERROR: npmx_timer_config_set=%d\n"; /* ROM 0x735e04 */
static const char s_chg_cur[] = "ERROR: npmx_charger_charging_current_set=%d\n"; /* ROM 0x735e34 */
static const char c_chg_cur[] = "[npmx_driver]ERROR: npmx_charger_charging_current_set=%d\n"; /* ROM 0x716d44 */
static const char s_dischg_cur[] = "ERROR: npmx_charger_discharging_current_set=%d\n"; /* ROM 0x735e64 */
static const char c_dischg_cur[] = "[npmx_driver]ERROR: npmx_charger_discharging_current_set=%d\n"; /* ROM 0x70d4a4 */
static const char s_term_normal[] = "ERROR: npmx_charger_termination_normal_voltage_set=%d\n"; /* ROM 0x720948 */
static const char c_term_normal[] = "[npmx_driver]ERROR: npmx_charger_termination_normal_voltage_set=%d\n"; /* ROM 0x704308 */
static const char s_term_warm[] = "ERROR: npmx_charger_termination_warm_voltage_set=%d\n"; /* ROM 0x720980 */
static const char c_term_warm[] = "[npmx_driver]ERROR: npmx_charger_termination_warm_voltage_set=%d\n"; /* ROM 0x70434c */
static const char s_chg_enable[] = "ERROR: npmx_charger_module_enable_set=%d\n"; /* ROM 0x7408ec */
static const char c_chg_enable[] = "[npmx_driver]ERROR: npmx_charger_module_enable_set=%d\n"; /* ROM 0x7209b8 */
static const char s_chg_disable[] = "ERROR: npmx_charger_module_disable_set=%d\n"; /* ROM 0x740a78 */
static const char c_chg_disable[] = "[npmx_driver]ERROR: npmx_charger_module_disable_set=%d\n"; /* ROM 0x720b08 */
static const char s_vbus_ilim[] = "ERROR: npmx_vbusin_current_limit_set=%d\n"; /* ROM 0x740918 */
static const char c_vbus_ilim[] = "[npmx_driver]ERROR: npmx_vbusin_current_limit_set=%d\n"; /* ROM 0x7209f0 */
static const char s_vbus_task[] = "ERROR: npmx_vbusin_task_trigger=%d\n"; /* ROM 0x757110 */
static const char c_vbus_task[] = "[npmx_driver]ERROR: npmx_vbusin_task_trigger=%d\n"; /* ROM 0x72b508 */
static const char s_ntc_cfg[] = "ERROR: npmx_adc_ntc_config_set=%d\n"; /* ROM 0x757134 */
static const char c_ntc_cfg[] = "[npmx_driver]ERROR: npmx_adc_ntc_config_set=%d\n"; /* ROM 0x735e94 */
static const char s_ibat_meas[] = "ERROR: npmx_adc_ibat_meas_enable_set=%d\n"; /* ROM 0x740944 */
static const char c_ibat_meas[] = "[npmx_driver]ERROR: npmx_adc_ibat_meas_enable_set=%d\n"; /* ROM 0x720a28 */
static const char s_adc_task[] = "ERROR: npmx_adc_task_trigger=%d\n"; /* ROM 0x757158 */
static const char c_adc_task[] = "[npmx_driver]ERROR: npmx_adc_task_trigger=%d\n"; /* ROM 0x735ec4 */
static const char s_wdt_enable[] = "ERROR:enable npmx watchdog task_trigger=%d\n"; /* ROM 0x740970 */
static const char c_wdt_enable[] = "[npmx_driver]ERROR:enable npmx watchdog task_trigger=%d\n"; /* ROM 0x716d80 */
static const char s_meas_all[] = "ERROR: npmx_adc_meas_all_get=%d\n"; /* ROM 0x75717c */
static const char c_meas_all[] = "[npmx_driver]ERROR: npmx_adc_meas_all_get=%d\n"; /* ROM 0x735ef4 */
static const char s_chg_status[] = "ERROR: npmx_charger_status_get=%d\n"; /* ROM 0x7571a0 */
static const char c_chg_status[] = "[npmx_driver]ERROR: npmx_charger_status_get=%d\n"; /* ROM 0x735f24 */
static const char s_fg_variant[] = "ERROR: Wrong fuel gauge variant\n"; /* ROM 0x7571c4 */
static const char c_fg_variant[] = "[npmx_driver]ERROR: Wrong fuel gauge variant\n"; /* ROM 0x735f54 */
static const char s_get_adc[] = "ERROR: npmx_get_adc_measurements=%d\n"; /* ROM 0x74bb44 */
static const char c_get_adc[] = "[npmx_driver]ERROR: npmx_get_adc_measurements=%d\n"; /* ROM 0x72b53c */
static const char s_fg_init[] = "ERROR: nrf_fuel_gauge_init=%d\n"; /* ROM 0x7628f0 */
static const char c_fg_init[] = "[npmx_driver]ERROR: nrf_fuel_gauge_init=%d\n"; /* ROM 0x7409c8 */
static const char s_fg_ext[] = "ERROR: nrf_fuel_gauge_ext_state_update=%d\n"; /* ROM 0x7409f4 */
static const char c_fg_ext[] = "[npmx_driver]ERROR: nrf_fuel_gauge_ext_state_update=%d\n"; /* ROM 0x720a98 */
static const char s_fg_inform[] = "ERROR: charge_status_inform_fuel_gauge=%d\n"; /* ROM 0x740a20 */
static const char c_fg_inform[] = "[npmx_driver]ERROR: charge_status_inform_fuel_gauge=%d\n"; /* ROM 0x720ad0 */
static const char s_fg_done[] = "Fuel gauge initialized\n"; /* ROM 0x779b5c */
static const char c_fg_done[] = "[npmx_driver]Fuel gauge initialized\n"; /* ROM 0x74bb6c */
static const char s_fg_v0[] = "  v0=%f,i0=%f,t0=%f\n"; /* ROM 0x779b74 */
static const char c_fg_v0[] = "[npmx_driver]  v0=%f,i0=%f,t0=%f\n"; /* ROM 0x7571e8 */
static const char s_fg_version[] = "  Version: %s\n"; /* ROM 0x787b50 */
static const char c_fg_version[] = "[npmx_driver]  Version: %s\n"; /* ROM 0x76e884 */
static const char s_fg_date[] = "  Build date: %s\n"; /* ROM 0x781494 */
static const char c_fg_date[] = "[npmx_driver]  Build date: %s\n"; /* ROM 0x762910 */
static const char s_vbus_status[] = "ERROR: npmx_vbusin_vbus_status_get=%d\n"; /* ROM 0x74bb94 */
static const char c_vbus_status[] = "[npmx_driver]ERROR: npmx_vbusin_vbus_status_get=%d\n"; /* ROM 0x72b570 */
static const char s_buck2_null[] = "p_buck2 is null!\n"; /* ROM 0x7814d0 */
static const char c_buck2_null[] = "[npmx_driver]p_buck2 is null!\n"; /* ROM 0x762950 */
static const char s_ldsw1_null[] = "p_ldsw1 is null!\n"; /* ROM 0x7814e4 */
static const char c_ldsw1_null[] = "[npmx_driver]p_ldsw1 is null!\n"; /* ROM 0x762970 */
static const char s_init_start[] = "Start to check npm1300 init..\n\n"; /* ROM 0x7629b0 */
static const char c_init_start[] = "[npmx_driver]Start to check npm1300 init..\n\n"; /* ROM 0x735f84 */
static const char s_init_backend[] = "Start npmx_backend_init..\n\n"; /* ROM 0x76e8a0 */
static const char c_init_backend[] = "[npmx_driver]Start npmx_backend_init..\n\n"; /* ROM 0x740a4c */
static const char s_init_int_pin[] = "Start npmx_int_pin_configure..\n\n"; /* ROM 0x75720c */
static const char c_init_int_pin[] = "[npmx_driver]Start npmx_int_pin_configure..\n\n"; /* ROM 0x735fb4 */
static const char s_init_bchg[] = "Configure bchg vbat low charge before enable charger..\n\n"; /* ROM 0x716dbc */
static const char c_init_bchg[] = "[npmx_driver]Configure bchg vbat low charge before enable charger..\n\n"; /* ROM 0x6fbb1c */
static const char s_init_app[] = "Start npmx_application_configure..\n\n"; /* ROM 0x74bbbc */
static const char c_init_app[] = "[npmx_driver]Start npmx_application_configure..\n\n"; /* ROM 0x72b5a4 */
static const char s_init_done[] = "Start to check npm1300 init done..\n\n"; /* ROM 0x74bbe4 */
static const char c_init_done[] = "[npmx_driver]Start to check npm1300 init done..\n\n"; /* ROM 0x72b5d8 */
static const char s_fg_not_init[] = "Fuel gauge not initialized, initializing...\n"; /* ROM 0x735fe4 */
static const char c_fg_not_init[] = "[npmx_driver]Fuel gauge not initialized, initializing...\n"; /* ROM 0x716df8 */
static const char s_chg_null[] = "p_charger is null!\n"; /* ROM 0x78150c */
static const char c_chg_null[] = "[npmx_driver]p_charger is null!\n"; /* ROM 0x757230 */
static const char s_ship_null[] = "p_ship is NULL\n"; /* ROM 0x787b60 */
static const char c_ship_null[] = "[npmx_driver]p_ship is NULL\n"; /* ROM 0x7629d0 */
static const char s_ship_fail[] = "npmx_ship_task_trigger failed\n"; /* ROM 0x7629f0 */
static const char c_ship_fail[] = "[npmx_driver]npmx_ship_task_trigger failed\n"; /* ROM 0x740aa4 */
static const char s_syslabel[] = "npmx_get_device_id: read SYSLABEL failed, err=%d"; /* ROM 0x72b60c */
static const char c_syslabel[] = "[npmx_driver]npmx_get_device_id: read SYSLABEL failed, err=%d"; /* ROM 0x70d4e4 */

/* Stock tables. */
static const npmx_timer_config_t watchdog_timer_config = {2u, 1u, 0x3c00u}; /* ROM 0x78b624: ~30.7 s */
static const npmx_adc_ntc_config_t ntc_config_template = {0u, 4250u};      /* ROM 0x78de1c */
static const nrf_fuel_gauge_init_parameters_t fuel_gauge_init_template = { /* ROM 0x779c7c */
    0.0f, 0.0f, 0.0f, g2_npm1300_battery_model, NULL, NULL};
static const float fuel_gauge_charge_current_limit = 0.096f; /* ROM 0x78f31c, amperes */
static const float fuel_gauge_term_current = 0.0096f;        /* ROM 0x78f320, amperes */

/* Common stock log pair: full record when flag bit 1 is set, compressed
 * record when bit 0 or bit 2 is set. type = level << 26 | argc << 22. */
#define NPMX_LOG0(level, fn, line, plain, compact)                                     \
    do {                                                                               \
        if (audio_log_flags() & 2u)                                                    \
            audio_log_extended((level), module_tag, source_file, (fn), (line), (plain)); \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                      \
            (void)compress_log_output((uint32_t)(level) << 26, (compact), (compact));  \
    } while (0)

#define NPMX_LOG1(level, fn, line, plain, compact, value)                              \
    do {                                                                               \
        if (audio_log_flags() & 2u)                                                    \
            audio_log_extended((level), module_tag, source_file, (fn), (line), (plain), (value)); \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                      \
            (void)compress_log_output(((uint32_t)(level) << 26) | (1u << 22), (compact), (compact), (value)); \
    } while (0)

/* npmx backend read callback: two-byte big-endian register address, then a
 * repeated-start read of len bytes. */
uint32_t npmx_backend_i2c_read_511002(void *p_context, uint32_t register_address,
                                      uint8_t *p_data, size_t len) {
    (void)p_context;
    uint8_t addr[2] = {(uint8_t)(register_address >> 8), (uint8_t)register_address};
    if (len > NPMX_BACKEND_MAX_LEN)
        return NPMX_ERROR_INVALID_PARAM;
    uint32_t status = hal_i2c_transfer_full(G2_NPM1300_I2C_BUS, G2_NPM1300_I2C_ADDR, addr, 2u, p_data, len);
    if (status == 0u)
        return NPMX_SUCCESS;
    NPMX_LOG1(1u, fn_i2c_read, 0xf1u, s_i2c_read, c_i2c_read, status);
    return NPMX_ERROR_IO;
}

/* npmx backend write callback: address and payload as one joined write. */
uint32_t npmx_backend_i2c_write_511084(void *p_context, uint32_t register_address,
                                       uint8_t *p_data, size_t len) {
    (void)p_context;
    uint8_t addr[2] = {(uint8_t)(register_address >> 8), (uint8_t)register_address};
    if (len > NPMX_BACKEND_MAX_LEN)
        return NPMX_ERROR_INVALID_PARAM;
    uint32_t status = hal_i2c_transfer_joined(G2_NPM1300_I2C_BUS, G2_NPM1300_I2C_ADDR, addr, 2u, p_data, len);
    if (status == 0u)
        return NPMX_SUCCESS;
    NPMX_LOG1(1u, fn_i2c_write, 0x130u, s_i2c_write, c_i2c_write, status);
    return NPMX_ERROR_IO;
}

/* Fill the backend record, run npmx_core_init with restore_values = true,
 * then mask every event of all eight event groups. */
void npmx_backend_init_511108(void) {
    g2_npmx_backend.read = npmx_backend_i2c_read_511002;
    g2_npmx_backend.write = npmx_backend_i2c_write_511084;
    g2_npmx_backend.p_context = g2_npmx_backend_context;
    uint32_t err = npmx_core_init(&g2_npmx_instance, &g2_npmx_backend, NULL, true);
    if (err != NPMX_SUCCESS)
        NPMX_LOG1(1u, fn_backend_init, 0x169u, s_core_init, c_core_init, err);
    for (uint32_t group = 0; group < NPMX_EVENT_GROUP_COUNT; group++) {
        err = npmx_core_event_interrupt_disable(&g2_npmx_instance, group, 0xffu);
        if (err != NPMX_SUCCESS)
            NPMX_LOG1(1u, fn_backend_init, 0x171u, s_irq_disable, c_irq_disable, err);
    }
}

/* PMIC GPIO1 becomes the interrupt output (NPMX_GPIO_MODE_OUTPUT_IRQ = 5). */
void npmx_int_pin_configure_5111e6(void) {
    uint32_t err = npmx_gpio_mode_set(npmx_gpio_get(&g2_npmx_instance, 1u), 5u);
    if (err != NPMX_SUCCESS)
        NPMX_LOG1(1u, fn_int_pin, 0x17cu, s_gpio_mode, c_gpio_mode, err);
}

void watchdog_timer_callback_51124c(struct npmx_instance *p_pm, uint32_t type, uint8_t mask) {
    (void)p_pm;
    (void)type;
    (void)mask;
    NPMX_LOG0(3u, fn_wdt_cb, 0x182u, s_wdt_triggered, c_wdt_triggered);
}

/* VBUSIN voltage events: on attach re-apply the VBUS current limit and tell
 * the box-detect service; on removal tell box-detect. */
void vbusin_voltage_callback_511294(struct npmx_instance *p_pm, uint32_t type, uint8_t mask) {
    (void)type;
    if (mask & NPMX_EVENT_VBUSIN_DETECTED) {
        NPMX_LOG0(4u, fn_vbus_cb, 0x189u, s_vbus_on, c_vbus_on);
        (void)npmx_vbusin_task_trigger(npmx_vbusin_get(p_pm, 0u), 0u);
        box_detect_vbus_connected_4ac130();
    }
    if (mask & NPMX_EVENT_VBUSIN_REMOVED) {
        NPMX_LOG0(4u, fn_vbus_cb, 0x190u, s_vbus_off, c_vbus_off);
        box_detect_vbus_removed_4ac154();
    }
}

/* Charger profile: 96 mA charge, 1000 mA discharge limit, 4.45 V normal and
 * 4.00 V warm termination, VBUS limit 500 mA, 100 kOhm NTC (beta 4250), IBAT
 * measurement on; watchdog in reset mode with the warning event routed to
 * watchdog_timer_callback. */
void npmx_application_configure_511342(void) {
    void *timer = npmx_timer_get(&g2_npmx_instance, 0u);
    void *charger = npmx_charger_get(&g2_npmx_instance, 0u);
    void *vbusin = npmx_vbusin_get(&g2_npmx_instance, 0u);
    void *adc = npmx_adc_get(&g2_npmx_instance, 0u);
    uint32_t err;

    npmx_core_register_cb(&g2_npmx_instance, (void *)watchdog_timer_callback_51124c, NPMX_EVENT_GROUP_SHIPHOLD);
    err = npmx_core_event_interrupt_enable(&g2_npmx_instance, NPMX_EVENT_GROUP_SHIPHOLD,
                                                  NPMX_EVENT_SHIPHOLD_WATCHDOG_WARN);
    if (err != NPMX_SUCCESS)
        NPMX_LOG1(1u, fn_app_cfg, 0x1aau, s_irq_enable, c_irq_enable, err);

    npmx_timer_config_t timer_config = watchdog_timer_config;
    err = npmx_timer_config_set(timer, &timer_config);
    if (err != NPMX_SUCCESS)
        NPMX_LOG1(1u, fn_app_cfg, 0x1b8u, s_timer_cfg, c_timer_cfg, err);

    npmx_core_register_cb(&g2_npmx_instance, (void *)vbusin_voltage_callback_511294, NPMX_EVENT_GROUP_VBUSIN_VOLTAGE);
    err = npmx_core_event_interrupt_enable(&g2_npmx_instance, NPMX_EVENT_GROUP_VBUSIN_VOLTAGE,
                                                  NPMX_EVENT_VBUSIN_DETECTED | NPMX_EVENT_VBUSIN_REMOVED);
    if (err != NPMX_SUCCESS)
        NPMX_LOG1(1u, fn_app_cfg, 0x1c9u, s_irq_enable, c_irq_enable, err);

    err = npmx_charger_charging_current_set(charger, 96u);
    if (err != NPMX_SUCCESS)
        NPMX_LOG1(1u, fn_app_cfg, 0x1cfu, s_chg_cur, c_chg_cur, err);
    err = npmx_charger_discharging_current_set(charger, 1000u);
    if (err != NPMX_SUCCESS)
        NPMX_LOG1(1u, fn_app_cfg, 0x1d5u, s_dischg_cur, c_dischg_cur, err);
    err = npmx_charger_termination_normal_voltage_set(charger, npmx_charger_voltage_convert(4450u));
    if (err != NPMX_SUCCESS)
        NPMX_LOG1(1u, fn_app_cfg, 0x1dcu, s_term_normal, c_term_normal, err);
    err = npmx_charger_termination_warm_voltage_set(charger, npmx_charger_voltage_convert(4000u));
    if (err != NPMX_SUCCESS)
        NPMX_LOG1(1u, fn_app_cfg, 0x1e3u, s_term_warm, c_term_warm, err);
    err = npmx_charger_module_enable_set(charger, 1u); /* NPMX_CHARGER_MODULE_CHARGER_MASK */
    if (err != NPMX_SUCCESS)
        NPMX_LOG1(1u, fn_app_cfg, 0x1eau, s_chg_enable, c_chg_enable, err);

    err = npmx_vbusin_current_limit_set(vbusin, npmx_vbusin_current_convert(500u));
    if (err != NPMX_SUCCESS)
        NPMX_LOG1(1u, fn_app_cfg, 0x1f4u, s_vbus_ilim, c_vbus_ilim, err);
    err = npmx_vbusin_task_trigger(vbusin, 0u); /* APPLY_CURRENT_LIMIT */
    if (err != NPMX_SUCCESS)
        NPMX_LOG1(1u, fn_app_cfg, 0x1fau, s_vbus_task, c_vbus_task, err);

    npmx_adc_ntc_config_t ntc_config = ntc_config_template;
    ntc_config.type = npmx_adc_ntc_type_convert(100000u);
    err = npmx_adc_ntc_config_set(adc, &ntc_config);
    if (err != NPMX_SUCCESS)
        NPMX_LOG1(1u, fn_app_cfg, 0x204u, s_ntc_cfg, c_ntc_cfg, err);
    err = npmx_adc_ibat_meas_enable_set(adc, true);
    if (err != NPMX_SUCCESS)
        NPMX_LOG1(1u, fn_app_cfg, 0x20au, s_ibat_meas, c_ibat_meas, err);
    err = npmx_adc_task_trigger(adc, 0u);
    if (err != NPMX_SUCCESS)
        NPMX_LOG1(1u, fn_app_cfg, 0x212u, s_adc_task, c_adc_task, err);
    err = npmx_adc_task_trigger(adc, 1u);
    if (err != NPMX_SUCCESS)
        NPMX_LOG1(1u, fn_app_cfg, 0x216u, s_adc_task, c_adc_task, err);
}

/* Timer 0 task 0 (NPMX_TIMER_TASK_ENABLE) starts the PMIC watchdog. */
void npmx_watchdog_enable_511882(void) {
    uint32_t err = npmx_timer_task_trigger(npmx_timer_get(&g2_npmx_instance, 0u), 0u);
    if (err != NPMX_SUCCESS)
        NPMX_LOG1(1u, fn_wdt_enable, 0x223u, s_wdt_enable, c_wdt_enable, err);
}

/* Read all ADC channels (V, A, degC), the charger status byte, and re-arm the
 * single-shot VBAT and NTC conversions. Returns the first failing npmx code. */
uint32_t npmx_get_adc_measurements_511990(float *voltage, float *current, float *temp,
                                          uint8_t *charger_status) {
    void *adc = npmx_adc_get(&g2_npmx_instance, 0u);
    void *charger = npmx_charger_get(&g2_npmx_instance, 0u);
    uint32_t ret = NPMX_SUCCESS;
    npmx_adc_meas_all_t meas;

    uint32_t err = npmx_adc_meas_all_get(adc, &meas);
    if (err == NPMX_SUCCESS) {
        *current = (float)meas.values[6] / 1000.0f;
        *temp = (float)meas.values[1] / 1000.0f;
        *voltage = (float)meas.values[0] / 1000.0f;
        err = npmx_charger_status_get(charger, charger_status);
        if (err != NPMX_SUCCESS) {
            NPMX_LOG1(1u, fn_adc_meas, 0x262u, s_chg_status, c_chg_status, err);
            return err;
        }
    } else {
        NPMX_LOG1(2u, fn_adc_meas, 0x251u, s_meas_all, c_meas_all, err);
        ret = err;
    }
    err = npmx_adc_task_trigger(adc, 0u);
    if (err != NPMX_SUCCESS) {
        NPMX_LOG1(1u, fn_adc_meas, 0x26au, s_adc_task, c_adc_task, err);
        return err;
    }
    err = npmx_adc_task_trigger(adc, 1u);
    if (err != NPMX_SUCCESS) {
        NPMX_LOG1(1u, fn_adc_meas, 0x270u, s_adc_task, c_adc_task, err);
        return err;
    }
    return ret;
}

/* Seed nrf_fuel_gauge with the first ADC sample. A failing
 * nrf_fuel_gauge_init is logged and initialisation continues. */
void initialize_fuel_gauge_511c24(void) {
    nrf_fuel_gauge_init_parameters_t params;
    uint8_t charger_status;
    int32_t ret;

    (void)audio_uart_display_area_copy_439c04(&params, &fuel_gauge_init_template, sizeof(params));
    if (nrf_fuel_gauge_variant != 1u) {
        NPMX_LOG0(1u, fn_fg_init, 0x2a0u, s_fg_variant, c_fg_variant);
        return;
    }
    uint32_t err = npmx_get_adc_measurements_511990(&params.v0, &params.i0, &params.t0, &charger_status);
    if (err != NPMX_SUCCESS) {
        NPMX_LOG1(1u, fn_fg_init, 0x2a6u, s_get_adc, c_get_adc, err);
        return;
    }
    ret = nrf_fuel_gauge_init_43c150(&params, NULL);
    if (ret != 0)
        NPMX_LOG1(1u, fn_fg_init, 0x2acu, s_fg_init, c_fg_init, ret);

    float charge_current_limit = fuel_gauge_charge_current_limit;
    ret = nrf_fuel_gauge_ext_state_update_55f74c(FG_EXT_CHARGE_CURRENT_LIMIT, &charge_current_limit);
    if (ret != 0) {
        NPMX_LOG1(1u, fn_fg_init, 0x2b3u, s_fg_ext, c_fg_ext, ret);
        return;
    }
    float term_current = fuel_gauge_term_current;
    ret = nrf_fuel_gauge_ext_state_update_55f74c(FG_EXT_TERM_CURRENT, &term_current);
    if (ret != 0) {
        NPMX_LOG1(1u, fn_fg_init, 0x2bcu, s_fg_ext, c_fg_ext, ret);
        return;
    }
    ret = charge_status_inform_fuel_gauge_511b74(charger_status);
    if (ret != 0) {
        NPMX_LOG1(1u, fn_fg_init, 0x2c2u, s_fg_inform, c_fg_inform, ret);
        return;
    }
    fuel_gauge_ref_time_update_512892();
    g2_fuel_gauge_initialized = 1u;

    NPMX_LOG0(4u, fn_fg_init, 0x2c9u, s_fg_done, c_fg_done);
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, fn_fg_init, 0x2cau, s_fg_v0,
                           (double)params.v0, (double)params.i0, (double)params.t0);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10c00000u, c_fg_v0, c_fg_v0,
                                  (double)params.v0, (double)params.i0, (double)params.t0);
    NPMX_LOG1(4u, fn_fg_init, 0x2cbu, s_fg_version, c_fg_version, nrf_fuel_gauge_version);
    NPMX_LOG1(4u, fn_fg_init, 0x2ccu, s_fg_date, c_fg_date, nrf_fuel_gauge_build_date);
}

/* Periodic gauge step. SoC outside [0, 150) reads as 0 and is capped at 100.
 * Telemetry +0x15 is set while SoC is in [93.5,94), [94.5,95) or [95.5,96).
 * Telemetry +4 SoC %, +8 mV, +0xc mA, +0x10 centi-degC. */
__attribute__((pcs("aapcs-vfp"))) void process_fuel_gauge_51201c(float t_delta) {
    void *vbusin = npmx_vbusin_get(&g2_npmx_instance, 0u);
    float voltage, current, temp;
    uint8_t charger_status;
    uint8_t vbus_status;
    int32_t ret;

    uint32_t err = npmx_get_adc_measurements_511990(&voltage, &current, &temp, &charger_status);
    if (err != NPMX_SUCCESS) {
        NPMX_LOG1(2u, fn_fg_process, 0x30cu, s_get_adc, c_get_adc, err);
        return;
    }
    err = npmx_vbusin_vbus_status_get(vbusin, &vbus_status);
    if (err != NPMX_SUCCESS) {
        NPMX_LOG1(1u, fn_fg_process, 0x312u, s_vbus_status, c_vbus_status, err);
        return;
    }
    if (vbus_status & 1u)
        ret = nrf_fuel_gauge_ext_state_update_55f74c(FG_EXT_VBUS_CONNECTED, NULL);
    else
        ret = nrf_fuel_gauge_ext_state_update_55f74c(FG_EXT_VBUS_DISCONNECTED, NULL);
    if (ret != 0)
        NPMX_LOG1(1u, fn_fg_process, 0x31cu, s_fg_ext, c_fg_ext, ret);

    float soc = nrf_fuel_gauge_process_55f848(voltage, current, temp, t_delta, NULL);
    (void)nrf_fuel_gauge_tte_get_55f994();
    (void)nrf_fuel_gauge_ttf_get_55f9a0();
    if (soc < 0.0f || !(soc < 150.0f))
        soc = 0.0f;
    else if (!(soc < 100.0f))
        soc = 100.0f;

    uint8_t *telemetry = (uint8_t *)&g2_charger_telemetry;
    if ((soc >= 93.5f && soc < 94.0f) || (soc >= 94.5f && soc < 95.0f) || (soc >= 95.5f && soc < 96.0f))
        telemetry[0x15] = 1u;
    else
        telemetry[0x15] = 0u;
    g2_charger_telemetry.soc = (int32_t)soc;
    g2_charger_telemetry.voltage_mv = (int32_t)(voltage * 1000.0f);
    g2_charger_telemetry.avg_current_ma = (int32_t)(current * 1000.0f);
    g2_charger_telemetry.temperature = (int32_t)(temp * 100.0f);

    if (charger_status != g2_npmx_last_charger_status) {
        ret = charge_status_inform_fuel_gauge_511b74(charger_status);
        if (ret != 0)
            NPMX_LOG1(1u, fn_fg_process, 0x374u, s_fg_inform, c_fg_inform, ret);
    }
    g2_npmx_last_charger_status = charger_status;
}

/* BUCK2: software-selected output at enum 0x15 (3.1 V), then enable. */
void configure_buck2_voltage_51238c(void) {
    void *buck = npmx_buck_get(&g2_npmx_instance, 1u);
    if (buck == NULL) {
        NPMX_LOG0(1u, fn_buck2, 0x3abu, s_buck2_null, c_buck2_null);
        return;
    }
    (void)npmx_buck_vout_select_set(buck, 1u);
    (void)npmx_buck_normal_voltage_set(buck, 0x15u);
    (void)npmx_buck_task_trigger(buck, 0u);
}

/* LDSW1 in LDO mode at enum 8 (1.8 V), then enable. */
void configure_lsdw1_voltage_51247c(void) {
    void *ldsw = npmx_ldsw_get(&g2_npmx_instance, 0u);
    if (ldsw == NULL) {
        NPMX_LOG0(1u, fn_lsdw1, 0x3ddu, s_ldsw1_null, c_ldsw1_null);
        return;
    }
    (void)npmx_ldsw_mode_set(ldsw, 1u);
    (void)npmx_ldsw_ldo_voltage_set(ldsw, 8u);
    (void)npmx_ldsw_task_trigger(ldsw, 0u);
}

/* Board record byte 0 of radio-mode slot 1 == 6 selects the extra LDSW2 step.
 * Between the first log and backend init the stock keeps an empty inlined
 * call with arguments (7, 0) that compiled to two NOPs. */
void npmx_main_driver_init_512644(void) {
    NPMX_LOG0(4u, fn_main_init, 0x430u, s_init_start, c_init_start);
    const uint8_t *board = audio_ble_hci_radio_mode_state_50938e(1u);
    NPMX_LOG0(4u, fn_main_init, 0x440u, s_init_backend, c_init_backend);
    npmx_backend_init_511108();
    NPMX_LOG0(4u, fn_main_init, 0x442u, s_init_int_pin, c_init_int_pin);
    npmx_int_pin_configure_5111e6();
    NPMX_LOG0(4u, fn_main_init, 0x444u, s_init_bchg, c_init_bchg);
    npmx_bchg_vbat_low_charge_enable_512a34();
    npmx_bchg_ntc_enable_512a4c();
    NPMX_LOG0(4u, fn_main_init, 0x447u, s_init_app, c_init_app);
    npmx_application_configure_511342();
    g2_delay_ms_4910f4(1u);
    NPMX_LOG0(4u, fn_main_init, 0x44du, s_init_done, c_init_done);
    initialize_fuel_gauge_511c24();
    g2_delay_ms_4910f4(50u);
    configure_buck2_voltage_51238c();
    configure_lsdw1_voltage_51247c();
    if (board[0] == 6u)
        display_driver_uled_type0_mode4_finish_5125a8();
}

void check_fuel_gauge_init_51283c(void) {
    if (g2_fuel_gauge_initialized != 0u)
        return;
    NPMX_LOG0(2u, fn_fg_check, 0x46fu, s_fg_not_init, c_fg_not_init);
    initialize_fuel_gauge_511c24();
}

void fuel_gauge_ref_time_update_512892(void) {
    g2_fuel_gauge_ref_time = osKernelGetTickCount();
}

/* Mask 0xf: charger, full-cool, recharge and NTC-limit modules. */
void npmx_charger_disable_5128f8(void) {
    void *charger = npmx_charger_get(&g2_npmx_instance, 0u);
    if (charger == NULL) {
        NPMX_LOG0(1u, fn_chg_disable, 0x4c7u, s_chg_null, c_chg_null);
        return;
    }
    uint32_t err = npmx_charger_module_disable_set(charger, 0xfu);
    if (err != NPMX_SUCCESS)
        NPMX_LOG1(1u, fn_chg_disable, 0x4d3u, s_chg_disable, c_chg_disable, err);
}

void npmx_charger_enable_51299c(void) {
    void *charger = npmx_charger_get(&g2_npmx_instance, 0u);
    if (charger == NULL) {
        NPMX_LOG0(1u, fn_chg_enable, 0x4ddu, s_chg_null, c_chg_null);
        return;
    }
    uint32_t err = npmx_charger_module_enable_set(charger, 0xfu);
    if (err != NPMX_SUCCESS)
        NPMX_LOG1(1u, fn_chg_enable, 0x4e8u, s_chg_enable, c_chg_enable, err);
}

/* BCHGVBATLOWCHARGE = 1: allow charging from a deeply discharged battery. */
void npmx_bchg_vbat_low_charge_enable_512a34(void) {
    uint8_t value = 1u;
    (void)npmx_backend_register_write(&g2_npmx_backend, NPM1300_BCHGVBATLOWCHARGE, &value, 1u);
}

/* BCHGDISABLECLR = 2: clear DISABLENTC so the charger honours the NTC. */
void npmx_bchg_ntc_enable_512a4c(void) {
    uint8_t value = 2u;
    (void)npmx_backend_register_write(&g2_npmx_backend, NPM1300_BCHGDISABLECLR, &value, 1u);
}

/* Returns 0, -1 (no ship instance) or -2 (task trigger failed). Task 2 is
 * NPMX_SHIP_TASK_SHIPMODE. */
int32_t npmx_enter_ship_mode_512a70(void) {
    void *ship = npmx_ship_get(&g2_npmx_instance, 0u);
    if (ship == NULL) {
        NPMX_LOG0(1u, fn_ship, 0x504u, s_ship_null, c_ship_null);
        return -1;
    }
    if (npmx_ship_task_trigger(ship, 2u) == NPMX_SUCCESS)
        return 0;
    NPMX_LOG0(1u, fn_ship, 0x50au, s_ship_fail, c_ship_fail);
    return -2;
}

/* SYSLABEL (0x0101); 0x00 and 0xff read as 0x13. Returns 0, -1 for a NULL
 * output, -2 on a bus error. */
int32_t npmx_get_device_id_512b20(uint32_t *device_id) {
    if (device_id == NULL)
        return -1;
    uint8_t label = 0u;
    uint32_t err = npmx_backend_register_read(&g2_npmx_backend, NPM1300_SYSLABEL, &label, 1u);
    if (err != NPMX_SUCCESS) {
        NPMX_LOG1(1u, fn_device_id, 0x51du, s_syslabel, c_syslabel, err);
        return -2;
    }
    if (label == 0u || label == 0xffu)
        label = 0x13u;
    *device_id = label;
    return 0;
}
