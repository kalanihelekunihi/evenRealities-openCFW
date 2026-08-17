#include "openr1_temperature_zephyr.h"

#include <errno.h>
#include <stddef.h>

#include <zephyr/kernel.h>
#include <zephyr/sys/atomic.h>

#include "gxt310/gxt310.h"
#include "openr1_databases_zephyr.h"
#include "openr1_software_twi_zephyr.h"

#define OPENR1_GXT310_REGISTER_TEMPERATURE UINT8_C(0x00)
#define OPENR1_GXT310_REGISTER_ID UINT8_C(0x03)
#define OPENR1_GXT310_EXPECTED_ID UINT8_C(0x50)
#define OPENR1_GXT310_STARTUP_MS UINT32_C(80)
#define OPENR1_GXT310_SAMPLE_INTERVAL_MS UINT32_C(5)

typedef struct {
    int (*initialize)(void);
    bool (*provider_available)(void);
    int (*read_pair)(int32_t[R1_TEMPERATURE_PAIR_SENSOR_COUNT]);
    int (*read_stream)(uint16_t *);
    int (*acquire)(r1_temperature_pair_result *);
    uint32_t (*failure_count)(void);
    int (*last_error)(void);
} openr1_temperature_zephyr_api;

static gxt310_provider temperature_provider;
static atomic_t failures;
static atomic_t last_error;
static bool module_initialized;
static bool provider_ready;
static r1_temperature_pair_calibration persisted_calibration;
static bool persisted_calibration_present;

static void record_error(int error) {
    if (error != 0) {
        (void)atomic_inc(&failures);
        atomic_set(&last_error, (atomic_val_t)error);
    }
}

static bool gxt_write(void *context, uint8_t address, uint16_t operation,
                      const uint8_t *bytes, size_t length) {
    (void)context;
    if (operation != GXT310_WRITE_OPERATION || bytes == NULL ||
        length != GXT310_COMMAND_BYTES) {
        return false;
    }
    const software_twi_write_request request = {
        .address = address,
        .register_address = bytes[0],
        .buffer = bytes + 1u,
        .length = 1u,
    };
    return openr1_software_twi_zephyr_write(
               SOFTWARE_TWI_BUS_I2C_2, &request) == 0;
}

static void gxt_failure(void *context, gxt310_failure_operation operation,
                        uint8_t address) {
    (void)context;
    (void)operation;
    (void)address;
    record_error(-EIO);
}

static bool gxt_read(uint8_t address, uint8_t register_address,
                     uint8_t output[2]) {
    const software_twi_read_request request = {
        .address = address,
        .register_address = register_address,
        .buffer = output,
        .length = 2u,
    };
    const int error = openr1_software_twi_zephyr_read(
        SOFTWARE_TWI_BUS_I2C_2, &request);
    if (error != 0) {
        record_error(error);
        return false;
    }
    return true;
}

static bool read_temperature(uint8_t address, int32_t *temperature) {
    uint8_t bytes[2] = {0u, 0u};
    if (temperature == NULL ||
        !gxt_read(address, OPENR1_GXT310_REGISTER_TEMPERATURE, bytes)) {
        return false;
    }
    *temperature = r1_temperature_gxt310_decode_milliunits(bytes);
    return true;
}

static bool begin_measurement(void) {
    const int error = openr1_software_twi_zephyr_open(
        SOFTWARE_TWI_BUS_I2C_2);
    if (error != 0) {
        record_error(error);
        return false;
    }
    if (gxt310_enable_pair(&temperature_provider) != GXT310_STATUS_SUCCESS) {
        openr1_software_twi_zephyr_close(SOFTWARE_TWI_BUS_I2C_2);
        return false;
    }
    k_msleep(OPENR1_GXT310_STARTUP_MS);
    return true;
}

static void end_measurement(void) {
    const uint32_t channel_0 = gxt310_channel_0_switch_mode(
        &temperature_provider, false);
    const uint32_t channel_2 = gxt310_channel_2_switch_mode(
        &temperature_provider, false);
    if (channel_0 != GXT310_STATUS_SUCCESS ||
        channel_2 != GXT310_STATUS_SUCCESS) {
        record_error(-EIO);
    }
    openr1_software_twi_zephyr_close(SOFTWARE_TWI_BUS_I2C_2);
}

static bool self_check(void) {
    if (!begin_measurement()) {
        return false;
    }
    uint8_t channel_0[2] = {0u, 0u};
    uint8_t channel_2[2] = {0u, 0u};
    const bool read_0 = gxt_read(
        GXT310_CHANNEL_0_ADDRESS, OPENR1_GXT310_REGISTER_ID, channel_0);
    const bool read_2 = gxt_read(
        GXT310_CHANNEL_2_ADDRESS, OPENR1_GXT310_REGISTER_ID, channel_2);
    end_measurement();
    return read_0 && read_2 &&
        channel_0[0] == OPENR1_GXT310_EXPECTED_ID &&
        channel_2[0] == OPENR1_GXT310_EXPECTED_ID;
}

