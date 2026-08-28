/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room behavioral reconstruction of the pathless G2 2.2.6.10 eAT
 * core/sensor command cluster: the twelve registered handlers AT^INFO,
 * AT^RESET, AT^PSN, AT^IMU_RAWDATA, AT^IMU_EULER, AT^SCRN_X, AT^SCRN_Y,
 * AT^ALS_READ, AT^ALS, AT^BRIGHTNESS, AT^ALS_SCALE_READ, and
 * AT^BRIGHTNESS_READ. The behavioral specifications, retained provider
 * bindings, retained literal addresses, and stock quirks (including
 * SCRN_Y accepting zero despite its 1-192 diagnostic, and the PSN error
 * reporting the required length rather than the observed one) are recorded
 * in docs/research/g2-eat-core-sensor-recovery.md and
 * components/apollo_main/core_overlay/EVIDENCE.md. This file is an openCFW
 * bounded reimplementation; no stock object bytes are reproduced here.
 */

#include <stdint.h>

#define OPEN_CFW_AT_RETAINED_STRING(address) \
    ((const char *)(uintptr_t)(address))

/* Retained format, response, and identity literals (stock addresses). */
#ifndef OPEN_CFW_AT_PRODUCT_NAME
#define OPEN_CFW_AT_PRODUCT_NAME OPEN_CFW_AT_RETAINED_STRING(0x0078cc0cu)
#endif
#ifndef OPEN_CFW_AT_INFO_PRODUCT_FORMAT
#define OPEN_CFW_AT_INFO_PRODUCT_FORMAT OPEN_CFW_AT_RETAINED_STRING(0x00769b4cu)
#endif
#ifndef OPEN_CFW_AT_INFO_HARDWARE_FORMAT
#define OPEN_CFW_AT_INFO_HARDWARE_FORMAT \
    OPEN_CFW_AT_RETAINED_STRING(0x00769b68u)
#endif
#ifndef OPEN_CFW_AT_SOFTWARE_VERSION
#define OPEN_CFW_AT_SOFTWARE_VERSION OPEN_CFW_AT_RETAINED_STRING(0x0078a3a0u)
#endif
#ifndef OPEN_CFW_AT_INFO_SOFTWARE_FORMAT
#define OPEN_CFW_AT_INFO_SOFTWARE_FORMAT \
    OPEN_CFW_AT_RETAINED_STRING(0x00769b84u)
#endif
#ifndef OPEN_CFW_AT_INFO_CODEC_FORMAT
#define OPEN_CFW_AT_INFO_CODEC_FORMAT OPEN_CFW_AT_RETAINED_STRING(0x00769ba0u)
#endif
#ifndef OPEN_CFW_AT_INFO_TOUCH_FORMAT
#define OPEN_CFW_AT_INFO_TOUCH_FORMAT OPEN_CFW_AT_RETAINED_STRING(0x00769bbcu)
#endif
#ifndef OPEN_CFW_AT_COMPILE_DATE
#define OPEN_CFW_AT_COMPILE_DATE OPEN_CFW_AT_RETAINED_STRING(0x0078a3acu)
#endif
#ifndef OPEN_CFW_AT_COMPILE_TIME
#define OPEN_CFW_AT_COMPILE_TIME OPEN_CFW_AT_RETAINED_STRING(0x0078a3b8u)
#endif
#ifndef OPEN_CFW_AT_INFO_COMPILE_FORMAT
#define OPEN_CFW_AT_INFO_COMPILE_FORMAT \
    OPEN_CFW_AT_RETAINED_STRING(0x00769bd8u)
#endif
#ifndef OPEN_CFW_AT_INFO_SN_FORMAT
#define OPEN_CFW_AT_INFO_SN_FORMAT OPEN_CFW_AT_RETAINED_STRING(0x00769bf4u)
#endif
#ifndef OPEN_CFW_AT_INFO_BLE_NAME_FORMAT
#define OPEN_CFW_AT_INFO_BLE_NAME_FORMAT \
    OPEN_CFW_AT_RETAINED_STRING(0x00769c10u)
#endif
#ifndef OPEN_CFW_AT_INFO_BLE_ADDR_FORMAT
#define OPEN_CFW_AT_INFO_BLE_ADDR_FORMAT \
    OPEN_CFW_AT_RETAINED_STRING(0x00727200u)
