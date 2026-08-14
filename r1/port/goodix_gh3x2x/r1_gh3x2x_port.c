/*
 * openR1 port layer for the Goodix GH3X2X democode: board/HAL trampolines
 * and the goodix_mem integrator surface.  See r1_gh3x2x_port.h for the
 * contract.  Freestanding-safe: explicit loops, no C library calls.
 */

#include "r1_gh3x2x_port.h"

#include <stddef.h>

static r1_gh3x2x_hal port_hal;
static bool port_hal_bound;
static const r1_goodix_pool_fatal_ops *pool_ops;

void r1_gh3x2x_port_bind_hal(const r1_gh3x2x_hal *hal) {
    if (hal == NULL) {
        r1_gh3x2x_port_unbind_hal();
        return;
    }
    port_hal = *hal;
    port_hal_bound = true;
}

void r1_gh3x2x_port_unbind_hal(void) {
    uint8_t *bytes = (uint8_t *)&port_hal;
    for (size_t index = 0u; index < sizeof(port_hal); ++index) {
        bytes[index] = 0u;
    }
    port_hal_bound = false;
}

bool r1_gh3x2x_port_hal_bound(void) {
    return port_hal_bound;
}

void r1_gh3x2x_pool_bind(const r1_goodix_pool_fatal_ops *ops) {
    pool_ops = ops;
}

static void zero_bytes(uint8_t *data, uint16_t length) {
    for (uint16_t index = 0u; index < length; ++index) {
        data[index] = 0u;
    }
}

void gh3026_i2c_init(void) {
    if (port_hal_bound && port_hal.i2c_init != NULL) {
        port_hal.i2c_init(port_hal.context);
    }
}

void gh3026_i2c_write(uint8_t device_id, const uint8_t data[],
                      uint16_t length) {
    if (port_hal_bound && port_hal.i2c_write != NULL) {
        port_hal.i2c_write(port_hal.context, device_id, data, length);
    }
}

void gh3026_i2c_read(uint8_t device_id, const uint8_t command[],
                     uint16_t command_length, uint8_t data[],
                     uint16_t data_length) {
    if (data == NULL) {
        return;
    }
    if (port_hal_bound && port_hal.i2c_read != NULL) {
        port_hal.i2c_read(port_hal.context, device_id, command,
                          command_length, data, data_length);
        return;
    }
    /* Unbound or no read hook: fail closed with a zeroed buffer so the
     * driver's magic-value checks (e.g. the 0xAA55 communicate-confirm)
     * fail instead of consuming stale stack data. */
    zero_bytes(data, data_length);
}

void gh3026_int_pin_init(void) {
    if (port_hal_bound && port_hal.int_pin_init != NULL) {
        port_hal.int_pin_init(port_hal.context);
    }
}

void gh3026_reset_pin_init(void) {
    if (port_hal_bound && port_hal.reset_pin_init != NULL) {
        port_hal.reset_pin_init(port_hal.context);
    }
}

void gh3026_reset_pin_ctrl(uint8_t level) {
    if (port_hal_bound && port_hal.reset_pin_ctrl != NULL) {
        port_hal.reset_pin_ctrl(port_hal.context, level);
    }
}

void gh3026_gsensor_data_get(r1_gh3x2x_gsensor_sample samples[],
                             uint16_t *count) {
    if (count == NULL) {
        return;
    }
    *count = 0u;
    if (port_hal_bound && port_hal.gsensor_get != NULL) {
        port_hal.gsensor_get(port_hal.context, samples, count);
    }
}

void delay_us(uint32_t microseconds) {
    if (port_hal_bound && port_hal.delay_us != NULL) {
        port_hal.delay_us(port_hal.context, microseconds);
    }
}

void gh3x2x_print_fmt(const char *format, ...) {
    /* Varargs are intentionally not formatted: the freestanding target has
     * no vsnprintf.  The format text itself is forwarded verbatim. */
    if (port_hal_bound && port_hal.log != NULL && format != NULL) {
        port_hal.log(port_hal.context, format);
    }
}

void gh3x2x_rawdata_notify(uint32_t *rawdata, uint32_t count) {
    if (port_hal_bound && port_hal.rawdata_notify != NULL) {
        port_hal.rawdata_notify(port_hal.context, rawdata, count);
    }
}

void gh3x2x_wear_evt_notify(bool worn) {
    if (port_hal_bound && port_hal.wear_notify != NULL) {
        port_hal.wear_notify(port_hal.context, worn);
    }
}

void Gh3x2xPoolIsNotEnough(void) {
    /* goodix_mem reports exhaustion with no payload at this boundary; the
     * recovered stock body logs "sensor_algo_mem_fatal, info1: %u" and
     * halts.  info1 is unavailable across this void(void) seam, so the
     * redacted diagnostic records 0. */
    r1_goodix_pool_not_enough(pool_ops, 0u);
}
