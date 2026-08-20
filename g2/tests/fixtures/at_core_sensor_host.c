#include "at_core_sensor_host.h"

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

const char open_cfw_test_product_name[] = "S200";
const char open_cfw_test_info_product_format[] = "Product name:     [%s]\r\n";
const char open_cfw_test_info_hardware_format[] = "Hardware version: [%s]\r\n";
const char open_cfw_test_software_version[] = "2.2.6.10";
const char open_cfw_test_info_software_format[] = "Software version: [%s]\r\n";
const char open_cfw_test_info_codec_format[] = "Codec version:    [%s]\r\n";
const char open_cfw_test_info_touch_format[] = "Touch version:    [%s]\r\n";
const char open_cfw_test_compile_date[] = "Jul  6 2026";
const char open_cfw_test_compile_time[] = "21:37:47";
const char open_cfw_test_info_compile_format[] = "Compile time:     [%s %s]\r\n";
const char open_cfw_test_info_sn_format[] = "Product SN:       [%s]\r\n";
const char open_cfw_test_info_ble_name_format[] = "BLE NAME:         [%s]\r\n";
const char open_cfw_test_info_ble_addr_format[] =
    "BLE ADDR:         [%02X:%02X:%02X:%02X:%02X:%02X]\r\n";
const char open_cfw_test_info_response[] = "INFO+OK\r\n";
const char open_cfw_test_reset_response[] = "RESET+OK\r\n";
const char open_cfw_test_psn_echo_format[] = "%s";
const char open_cfw_test_psn_error_format[] =
    "AT^PSN: set PSN: The parameter is incorrect. Please enter the correct "
    "command (len %d)\r\n";
const char open_cfw_test_psn_response[] = "PSN+OK\r\n";
const char open_cfw_test_imu_rawdata_format[] = "AT^IMU_RAWDATA+OK:type=%d\r\n";
const char open_cfw_test_imu_rawdata_error[] =
    "AT^IMU_RAWDATA+ERROR: invalid parameter, use 1 to start or 0 to stop\r\n";
const char open_cfw_test_imu_euler_format[] =
    "AT^IMU_EULER+OK:roll=%.2f,pitch=%.2f,yaw=%.2f\r\n";
const char open_cfw_test_scrn_x_response[] = "AT^SCRN_X+OK\r\n";
const char open_cfw_test_scrn_y_error[] =
    "AT^SCRN_Y Error,height value must be 1 - 192.\r\n";
const char open_cfw_test_scrn_y_response[] = "AT^SCRN_Y+OK\r\n";
const char open_cfw_test_als_read_format[] =
    "AT^ALS_READ+OK:ALS\xe5\x80\xbc=%u, LUX_BASE=%d\r\n";
const char open_cfw_test_als_format[] = "AT^ALS+OK:enable=%d\r\n";
const char open_cfw_test_brightness_format[] =
    "AT^BRIGHTNESS+OK:brightness=%d\r\n";
const char open_cfw_test_als_scale_read_format[] =
    "AT^ALS_SCALE_READ+OK:scale_q10=%u\r\n";
const char open_cfw_test_brightness_read_format[] =
    "AT^BRIGHTNESS_READ+OK:brightness=%u\r\n";

volatile int32_t open_cfw_test_lux_base = -77;
uint32_t open_cfw_test_als_value = 1234u;
uint32_t open_cfw_test_als_scale = 1024u;
uint32_t open_cfw_test_brightness = 55u;
float open_cfw_test_euler_angles[3] = {1.5f, -2.25f, 3.0f};
const uint8_t open_cfw_test_ble_address[6] =
    {0xaau, 0xbbu, 0xccu, 0x11u, 0x22u, 0x33u};
const char open_cfw_test_ble_name[] = "G2";
const char open_cfw_test_hardware_version[] = "1.0.0.0";
const char open_cfw_test_codec_version[] = "2.0.0.0";
const char open_cfw_test_touch_version[] = "3.0.0.0";
const char open_cfw_test_psn_value[] = "12345678901234";

char open_cfw_test_output_log[4096];
unsigned int open_cfw_test_output_count;
unsigned int open_cfw_test_reset_count;
unsigned int open_cfw_test_snprintf_count;
unsigned int open_cfw_test_psn_read_count;
int open_cfw_test_psn_read_slots[8];
unsigned int open_cfw_test_psn_write_count;
int open_cfw_test_psn_write_slot;
char open_cfw_test_psn_write_value[32];
unsigned int open_cfw_test_imu_rawdata_count;
int open_cfw_test_imu_rawdata_values[8];
unsigned int open_cfw_test_screen_height_count;
int open_cfw_test_screen_height_values[8];
unsigned int open_cfw_test_als_enable_count;
int open_cfw_test_als_enable_values[8];
unsigned int open_cfw_test_als_disable_count;
int open_cfw_test_als_disable_values[8];
unsigned int open_cfw_test_brightness_write_count;
int open_cfw_test_brightness_write_values[8];