#endif
#ifndef OPEN_CFW_AT_INFO_RESPONSE
#define OPEN_CFW_AT_INFO_RESPONSE OPEN_CFW_AT_RETAINED_STRING(0x0078a3c4u)
#endif
#ifndef OPEN_CFW_AT_RESET_RESPONSE
#define OPEN_CFW_AT_RESET_RESPONSE OPEN_CFW_AT_RETAINED_STRING(0x0078a3d0u)
#endif
#ifndef OPEN_CFW_AT_PSN_ECHO_FORMAT
#define OPEN_CFW_AT_PSN_ECHO_FORMAT OPEN_CFW_AT_RETAINED_STRING(0x005a5824u)
#endif
#ifndef OPEN_CFW_AT_PSN_ERROR_FORMAT
#define OPEN_CFW_AT_PSN_ERROR_FORMAT OPEN_CFW_AT_RETAINED_STRING(0x006df828u)
#endif
#ifndef OPEN_CFW_AT_PSN_RESPONSE
#define OPEN_CFW_AT_PSN_RESPONSE OPEN_CFW_AT_RETAINED_STRING(0x0078a3e8u)
#endif
#ifndef OPEN_CFW_AT_IMU_RAWDATA_FORMAT
#define OPEN_CFW_AT_IMU_RAWDATA_FORMAT \
    OPEN_CFW_AT_RETAINED_STRING(0x00769c2cu)
#endif
#ifndef OPEN_CFW_AT_IMU_RAWDATA_ERROR
#define OPEN_CFW_AT_IMU_RAWDATA_ERROR \
    OPEN_CFW_AT_RETAINED_STRING(0x006f887cu)
#endif
#ifndef OPEN_CFW_AT_IMU_EULER_FORMAT
#define OPEN_CFW_AT_IMU_EULER_FORMAT OPEN_CFW_AT_RETAINED_STRING(0x00731b44u)
#endif
#ifndef OPEN_CFW_AT_SCRN_X_RESPONSE
#define OPEN_CFW_AT_SCRN_X_RESPONSE OPEN_CFW_AT_RETAINED_STRING(0x00785190u)
#endif
#ifndef OPEN_CFW_AT_SCRN_Y_ERROR
#define OPEN_CFW_AT_SCRN_Y_ERROR OPEN_CFW_AT_RETAINED_STRING(0x00731b74u)
#endif
#ifndef OPEN_CFW_AT_SCRN_Y_RESPONSE
#define OPEN_CFW_AT_SCRN_Y_RESPONSE OPEN_CFW_AT_RETAINED_STRING(0x007851a0u)
#endif
#ifndef OPEN_CFW_AT_ALS_READ_FORMAT
#define OPEN_CFW_AT_ALS_READ_FORMAT OPEN_CFW_AT_RETAINED_STRING(0x00747c74u)
#endif
#ifndef OPEN_CFW_AT_ALS_FORMAT
#define OPEN_CFW_AT_ALS_FORMAT OPEN_CFW_AT_RETAINED_STRING(0x00775614u)
#endif
#ifndef OPEN_CFW_AT_BRIGHTNESS_FORMAT
#define OPEN_CFW_AT_BRIGHTNESS_FORMAT OPEN_CFW_AT_RETAINED_STRING(0x007523b8u)
#endif
#ifndef OPEN_CFW_AT_ALS_SCALE_READ_FORMAT
#define OPEN_CFW_AT_ALS_SCALE_READ_FORMAT \
    OPEN_CFW_AT_RETAINED_STRING(0x007523dcu)
#endif
#ifndef OPEN_CFW_AT_BRIGHTNESS_READ_FORMAT
#define OPEN_CFW_AT_BRIGHTNESS_READ_FORMAT \
    OPEN_CFW_AT_RETAINED_STRING(0x00747c9cu)
#endif

/* Signed LUX_BASE shadow word in stock SRAM. */
#ifndef OPEN_CFW_AT_LUX_BASE_ADDRESS
#define OPEN_CFW_AT_LUX_BASE_ADDRESS 0x200039bcu
#endif
#ifndef OPEN_CFW_AT_LUX_BASE
#define OPEN_CFW_AT_LUX_BASE \
    (*(volatile int32_t *)(uintptr_t)OPEN_CFW_AT_LUX_BASE_ADDRESS)
#endif

