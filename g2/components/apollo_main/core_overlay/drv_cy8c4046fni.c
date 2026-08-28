/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room behavioral reconstruction of the retained G2 2.2.6.10
 * driver/touch/drv_cy8c4046fni.c host-side Cypress touch driver.
 */

#include <stdint.h>

typedef uintptr_t open_cfw_cy8c_uintptr;
typedef int32_t (*open_cfw_cy8c_register_write_fn)(
    uint8_t command, const void *data, uint16_t size
);
typedef int32_t (*open_cfw_cy8c_register_read_fn)(
    uint8_t command, void *data, uint16_t size
);
typedef int32_t (*open_cfw_cy8c_raw_write_fn)(const void *data, uint16_t size);
typedef int32_t (*open_cfw_cy8c_raw_read_fn)(void *data, uint16_t size);

typedef struct {
    open_cfw_cy8c_register_write_fn register_write;
    open_cfw_cy8c_register_read_fn register_read;
    open_cfw_cy8c_raw_write_fn raw_write;
    open_cfw_cy8c_raw_read_fn raw_read;
} open_cfw_cy8c_ops;

#ifndef OPEN_CFW_CY8C_OPS
#define OPEN_CFW_CY8C_OPS \
    ((open_cfw_cy8c_ops *)(open_cfw_cy8c_uintptr)0x20073e24u)
#endif
#ifndef OPEN_CFW_CY8C_BASELINE_SCRATCH
#define OPEN_CFW_CY8C_BASELINE_SCRATCH \
    ((volatile uint8_t *)(open_cfw_cy8c_uintptr)0x20074508u)
#endif
#ifndef OPEN_CFW_CY8C_STOCK_OPS_TABLE
#define OPEN_CFW_CY8C_STOCK_OPS_TABLE \
    ((const uint32_t *)(open_cfw_cy8c_uintptr)0x0055b9f0u)
#endif

