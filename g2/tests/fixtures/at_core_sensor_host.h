#ifndef OPEN_CFW_AT_CORE_SENSOR_HOST_H
#define OPEN_CFW_AT_CORE_SENSOR_HOST_H

#include <stdint.h>

/* Fixture copies of the retained stock literals (exact stock contents). */
extern const char open_cfw_test_product_name[];
extern const char open_cfw_test_info_product_format[];
extern const char open_cfw_test_info_hardware_format[];
extern const char open_cfw_test_software_version[];
extern const char open_cfw_test_info_software_format[];
extern const char open_cfw_test_info_codec_format[];
extern const char open_cfw_test_info_touch_format[];
extern const char open_cfw_test_compile_date[];
extern const char open_cfw_test_compile_time[];
extern const char open_cfw_test_info_compile_format[];
extern const char open_cfw_test_info_sn_format[];
extern const char open_cfw_test_info_ble_name_format[];
extern const char open_cfw_test_info_ble_addr_format[];
extern const char open_cfw_test_info_response[];
extern const char open_cfw_test_reset_response[];
extern const char open_cfw_test_psn_echo_format[];
extern const char open_cfw_test_psn_error_format[];
extern const char open_cfw_test_psn_response[];
extern const char open_cfw_test_imu_rawdata_format[];
extern const char open_cfw_test_imu_rawdata_error[];
extern const char open_cfw_test_imu_euler_format[];
extern const char open_cfw_test_scrn_x_response[];
extern const char open_cfw_test_scrn_y_error[];
extern const char open_cfw_test_scrn_y_response[];
extern const char open_cfw_test_als_read_format[];
extern const char open_cfw_test_als_format[];
extern const char open_cfw_test_brightness_format[];
extern const char open_cfw_test_als_scale_read_format[];
extern const char open_cfw_test_brightness_read_format[];

/* Programmable provider state. */
extern volatile int32_t open_cfw_test_lux_base;
extern uint32_t open_cfw_test_als_value;
extern uint32_t open_cfw_test_als_scale;
extern uint32_t open_cfw_test_brightness;
extern float open_cfw_test_euler_angles[3];
extern const uint8_t open_cfw_test_ble_address[6];
extern const char open_cfw_test_ble_name[];
extern const char open_cfw_test_hardware_version[];
extern const char open_cfw_test_codec_version[];
extern const char open_cfw_test_touch_version[];
extern const char open_cfw_test_psn_value[];

/* Spy state. */
extern char open_cfw_test_output_log[4096];
extern unsigned int open_cfw_test_output_count;
extern unsigned int open_cfw_test_reset_count;
extern unsigned int open_cfw_test_snprintf_count;
extern unsigned int open_cfw_test_psn_read_count;
extern int open_cfw_test_psn_read_slots[8];
extern unsigned int open_cfw_test_psn_write_count;
extern int open_cfw_test_psn_write_slot;
extern char open_cfw_test_psn_write_value[32];
extern unsigned int open_cfw_test_imu_rawdata_count;
extern int open_cfw_test_imu_rawdata_values[8];
extern unsigned int open_cfw_test_screen_height_count;
extern int open_cfw_test_screen_height_values[8];
extern unsigned int open_cfw_test_als_enable_count;
extern int open_cfw_test_als_enable_values[8];
extern unsigned int open_cfw_test_als_disable_count;
extern int open_cfw_test_als_disable_values[8];
extern unsigned int open_cfw_test_brightness_write_count;
extern int open_cfw_test_brightness_write_values[8];

void open_cfw_test_reset(void);

#define OPEN_CFW_AT_PRODUCT_NAME open_cfw_test_product_name
#define OPEN_CFW_AT_INFO_PRODUCT_FORMAT open_cfw_test_info_product_format
#define OPEN_CFW_AT_INFO_HARDWARE_FORMAT open_cfw_test_info_hardware_format
#define OPEN_CFW_AT_SOFTWARE_VERSION open_cfw_test_software_version
#define OPEN_CFW_AT_INFO_SOFTWARE_FORMAT open_cfw_test_info_software_format
#define OPEN_CFW_AT_INFO_CODEC_FORMAT open_cfw_test_info_codec_format
#define OPEN_CFW_AT_INFO_TOUCH_FORMAT open_cfw_test_info_touch_format
#define OPEN_CFW_AT_COMPILE_DATE open_cfw_test_compile_date
#define OPEN_CFW_AT_COMPILE_TIME open_cfw_test_compile_time
#define OPEN_CFW_AT_INFO_COMPILE_FORMAT open_cfw_test_info_compile_format
#define OPEN_CFW_AT_INFO_SN_FORMAT open_cfw_test_info_sn_format
#define OPEN_CFW_AT_INFO_BLE_NAME_FORMAT open_cfw_test_info_ble_name_format
#define OPEN_CFW_AT_INFO_BLE_ADDR_FORMAT open_cfw_test_info_ble_addr_format
#define OPEN_CFW_AT_INFO_RESPONSE open_cfw_test_info_response
#define OPEN_CFW_AT_RESET_RESPONSE open_cfw_test_reset_response
#define OPEN_CFW_AT_PSN_ECHO_FORMAT open_cfw_test_psn_echo_format
#define OPEN_CFW_AT_PSN_ERROR_FORMAT open_cfw_test_psn_error_format
#define OPEN_CFW_AT_PSN_RESPONSE open_cfw_test_psn_response
#define OPEN_CFW_AT_IMU_RAWDATA_FORMAT open_cfw_test_imu_rawdata_format
#define OPEN_CFW_AT_IMU_RAWDATA_ERROR open_cfw_test_imu_rawdata_error
#define OPEN_CFW_AT_IMU_EULER_FORMAT open_cfw_test_imu_euler_format
#define OPEN_CFW_AT_SCRN_X_RESPONSE open_cfw_test_scrn_x_response
#define OPEN_CFW_AT_SCRN_Y_ERROR open_cfw_test_scrn_y_error
#define OPEN_CFW_AT_SCRN_Y_RESPONSE open_cfw_test_scrn_y_response
#define OPEN_CFW_AT_ALS_READ_FORMAT open_cfw_test_als_read_format
#define OPEN_CFW_AT_ALS_FORMAT open_cfw_test_als_format
#define OPEN_CFW_AT_BRIGHTNESS_FORMAT open_cfw_test_brightness_format
#define OPEN_CFW_AT_ALS_SCALE_READ_FORMAT open_cfw_test_als_scale_read_format
#define OPEN_CFW_AT_BRIGHTNESS_READ_FORMAT \
    open_cfw_test_brightness_read_format