/* Retained providers (stock binding addresses are pinned in overlay.json). */
#ifndef OPEN_CFW_AT_OUTPUT
void open_cfw_retained_at_output(const char *format, ...);
#define OPEN_CFW_AT_OUTPUT(...) open_cfw_retained_at_output(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_AT_PARAMETER_LENGTH
uint32_t open_cfw_retained_at_parameter_length(const char *parameter);
#define OPEN_CFW_AT_PARAMETER_LENGTH(parameter) \
    open_cfw_retained_at_parameter_length((parameter))
#endif
#ifndef OPEN_CFW_AT_PARSE_INTEGER
int open_cfw_retained_at_parse_integer(const char *parameter);
#define OPEN_CFW_AT_PARSE_INTEGER(parameter) \
    open_cfw_retained_at_parse_integer((parameter))
#endif
#ifndef OPEN_CFW_AT_SNPRINTF
int open_cfw_retained_snprintf(
    char *buffer, uint32_t capacity, const char *format, ...
);
#define OPEN_CFW_AT_SNPRINTF(...) open_cfw_retained_snprintf(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_AT_HARDWARE_VERSION
const char *open_cfw_retained_hardware_version(void);
#define OPEN_CFW_AT_HARDWARE_VERSION() open_cfw_retained_hardware_version()
#endif
#ifndef OPEN_CFW_AT_CODEC_VERSION
const char *open_cfw_retained_codec_version(void);
#define OPEN_CFW_AT_CODEC_VERSION() open_cfw_retained_codec_version()
#endif
#ifndef OPEN_CFW_AT_TOUCH_VERSION
const char *open_cfw_retained_touch_version(void);
#define OPEN_CFW_AT_TOUCH_VERSION() open_cfw_retained_touch_version()
#endif
#ifndef OPEN_CFW_AT_PSN_READ
const char *open_cfw_retained_psn_read(int slot);
#define OPEN_CFW_AT_PSN_READ(slot) open_cfw_retained_psn_read((slot))
#endif
#ifndef OPEN_CFW_AT_BLE_ADDRESS
const uint8_t *open_cfw_retained_ble_address(void);
#define OPEN_CFW_AT_BLE_ADDRESS() open_cfw_retained_ble_address()
#endif
#ifndef OPEN_CFW_AT_BLE_NAME
const char *open_cfw_retained_ble_name(void);
#define OPEN_CFW_AT_BLE_NAME() open_cfw_retained_ble_name()
#endif
#ifndef OPEN_CFW_AT_SYSTEM_RESET
void open_cfw_retained_system_reset(void);
#define OPEN_CFW_AT_SYSTEM_RESET() open_cfw_retained_system_reset()
#endif
#ifndef OPEN_CFW_AT_PSN_WRITE
void open_cfw_retained_psn_write(int slot, const char *value);
#define OPEN_CFW_AT_PSN_WRITE(slot, value) \
    open_cfw_retained_psn_write((slot), (value))
#endif
#ifndef OPEN_CFW_AT_IMU_RAWDATA
void open_cfw_retained_imu_rawdata(int enable);
#define OPEN_CFW_AT_IMU_RAWDATA(enable) \
    open_cfw_retained_imu_rawdata((enable))
#endif
#ifndef OPEN_CFW_AT_IMU_EULER
const float *open_cfw_retained_imu_euler(void);
#define OPEN_CFW_AT_IMU_EULER() open_cfw_retained_imu_euler()
#endif
#ifndef OPEN_CFW_AT_SCREEN_HEIGHT
void open_cfw_retained_screen_height(int height);
#define OPEN_CFW_AT_SCREEN_HEIGHT(height) \
    open_cfw_retained_screen_height((height))
#endif
#ifndef OPEN_CFW_AT_ALS_READ
uint32_t open_cfw_retained_als_read(void);
#define OPEN_CFW_AT_ALS_READ() open_cfw_retained_als_read()
#endif
#ifndef OPEN_CFW_AT_ALS_ENABLE
void open_cfw_retained_als_enable(int state);
#define OPEN_CFW_AT_ALS_ENABLE(state) open_cfw_retained_als_enable((state))
#endif
#ifndef OPEN_CFW_AT_ALS_DISABLE
void open_cfw_retained_als_disable(int state);
#define OPEN_CFW_AT_ALS_DISABLE(state) open_cfw_retained_als_disable((state))
#endif
#ifndef OPEN_CFW_AT_BRIGHTNESS_WRITE
void open_cfw_retained_brightness_write(int brightness);
#define OPEN_CFW_AT_BRIGHTNESS_WRITE(brightness) \
    open_cfw_retained_brightness_write((brightness))