int openr1_temperature_zephyr_initialize(void) {
    if (module_initialized) {
        return -EALREADY;
    }
    int error = openr1_software_twi_zephyr_initialize();
    if (error != 0 && error != -EALREADY) {
        return error;
    }
    module_initialized = true;
    provider_ready = false;
    persisted_calibration_present =
        openr1_databases_zephyr_temperature_calibration(
            &persisted_calibration);
    atomic_clear(&failures);
    atomic_clear(&last_error);
    gxt310_provider_initialize(
        &temperature_provider, gxt_write, NULL, gxt_failure, NULL);
    if (self_check()) {
        provider_ready = true;
    } else {
        record_error(-ENODEV);
    }
    /* Missing or electrically unvalidated GXT310 hardware is fail-closed but
     * does not prevent BLE recovery and diagnostics from starting. */
    return 0;
}

bool openr1_temperature_zephyr_provider_available(void) {
    return provider_ready;
}

int openr1_temperature_zephyr_read_pair(
    int32_t channels[R1_TEMPERATURE_PAIR_SENSOR_COUNT]) {
    if (channels == NULL) {
        return -EINVAL;
    }
    if (!provider_ready || k_is_in_isr()) {
        return -EACCES;
    }
    if (!begin_measurement()) {
        return -EIO;
    }
    int32_t measured[R1_TEMPERATURE_PAIR_SENSOR_COUNT];
    const bool read_0 = read_temperature(
        GXT310_CHANNEL_0_ADDRESS, &measured[0]);
    const bool read_2 = read_temperature(
        GXT310_CHANNEL_2_ADDRESS, &measured[1]);
    end_measurement();
    if (!read_0 || !read_2) {
        return -EIO;
    }
    channels[0] = measured[0];
    channels[1] = measured[1];
    return 0;
}

int openr1_temperature_zephyr_read_stream(uint16_t *value) {
    if (value == NULL) {
        return -EINVAL;
    }
    int32_t channels[R1_TEMPERATURE_PAIR_SENSOR_COUNT];
    const int error = openr1_temperature_zephyr_read_pair(channels);
    if (error != 0) {
        return error;
    }
    const r1_temperature_pair_calibration *calibration =
        persisted_calibration_present ? &persisted_calibration : NULL;
    if (r1_temperature_pair_stream_value(
            channels, calibration, value) != R1_OK) {
        record_error(-EINVAL);
        return -EINVAL;
    }
    return 0;
}

int openr1_temperature_zephyr_acquire(r1_temperature_pair_result *result) {
    if (result == NULL) {
        return -EINVAL;
    }
    if (!provider_ready || k_is_in_isr()) {
        return -EACCES;
    }
    int32_t samples[R1_TEMPERATURE_PAIR_SENSOR_COUNT]
                   [R1_TEMPERATURE_PAIR_SAMPLE_COUNT];
    if (!begin_measurement()) {
        return -EIO;
    }
    bool success = true;
    for (size_t index = 0u;
         index < R1_TEMPERATURE_PAIR_SAMPLE_COUNT; ++index) {
        const bool read_0 = read_temperature(
            GXT310_CHANNEL_0_ADDRESS, &samples[0][index]);
        const bool read_2 = read_temperature(
            GXT310_CHANNEL_2_ADDRESS, &samples[1][index]);
        success = read_0 && read_2 && success;
        k_msleep(OPENR1_GXT310_SAMPLE_INTERVAL_MS);
    }
    end_measurement();
    if (!success) {
        return -EIO;
    }
    const r1_temperature_pair_calibration *calibration =
        persisted_calibration_present ? &persisted_calibration : NULL;
    if (r1_temperature_pair_reduce(samples, calibration, result) != R1_OK) {
        record_error(-EINVAL);
        return -EINVAL;
    }
    return 0;
}

uint32_t openr1_temperature_zephyr_failure_count(void) {
    return (uint32_t)atomic_get(&failures);
}

int openr1_temperature_zephyr_last_error(void) {
    return (int)atomic_get(&last_error);
}

__attribute__((used, section(".openr1_platform_api")))
static const openr1_temperature_zephyr_api temperature_zephyr_api = {
    openr1_temperature_zephyr_initialize,
    openr1_temperature_zephyr_provider_available,
    openr1_temperature_zephyr_read_pair,
    openr1_temperature_zephyr_read_stream,
    openr1_temperature_zephyr_acquire,
    openr1_temperature_zephyr_failure_count,
    openr1_temperature_zephyr_last_error,
};