#define OPEN_CFW_AT_LUX_BASE open_cfw_test_lux_base

void open_cfw_test_at_output(const char *format, ...);
uint32_t open_cfw_test_at_parameter_length(const char *parameter);
int open_cfw_test_at_parse_integer(const char *parameter);
int open_cfw_test_snprintf(
    char *buffer, uint32_t capacity, const char *format, ...
);
const char *open_cfw_test_hardware_version_get(void);
const char *open_cfw_test_codec_version_get(void);
const char *open_cfw_test_touch_version_get(void);
const char *open_cfw_test_psn_read(int slot);
const uint8_t *open_cfw_test_ble_address_get(void);
const char *open_cfw_test_ble_name_get(void);
void open_cfw_test_system_reset(void);
void open_cfw_test_psn_write(int slot, const char *value);
void open_cfw_test_imu_rawdata(int enable);
const float *open_cfw_test_imu_euler(void);
void open_cfw_test_screen_height(int height);
uint32_t open_cfw_test_als_read(void);
void open_cfw_test_als_enable(int state);
void open_cfw_test_als_disable(int state);
void open_cfw_test_brightness_write(int brightness);
uint32_t open_cfw_test_als_scale_read(void);
uint32_t open_cfw_test_brightness_read(void);

#define OPEN_CFW_AT_OUTPUT(...) open_cfw_test_at_output(__VA_ARGS__)
#define OPEN_CFW_AT_PARAMETER_LENGTH(parameter) \
    open_cfw_test_at_parameter_length((parameter))
#define OPEN_CFW_AT_PARSE_INTEGER(parameter) \
    open_cfw_test_at_parse_integer((parameter))
#define OPEN_CFW_AT_SNPRINTF(...) open_cfw_test_snprintf(__VA_ARGS__)
#define OPEN_CFW_AT_HARDWARE_VERSION() open_cfw_test_hardware_version_get()
#define OPEN_CFW_AT_CODEC_VERSION() open_cfw_test_codec_version_get()
#define OPEN_CFW_AT_TOUCH_VERSION() open_cfw_test_touch_version_get()
#define OPEN_CFW_AT_PSN_READ(slot) open_cfw_test_psn_read((slot))
#define OPEN_CFW_AT_BLE_ADDRESS() open_cfw_test_ble_address_get()
#define OPEN_CFW_AT_BLE_NAME() open_cfw_test_ble_name_get()
#define OPEN_CFW_AT_SYSTEM_RESET() open_cfw_test_system_reset()
#define OPEN_CFW_AT_PSN_WRITE(slot, value) \
    open_cfw_test_psn_write((slot), (value))
#define OPEN_CFW_AT_IMU_RAWDATA(enable) open_cfw_test_imu_rawdata((enable))
#define OPEN_CFW_AT_IMU_EULER() open_cfw_test_imu_euler()
#define OPEN_CFW_AT_SCREEN_HEIGHT(height) \
    open_cfw_test_screen_height((height))
#define OPEN_CFW_AT_ALS_READ() open_cfw_test_als_read()
#define OPEN_CFW_AT_ALS_ENABLE(state) open_cfw_test_als_enable((state))
#define OPEN_CFW_AT_ALS_DISABLE(state) open_cfw_test_als_disable((state))
#define OPEN_CFW_AT_BRIGHTNESS_WRITE(brightness) \
    open_cfw_test_brightness_write((brightness))
#define OPEN_CFW_AT_ALS_SCALE_READ() open_cfw_test_als_scale_read()
#define OPEN_CFW_AT_BRIGHTNESS_READ() open_cfw_test_brightness_read()

#endif