#endif
#ifndef OPEN_CFW_AT_ALS_SCALE_READ
uint32_t open_cfw_retained_als_scale_read(void);
#define OPEN_CFW_AT_ALS_SCALE_READ() open_cfw_retained_als_scale_read()
#endif
#ifndef OPEN_CFW_AT_BRIGHTNESS_READ
uint32_t open_cfw_retained_brightness_read(void);
#define OPEN_CFW_AT_BRIGHTNESS_READ() open_cfw_retained_brightness_read()
#endif

enum {
    OPEN_CFW_AT_PSN_REQUIRED_LENGTH = 14,
    OPEN_CFW_AT_SCRN_Y_REJECT_LEVEL = 193,
    OPEN_CFW_AT_ALS_READ_CAPACITY = 100
};

#if defined(__arm__) || defined(__thumb__)
/*
 * The overlay's soft-float Clang target would lower the stock single- to
 * double-precision promotion to an unresolved __aeabi helper; express the
 * stock VFP operation explicitly, matching the runtime_ftoa.c idiom.
 */
static __attribute__((always_inline)) inline double
open_cfw_at_euler_promote(float value)
{
    union {
        float floating;
        uint32_t bits;
    } representation;
    double result;

    representation.floating = value;
    __asm__ volatile (
        ".fpu fpv5-d16\n\t"
        "vmov s0, %1\n\t"
        "vcvt.f64.f32 %P0, s0"
        : "=w"(result)
        : "r"(representation.bits)
    );
    return result;
}
#else
static __attribute__((always_inline)) inline double
open_cfw_at_euler_promote(float value)
{
    return (double)value;
}
#endif

int open_cfw_at_info_handler(void)
{
    const uint8_t *address;
    const char *name;

    OPEN_CFW_AT_OUTPUT(
        OPEN_CFW_AT_INFO_PRODUCT_FORMAT, OPEN_CFW_AT_PRODUCT_NAME
    );
    OPEN_CFW_AT_OUTPUT(
        OPEN_CFW_AT_INFO_HARDWARE_FORMAT, OPEN_CFW_AT_HARDWARE_VERSION()
    );
    OPEN_CFW_AT_OUTPUT(
        OPEN_CFW_AT_INFO_SOFTWARE_FORMAT, OPEN_CFW_AT_SOFTWARE_VERSION
    );
    OPEN_CFW_AT_OUTPUT(
        OPEN_CFW_AT_INFO_CODEC_FORMAT, OPEN_CFW_AT_CODEC_VERSION()
    );
    OPEN_CFW_AT_OUTPUT(
        OPEN_CFW_AT_INFO_TOUCH_FORMAT, OPEN_CFW_AT_TOUCH_VERSION()
    );
    OPEN_CFW_AT_OUTPUT(
        OPEN_CFW_AT_INFO_COMPILE_FORMAT,
        OPEN_CFW_AT_COMPILE_DATE,
        OPEN_CFW_AT_COMPILE_TIME
    );
    OPEN_CFW_AT_OUTPUT(
        OPEN_CFW_AT_INFO_SN_FORMAT, OPEN_CFW_AT_PSN_READ(0)
    );
    address = OPEN_CFW_AT_BLE_ADDRESS();
    name = OPEN_CFW_AT_BLE_NAME();
    OPEN_CFW_AT_OUTPUT(OPEN_CFW_AT_INFO_BLE_NAME_FORMAT, name);
    OPEN_CFW_AT_OUTPUT(
        OPEN_CFW_AT_INFO_BLE_ADDR_FORMAT,
        address[5],
        address[4],
        address[3],
        address[2],
        address[1],
        address[0]
    );
    OPEN_CFW_AT_OUTPUT(OPEN_CFW_AT_INFO_RESPONSE);
    return 1;
}

int open_cfw_at_reset_handler(void)
{
    OPEN_CFW_AT_OUTPUT(OPEN_CFW_AT_RESET_RESPONSE);
    OPEN_CFW_AT_SYSTEM_RESET();
    return 1;
}

int open_cfw_at_psn_handler(const char *parameter)
{
    if (
        OPEN_CFW_AT_PARAMETER_LENGTH(parameter)
        == OPEN_CFW_AT_PSN_REQUIRED_LENGTH
    ) {
        OPEN_CFW_AT_OUTPUT(OPEN_CFW_AT_PSN_ECHO_FORMAT, parameter);
        OPEN_CFW_AT_PSN_WRITE(0, parameter);
    } else {
        OPEN_CFW_AT_OUTPUT(
            OPEN_CFW_AT_PSN_ERROR_FORMAT, OPEN_CFW_AT_PSN_REQUIRED_LENGTH
        );
    }
    OPEN_CFW_AT_OUTPUT(OPEN_CFW_AT_PSN_RESPONSE);
    return 1;
}

