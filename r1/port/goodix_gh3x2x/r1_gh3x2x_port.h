#ifndef R1_GH3X2X_PORT_H
#define R1_GH3X2X_PORT_H

/*
 * openR1 port layer for the Goodix GH3X2X democode (pinned upstream copy,
 * consumed via GOODIX_DEMOCODE_ROOT; see r1/docs/correlation/
 * GOODIX-DEMOCODE-INTEGRATION-CORRELATION.md).
 *
 * This file is R1-authored and freestanding-safe: it includes no vendor
 * headers and no C library headers beyond the compiler-provided stdint/
 * stdbool, so it builds on the Cortex-M4F freestanding clang target
 * (arm-objects) without the vendor tree present.
 *
 * The democode kernel template (demo_kernel_code/kernel/gh_demo_user.c)
 * expects the integrator to supply a fixed set of platform entry points
 * (gh3026_* board hooks, delay_us, gh3x2x_print_fmt, gh3x2x_rawdata_notify,
 * gh3x2x_wear_evt_notify).  The goodix_mem allocator contract declares
 * Gh3x2xPoolIsNotEnough() as integrator-supplied.  All of these are
 * implemented in r1_gh3x2x_port.c and forward onto the ops below.
 *
 * Every trampoline fails closed when no HAL is bound or a callback is
 * absent: I2C reads return a zeroed buffer (the driver magic-value and
 * communication-confirm checks then fail on their own), notifications are
 * dropped, and no sensor data is ever synthesized.
 */

#include <stdbool.h>
#include <stdint.h>

#include "openr1/r1_goodix.h"

/* Layout-compatible with the democode STGsensorRawdata when the gyro
 * channel is disabled (__GS_GYRO_ENABLE__ == 0 in the R1 configuration):
 * three 16-bit axis values, naturally packed. */
typedef struct {
    int16_t x;
    int16_t y;
    int16_t z;
} r1_gh3x2x_gsensor_sample;

typedef struct {
    void *context;
    /* I2C bus hooks.  device_id is the 8-bit democode device id
     * (GH3X2X_I2C_DEVICE_ID_BASE 0x28 | (id_sel << 1)); a 7-bit platform
     * bus layer must shift right by one, per the democode contract. */
    void (*i2c_init)(void *context);
    void (*i2c_write)(void *context, uint8_t device_id, const uint8_t *data,
                      uint16_t length);
    void (*i2c_read)(void *context, uint8_t device_id, const uint8_t *command,
                     uint16_t command_length, uint8_t *data,
                     uint16_t data_length);
    /* Board pin hooks. */
    void (*int_pin_init)(void *context);
    void (*reset_pin_init)(void *context);
    void (*reset_pin_ctrl)(void *context, uint8_t level);
    /* Accelerometer feed for the driver FIFO alignment path.  *count is
     * zeroed by the port before the call; the hook stores the number of
     * samples written into samples[]. */
    void (*gsensor_get)(void *context, r1_gh3x2x_gsensor_sample *samples,
                        uint16_t *count);
    /* Microsecond busy/sleep delay used by the driver timing paths. */
    void (*delay_us)(void *context, uint32_t microseconds);
    /* Log sink.  The democode passes a printf format string with optional
     * varargs; the port forwards the format text only and never formats
     * varargs (no C library on the freestanding target). */
    void (*log)(void *context, const char *text);
    /* Raw-frame notification: one frame of 32-bit raw channel words. */
    void (*rawdata_notify)(void *context, const uint32_t *rawdata,
                           uint32_t count);
    /* Soft-ADT wear state notification. */
    void (*wear_notify)(void *context, bool worn);
} r1_gh3x2x_hal;

/* Copy-bind the HAL table.  Passing NULL (or r1_gh3x2x_port_unbind_hal)
 * returns the port to the unbound, fail-closed state. */
void r1_gh3x2x_port_bind_hal(const r1_gh3x2x_hal *hal);
void r1_gh3x2x_port_unbind_hal(void);
bool r1_gh3x2x_port_hal_bound(void);

/* Bind the fatal pool handler used by Gh3x2xPoolIsNotEnough(); the ops
 * pointer must remain valid while bound. */
void r1_gh3x2x_pool_bind(const r1_goodix_pool_fatal_ops *ops);

/* Democode-facing trampolines.  The symbol names and ABIs are fixed by the
 * vendor tree; they are declared here with R1-visible types only. */
void gh3026_i2c_init(void);
void gh3026_i2c_write(uint8_t device_id, const uint8_t data[],
                      uint16_t length);
void gh3026_i2c_read(uint8_t device_id, const uint8_t command[],
                     uint16_t command_length, uint8_t data[],
                     uint16_t data_length);
void gh3026_int_pin_init(void);
void gh3026_reset_pin_init(void);
void gh3026_reset_pin_ctrl(uint8_t level);
void gh3026_gsensor_data_get(r1_gh3x2x_gsensor_sample samples[],
                             uint16_t *count);
void delay_us(uint32_t microseconds);
void gh3x2x_print_fmt(const char *format, ...);
void gh3x2x_rawdata_notify(uint32_t *rawdata, uint32_t count);
void gh3x2x_wear_evt_notify(bool worn);
void Gh3x2xPoolIsNotEnough(void);

#endif