#ifndef OPEN_CFW_CY8C_HAL_REGISTER_WRITE
int32_t open_cfw_retained_cy8c_hal_register_write(
    uint32_t bus, uint32_t address, const void *command,
    uint32_t command_size, const void *data, uint16_t data_size
);
#define OPEN_CFW_CY8C_HAL_REGISTER_WRITE(...) \
    open_cfw_retained_cy8c_hal_register_write(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_CY8C_HAL_REGISTER_READ
int32_t open_cfw_retained_cy8c_hal_register_read(
    uint32_t bus, uint32_t address, const void *command,
    uint32_t command_size, void *data, uint16_t data_size
);
#define OPEN_CFW_CY8C_HAL_REGISTER_READ(...) \
    open_cfw_retained_cy8c_hal_register_read(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_CY8C_HAL_RAW_WRITE
int32_t open_cfw_retained_cy8c_hal_raw_write(
    uint32_t bus, uint32_t address, const void *data, uint16_t size
);
#define OPEN_CFW_CY8C_HAL_RAW_WRITE(...) \
    open_cfw_retained_cy8c_hal_raw_write(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_CY8C_HAL_RAW_READ
int32_t open_cfw_retained_cy8c_hal_raw_read(
    uint32_t bus, uint32_t address, void *data, uint16_t size
);
#define OPEN_CFW_CY8C_HAL_RAW_READ(...) \
    open_cfw_retained_cy8c_hal_raw_read(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_CY8C_BOARD_CONTROL
void open_cfw_retained_cy8c_board_control(uint32_t selector, uint32_t enabled);
#define OPEN_CFW_CY8C_BOARD_CONTROL(selector, enabled) \
    open_cfw_retained_cy8c_board_control((selector), (enabled))
#endif
#ifndef OPEN_CFW_CY8C_DELAY
void open_cfw_retained_cy8c_delay(uint32_t milliseconds);
#define OPEN_CFW_CY8C_DELAY(milliseconds) \
    open_cfw_retained_cy8c_delay(milliseconds)
#endif

int32_t open_cfw_cy8c_i2c_register_write(
    uint8_t command, const void *data, uint16_t size
);
int32_t open_cfw_cy8c_i2c_register_read(
    uint8_t command, void *data, uint16_t size
);
int32_t open_cfw_cy8c_i2c_raw_write(const void *data, uint16_t size);
int32_t open_cfw_cy8c_i2c_raw_read(void *data, uint16_t size);
int32_t open_cfw_cy8c_command(open_cfw_cy8c_ops *ops);
int32_t open_cfw_cy8c_read_command(
    open_cfw_cy8c_ops *ops, void *data, uint16_t size
);
int32_t open_cfw_cy8c_write_command(
    open_cfw_cy8c_ops *ops, const void *data, uint16_t size
);
int32_t open_cfw_cy8c_save_command(open_cfw_cy8c_ops *ops);
int32_t open_cfw_cy8c_read_baseline_command(
    open_cfw_cy8c_ops *ops, uint16_t *value
);
uint32_t open_cfw_cy8c_gesture_threshold_valid(const uint16_t *threshold);
int32_t open_cfw_cy8c_write_gesture_private(
    open_cfw_cy8c_ops *ops, const uint16_t *threshold
);
int32_t open_cfw_cy8c_read_gesture_private(
    open_cfw_cy8c_ops *ops, uint16_t *threshold
);
void open_cfw_cy8c_install_default_ops(open_cfw_cy8c_ops *ops);
int32_t open_cfw_cy8c_switch_to_dfu(void);
void open_cfw_cy8c_reset(void);
void open_cfw_cy8c_initialize(void);
void open_cfw_cy8c_read_touch_frame(uint8_t *data);
int32_t open_cfw_cy8c_read_difference(uint8_t *data);
int32_t open_cfw_cy8c_prepare_proximity_baseline(uint32_t *value);
int32_t open_cfw_cy8c_save_proximity_baseline(void);
uint16_t open_cfw_cy8c_read_proximity_baseline(void);
int32_t open_cfw_cy8c_write_gesture_cfg(uint16_t *threshold);
int32_t open_cfw_cy8c_read_gesture_cfg(uint16_t *threshold);

static __attribute__((always_inline, unused)) inline void
open_cfw_cy8c_zero(void *target, uint32_t size)
{
    uint8_t *bytes = (uint8_t *)target;
    uint32_t index;
    for (index = 0u; index < size; ++index) {
        bytes[index] = 0u;
    }
}

static __attribute__((always_inline, unused)) inline void
open_cfw_cy8c_copy(void *target, const void *source, uint32_t size)
{
    uint8_t *to = (uint8_t *)target;
    const uint8_t *from = (const uint8_t *)source;
    uint32_t index;
    for (index = 0u; index < size; ++index) {
        to[index] = from[index];
    }
}

#if !defined(OPEN_CFW_CY8C_I2C_REGISTER_WRITE_ONLY) \
    && !defined(OPEN_CFW_CY8C_I2C_REGISTER_READ_ONLY) \
    && !defined(OPEN_CFW_CY8C_I2C_RAW_WRITE_ONLY) \
    && !defined(OPEN_CFW_CY8C_I2C_RAW_READ_ONLY) \
    && !defined(OPEN_CFW_CY8C_COMMAND_ONLY) \
    && !defined(OPEN_CFW_CY8C_READ_COMMAND_ONLY) \
    && !defined(OPEN_CFW_CY8C_WRITE_COMMAND_ONLY) \
    && !defined(OPEN_CFW_CY8C_SAVE_COMMAND_ONLY) \
    && !defined(OPEN_CFW_CY8C_READ_BASELINE_COMMAND_ONLY) \
    && !defined(OPEN_CFW_CY8C_GESTURE_THRESHOLD_VALID_ONLY) \
    && !defined(OPEN_CFW_CY8C_WRITE_GESTURE_PRIVATE_ONLY) \
    && !defined(OPEN_CFW_CY8C_READ_GESTURE_PRIVATE_ONLY) \
    && !defined(OPEN_CFW_CY8C_INSTALL_DEFAULT_OPS_ONLY) \
    && !defined(OPEN_CFW_CY8C_SWITCH_TO_DFU_ONLY) \
    && !defined(OPEN_CFW_CY8C_RESET_ONLY) \
    && !defined(OPEN_CFW_CY8C_INITIALIZE_ONLY) \
    && !defined(OPEN_CFW_CY8C_READ_TOUCH_FRAME_ONLY) \
    && !defined(OPEN_CFW_CY8C_READ_DIFFERENCE_ONLY) \
    && !defined(OPEN_CFW_CY8C_PREPARE_PROXIMITY_BASELINE_ONLY) \
    && !defined(OPEN_CFW_CY8C_SAVE_PROXIMITY_BASELINE_ONLY) \
    && !defined(OPEN_CFW_CY8C_READ_PROXIMITY_BASELINE_ONLY) \
    && !defined(OPEN_CFW_CY8C_WRITE_GESTURE_CFG_ONLY) \
    && !defined(OPEN_CFW_CY8C_READ_GESTURE_CFG_ONLY)
#define OPEN_CFW_CY8C_BUILD_ALL 1
#endif

#if defined(OPEN_CFW_CY8C_BUILD_ALL) || defined(OPEN_CFW_CY8C_I2C_REGISTER_WRITE_ONLY)
int32_t open_cfw_cy8c_i2c_register_write(
    uint8_t command, const void *data, uint16_t size
)
{
    uint32_t command_word = command;
    return OPEN_CFW_CY8C_HAL_REGISTER_WRITE(
        5u, 0x0cu, &command_word, 1u, data, size
    );
}
#endif

#if defined(OPEN_CFW_CY8C_BUILD_ALL) || defined(OPEN_CFW_CY8C_I2C_REGISTER_READ_ONLY)
int32_t open_cfw_cy8c_i2c_register_read(
    uint8_t command, void *data, uint16_t size
)
{
    uint32_t command_word = command;
    return OPEN_CFW_CY8C_HAL_REGISTER_READ(
        5u, 0x0cu, &command_word, 1u, data, size
    );
}
#endif

#if defined(OPEN_CFW_CY8C_BUILD_ALL) || defined(OPEN_CFW_CY8C_I2C_RAW_WRITE_ONLY)
int32_t open_cfw_cy8c_i2c_raw_write(const void *data, uint16_t size)
{
    return OPEN_CFW_CY8C_HAL_RAW_WRITE(5u, 0x0cu, data, size);
}
#endif

#if defined(OPEN_CFW_CY8C_BUILD_ALL) || defined(OPEN_CFW_CY8C_I2C_RAW_READ_ONLY)
int32_t open_cfw_cy8c_i2c_raw_read(void *data, uint16_t size)
{
    return OPEN_CFW_CY8C_HAL_RAW_READ(5u, 0x0cu, data, size);
}
#endif

#if defined(OPEN_CFW_CY8C_BUILD_ALL) || defined(OPEN_CFW_CY8C_COMMAND_ONLY)
int32_t open_cfw_cy8c_command(open_cfw_cy8c_ops *ops)
{
    return ops == (open_cfw_cy8c_ops *)0 ? -1 :
        ops->register_write(2u, (const void *)0, 0u);
}
#endif

#if defined(OPEN_CFW_CY8C_BUILD_ALL) || defined(OPEN_CFW_CY8C_READ_COMMAND_ONLY)
int32_t open_cfw_cy8c_read_command(
    open_cfw_cy8c_ops *ops, void *data, uint16_t size
)
{
    return ops == (open_cfw_cy8c_ops *)0 ? -1 :
        ops->register_read(3u, data, size);
}
#endif

#if defined(OPEN_CFW_CY8C_BUILD_ALL) || defined(OPEN_CFW_CY8C_WRITE_COMMAND_ONLY)
int32_t open_cfw_cy8c_write_command(
    open_cfw_cy8c_ops *ops, const void *data, uint16_t size
)
{
    return ops == (open_cfw_cy8c_ops *)0 ? -1 :
        ops->register_read(1u, (void *)data, size);
}
#endif

#if defined(OPEN_CFW_CY8C_BUILD_ALL) || defined(OPEN_CFW_CY8C_SAVE_COMMAND_ONLY)
int32_t open_cfw_cy8c_save_command(open_cfw_cy8c_ops *ops)
{
    return ops == (open_cfw_cy8c_ops *)0 ? -1 :
        ops->register_write(5u, (const void *)0, 0u);
}
#endif

#if defined(OPEN_CFW_CY8C_BUILD_ALL) || defined(OPEN_CFW_CY8C_READ_BASELINE_COMMAND_ONLY)
int32_t open_cfw_cy8c_read_baseline_command(
    open_cfw_cy8c_ops *ops, uint16_t *value
)
{
    uint8_t data[2];
    int32_t status;
    open_cfw_cy8c_zero(data, 2u);
    if (ops == (open_cfw_cy8c_ops *)0 || value == (uint16_t *)0) {
        return -1;
    }
    status = ops->register_read(6u, data, 2u);
    if (status == 0) {
        *value = (uint16_t)((uint16_t)data[0] | ((uint16_t)data[1] << 8));
    }
    return status;
}
#endif

#if defined(OPEN_CFW_CY8C_BUILD_ALL) || defined(OPEN_CFW_CY8C_GESTURE_THRESHOLD_VALID_ONLY)
uint32_t open_cfw_cy8c_gesture_threshold_valid(const uint16_t *threshold)
{
    return threshold != (const uint16_t *)0 && *threshold != 0u ? 1u : 0u;
}
#endif

#if defined(OPEN_CFW_CY8C_BUILD_ALL) || defined(OPEN_CFW_CY8C_WRITE_GESTURE_PRIVATE_ONLY)
int32_t open_cfw_cy8c_write_gesture_private(
    open_cfw_cy8c_ops *ops, const uint16_t *threshold
)
{
    uint8_t request[2];
    uint8_t acknowledgement[3];
    int32_t status;
    open_cfw_cy8c_zero(request, 2u);
    open_cfw_cy8c_zero(acknowledgement, 3u);
    if (ops == (open_cfw_cy8c_ops *)0 ||
        open_cfw_cy8c_gesture_threshold_valid(threshold) == 0u) {
        return 0xff;
    }
    request[0] = (uint8_t)*threshold;
    request[1] = (uint8_t)(*threshold >> 8);
    status = ops->register_write(7u, request, 2u);
    if (status != 0) {
        return status;
    }
    status = ops->raw_read(acknowledgement, 3u);
    if (status != 0) {
        return status;
    }
    if (acknowledgement[0] != 7u || acknowledgement[2] != 0x17u ||
        acknowledgement[1] != 0u) {
        return 0xff;
    }
    return 0;
}
#endif

#if defined(OPEN_CFW_CY8C_BUILD_ALL) || defined(OPEN_CFW_CY8C_READ_GESTURE_PRIVATE_ONLY)
int32_t open_cfw_cy8c_read_gesture_private(
    open_cfw_cy8c_ops *ops, uint16_t *threshold
)
{
    uint8_t data[2];
    int32_t status;
    open_cfw_cy8c_zero(data, 2u);
    if (ops == (open_cfw_cy8c_ops *)0 || threshold == (uint16_t *)0) {
        return -1;
    }
    status = ops->register_read(8u, data, 2u);
    if (status != 0) {
        return status;
    }
    *threshold = (uint16_t)((uint16_t)data[0] | ((uint16_t)data[1] << 8));
    return open_cfw_cy8c_gesture_threshold_valid(threshold) != 0u ? 0 : 0xff;
}
#endif

#if defined(OPEN_CFW_CY8C_BUILD_ALL) || defined(OPEN_CFW_CY8C_INSTALL_DEFAULT_OPS_ONLY)
void open_cfw_cy8c_install_default_ops(open_cfw_cy8c_ops *ops)
{
#ifdef OPEN_CFW_CY8C_HOST_INSTALL_DEFAULT_OPS
    OPEN_CFW_CY8C_HOST_INSTALL_DEFAULT_OPS(ops);
#else
    uint32_t *target = (uint32_t *)ops;
    const uint32_t *source = OPEN_CFW_CY8C_STOCK_OPS_TABLE;
    uint32_t index;
    if (ops == (open_cfw_cy8c_ops *)0) {
        return;
    }
    for (index = 0u; index < 4u; ++index) {
        target[index] = source[index];
    }
#endif
}
#endif

#if defined(OPEN_CFW_CY8C_BUILD_ALL) || defined(OPEN_CFW_CY8C_SWITCH_TO_DFU_ONLY)
int32_t open_cfw_cy8c_switch_to_dfu(void)
{
    return open_cfw_cy8c_command(OPEN_CFW_CY8C_OPS) == 0 ? 0 : -1;
}
#endif

#if defined(OPEN_CFW_CY8C_BUILD_ALL) || defined(OPEN_CFW_CY8C_RESET_ONLY)
void open_cfw_cy8c_reset(void)
{
    OPEN_CFW_CY8C_BOARD_CONTROL(10u, 0u);
    OPEN_CFW_CY8C_DELAY(10u);
    OPEN_CFW_CY8C_BOARD_CONTROL(10u, 1u);
    OPEN_CFW_CY8C_DELAY(50u);
}
#endif

#if defined(OPEN_CFW_CY8C_BUILD_ALL) || defined(OPEN_CFW_CY8C_INITIALIZE_ONLY)
void open_cfw_cy8c_initialize(void)
{
    open_cfw_cy8c_install_default_ops(OPEN_CFW_CY8C_OPS);
}
#endif

#if defined(OPEN_CFW_CY8C_BUILD_ALL) || defined(OPEN_CFW_CY8C_READ_TOUCH_FRAME_ONLY)
void open_cfw_cy8c_read_touch_frame(uint8_t *data)
{
    uint8_t frame[16];
    open_cfw_cy8c_zero(frame, 16u);
    if (data == (uint8_t *)0) {
        return;
    }
    (void)open_cfw_cy8c_read_command(OPEN_CFW_CY8C_OPS, frame, 16u);
    open_cfw_cy8c_copy(data, frame, 16u);
}
#endif

#if defined(OPEN_CFW_CY8C_BUILD_ALL) || defined(OPEN_CFW_CY8C_READ_DIFFERENCE_ONLY)
int32_t open_cfw_cy8c_read_difference(uint8_t *data)
{
    uint8_t difference[10];
    int32_t status;
    open_cfw_cy8c_zero(difference, 10u);
    status = OPEN_CFW_CY8C_OPS->register_read(4u, difference, 10u);
    if (status == 0 && data != (uint8_t *)0) {
        open_cfw_cy8c_copy(data, difference, 10u);
    }
    return status;
}
#endif

#if defined(OPEN_CFW_CY8C_BUILD_ALL) || defined(OPEN_CFW_CY8C_PREPARE_PROXIMITY_BASELINE_ONLY)
int32_t open_cfw_cy8c_prepare_proximity_baseline(uint32_t *value)
{
    uint8_t bytes[4];
    volatile uint8_t *scratch = OPEN_CFW_CY8C_BASELINE_SCRATCH;
    int32_t status;
    open_cfw_cy8c_zero(bytes, 4u);
    if (value == (uint32_t *)0) {
        return -1;
    }
    status = open_cfw_cy8c_write_command(OPEN_CFW_CY8C_OPS, bytes, 4u);
    scratch[0] = bytes[0];
    scratch[1] = bytes[1];
    scratch[2] = bytes[2];
    scratch[3] = bytes[3];
    *value = ((uint32_t)scratch[0] << 24) |
        ((uint32_t)scratch[1] << 16) |
        ((uint32_t)scratch[2] << 8) | (uint32_t)scratch[3];
    return status;
}
#endif

#if defined(OPEN_CFW_CY8C_BUILD_ALL) || defined(OPEN_CFW_CY8C_SAVE_PROXIMITY_BASELINE_ONLY)
int32_t open_cfw_cy8c_save_proximity_baseline(void)
{
    return open_cfw_cy8c_save_command(OPEN_CFW_CY8C_OPS) == 0 ? 0 : -1;
}
#endif

#if defined(OPEN_CFW_CY8C_BUILD_ALL) || defined(OPEN_CFW_CY8C_READ_PROXIMITY_BASELINE_ONLY)
uint16_t open_cfw_cy8c_read_proximity_baseline(void)
{
    uint16_t value = 0u;
    if (open_cfw_cy8c_read_baseline_command(OPEN_CFW_CY8C_OPS, &value) != 0 ||
        open_cfw_cy8c_gesture_threshold_valid(&value) == 0u) {
        return 0xffffu;
    }
    return value;
}
#endif

#if defined(OPEN_CFW_CY8C_BUILD_ALL) || defined(OPEN_CFW_CY8C_WRITE_GESTURE_CFG_ONLY)
int32_t open_cfw_cy8c_write_gesture_cfg(uint16_t *threshold)
{
    return open_cfw_cy8c_write_gesture_private(
        OPEN_CFW_CY8C_OPS, threshold
    ) == 0 ? 0 : -1;
}
#endif

#if defined(OPEN_CFW_CY8C_BUILD_ALL) || defined(OPEN_CFW_CY8C_READ_GESTURE_CFG_ONLY)
int32_t open_cfw_cy8c_read_gesture_cfg(uint16_t *threshold)
{
    return open_cfw_cy8c_read_gesture_private(
        OPEN_CFW_CY8C_OPS, threshold
    ) == 0 ? 0 : -1;
}
#endif