int open_cfw_at_imu_rawdata_handler(const char *parameter)
{
    int value = OPEN_CFW_AT_PARSE_INTEGER(parameter);

    if (value == 1) {
        OPEN_CFW_AT_IMU_RAWDATA(1);
        OPEN_CFW_AT_OUTPUT(OPEN_CFW_AT_IMU_RAWDATA_FORMAT, value);
        return 1;
    }
    if (value == 0) {
        OPEN_CFW_AT_IMU_RAWDATA(0);
        OPEN_CFW_AT_OUTPUT(OPEN_CFW_AT_IMU_RAWDATA_FORMAT, value);
        return 1;
    }
    OPEN_CFW_AT_OUTPUT(OPEN_CFW_AT_IMU_RAWDATA_ERROR);
    return 0;
}

int open_cfw_at_imu_euler_handler(void)
{
    const float *angles = OPEN_CFW_AT_IMU_EULER();

    OPEN_CFW_AT_OUTPUT(
        OPEN_CFW_AT_IMU_EULER_FORMAT,
        open_cfw_at_euler_promote(angles[0]),
        open_cfw_at_euler_promote(angles[1]),
        open_cfw_at_euler_promote(angles[2])
    );
    return 1;
}

int open_cfw_at_screen_x_handler(void)
{
    OPEN_CFW_AT_OUTPUT(OPEN_CFW_AT_SCRN_X_RESPONSE);
    return 1;
}

int open_cfw_at_screen_y_handler(const char *parameter)
{
    int value = OPEN_CFW_AT_PARSE_INTEGER(parameter);

    if ((uint32_t)value >= OPEN_CFW_AT_SCRN_Y_REJECT_LEVEL) {
        OPEN_CFW_AT_OUTPUT(OPEN_CFW_AT_SCRN_Y_ERROR);
    } else {
        OPEN_CFW_AT_SCREEN_HEIGHT(value);
        OPEN_CFW_AT_OUTPUT(OPEN_CFW_AT_SCRN_Y_RESPONSE);
    }
    return 1;
}

int open_cfw_at_als_read_handler(void)
{
    char buffer[OPEN_CFW_AT_ALS_READ_CAPACITY];
    uint32_t als = OPEN_CFW_AT_ALS_READ();
    int32_t lux_base = OPEN_CFW_AT_LUX_BASE;

    OPEN_CFW_AT_SNPRINTF(
        buffer,
        (uint32_t)sizeof(buffer),
        OPEN_CFW_AT_ALS_READ_FORMAT,
        als,
        lux_base
    );
    OPEN_CFW_AT_OUTPUT(buffer);
    return 1;
}

int open_cfw_at_als_handler(const char *parameter)
{
    int value = OPEN_CFW_AT_PARSE_INTEGER(parameter);

    if (value == 1) {
        OPEN_CFW_AT_ALS_ENABLE(value);
    } else if (value == 0) {
        OPEN_CFW_AT_ALS_DISABLE(value);
    }
    OPEN_CFW_AT_OUTPUT(OPEN_CFW_AT_ALS_FORMAT, value);
    return 1;
}

int open_cfw_at_brightness_handler(const char *parameter)
{
    int value = OPEN_CFW_AT_PARSE_INTEGER(parameter);

    OPEN_CFW_AT_BRIGHTNESS_WRITE(value);
    OPEN_CFW_AT_OUTPUT(OPEN_CFW_AT_BRIGHTNESS_FORMAT, value);
    return 1;
}

int open_cfw_at_als_scale_read_handler(void)
{
    OPEN_CFW_AT_OUTPUT(
        OPEN_CFW_AT_ALS_SCALE_READ_FORMAT, OPEN_CFW_AT_ALS_SCALE_READ()
    );
    return 1;
}

int open_cfw_at_brightness_read_handler(void)
{
    OPEN_CFW_AT_OUTPUT(
        OPEN_CFW_AT_BRIGHTNESS_READ_FORMAT, OPEN_CFW_AT_BRIGHTNESS_READ()
    );
    return 1;
}