void open_cfw_test_reset(void)
{
    open_cfw_test_output_log[0] = '\0';
    open_cfw_test_output_count = 0u;
    open_cfw_test_reset_count = 0u;
    open_cfw_test_snprintf_count = 0u;
    open_cfw_test_psn_read_count = 0u;
    open_cfw_test_psn_write_count = 0u;
    open_cfw_test_psn_write_slot = -1;
    open_cfw_test_psn_write_value[0] = '\0';
    open_cfw_test_imu_rawdata_count = 0u;
    open_cfw_test_screen_height_count = 0u;
    open_cfw_test_als_enable_count = 0u;
    open_cfw_test_als_disable_count = 0u;
    open_cfw_test_brightness_write_count = 0u;
}

void open_cfw_test_at_output(const char *format, ...)
{
    size_t used = strlen(open_cfw_test_output_log);
    va_list arguments;

    va_start(arguments, format);
    vsnprintf(
        open_cfw_test_output_log + used,
        sizeof(open_cfw_test_output_log) - used,
        format,
        arguments
    );
    va_end(arguments);
    ++open_cfw_test_output_count;
}

uint32_t open_cfw_test_at_parameter_length(const char *parameter)
{
    return (uint32_t)strlen(parameter);
}

int open_cfw_test_at_parse_integer(const char *parameter)
{
    return atoi(parameter);
}

int open_cfw_test_snprintf(
    char *buffer, uint32_t capacity, const char *format, ...
)
{
    va_list arguments;
    int result;

    va_start(arguments, format);
    result = vsnprintf(buffer, capacity, format, arguments);
    va_end(arguments);
    ++open_cfw_test_snprintf_count;
    return result;
}

const char *open_cfw_test_hardware_version_get(void)
{
    return open_cfw_test_hardware_version;
}

const char *open_cfw_test_codec_version_get(void)
{
    return open_cfw_test_codec_version;
}

const char *open_cfw_test_touch_version_get(void)
{
    return open_cfw_test_touch_version;
}

const char *open_cfw_test_psn_read(int slot)
{
    if (open_cfw_test_psn_read_count < 8u) {
        open_cfw_test_psn_read_slots[open_cfw_test_psn_read_count] = slot;
    }
    ++open_cfw_test_psn_read_count;
    return open_cfw_test_psn_value;
}

const uint8_t *open_cfw_test_ble_address_get(void)
{
    return open_cfw_test_ble_address;
}

const char *open_cfw_test_ble_name_get(void)
{
    return open_cfw_test_ble_name;
}

void open_cfw_test_system_reset(void)
{
    ++open_cfw_test_reset_count;
}

void open_cfw_test_psn_write(int slot, const char *value)
{
    open_cfw_test_psn_write_slot = slot;
    snprintf(
        open_cfw_test_psn_write_value,
        sizeof(open_cfw_test_psn_write_value),
        "%s",
        value
    );
    ++open_cfw_test_psn_write_count;
}

void open_cfw_test_imu_rawdata(int enable)
{
    if (open_cfw_test_imu_rawdata_count < 8u) {
        open_cfw_test_imu_rawdata_values[open_cfw_test_imu_rawdata_count] =
            enable;
    }
    ++open_cfw_test_imu_rawdata_count;
}

const float *open_cfw_test_imu_euler(void)
{
    return open_cfw_test_euler_angles;
}

void open_cfw_test_screen_height(int height)
{
    if (open_cfw_test_screen_height_count < 8u) {
        open_cfw_test_screen_height_values[open_cfw_test_screen_height_count] =
            height;
    }
    ++open_cfw_test_screen_height_count;
}

uint32_t open_cfw_test_als_read(void)
{
    return open_cfw_test_als_value;
}

void open_cfw_test_als_enable(int state)
{
    if (open_cfw_test_als_enable_count < 8u) {
        open_cfw_test_als_enable_values[open_cfw_test_als_enable_count] = state;
    }
    ++open_cfw_test_als_enable_count;
}

void open_cfw_test_als_disable(int state)
{
    if (open_cfw_test_als_disable_count < 8u) {
        open_cfw_test_als_disable_values[open_cfw_test_als_disable_count] =
            state;
    }
    ++open_cfw_test_als_disable_count;
}

void open_cfw_test_brightness_write(int brightness)
{
    if (open_cfw_test_brightness_write_count < 8u) {
        open_cfw_test_brightness_write_values[
            open_cfw_test_brightness_write_count
        ] = brightness;
    }
    ++open_cfw_test_brightness_write_count;
}

uint32_t open_cfw_test_als_scale_read(void)
{
    return open_cfw_test_als_scale;
}

uint32_t open_cfw_test_brightness_read(void)
{
    return open_cfw_test_brightness;
}
