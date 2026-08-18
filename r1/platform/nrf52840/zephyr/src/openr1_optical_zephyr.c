#include "openr1_optical_zephyr.h"

#include <errno.h>
#include <math.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

#include <zephyr/devicetree.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/atomic.h>

#include "openr1_motion_zephyr.h"
#include "openr1_software_twi_zephyr.h"
#include "openr1_yhm2710_zephyr.h"
#include "model_data/r1_model_data.h"
#include "quantized_runtime/quantized_runtime.h"
#include "r1_gh3x2x_bind.h"
#include "r1_gh3x2x_port.h"
#include "r1_gh3x2x_provider_composer.h"
#include "r1_gh3x2x_reconstructed_roots.h"

/* Public, source-built Goodix democode entry points. The binary algorithm
 * archives are deliberately not linked. Reconstructed roots are admitted
 * only after their complete source-owned state and execution providers have
 * been bound below; any absent row remains fail-closed. */
void Gh3x2xDemoInterruptProcess(void);
void hal_gh3x2x_int_handler_call_back(void);
const void *goodix_spo2_config_get_instance(void);

#define OPENR1_OPTICAL_NODE DT_NODELABEL(openr1_optical)
#define OPENR1_GOODIX_DEVICE_ID UINT8_C(0x28)
#define OPENR1_GOODIX_COMMAND_BYTES 2u
#define OPENR1_GOODIX_GSENSOR_LIMIT 31u

typedef struct {
    int (*initialize)(void);
    int (*start)(r1_goodix_stock_profile);
    int (*switch_profile)(r1_goodix_switch_selection);
    int (*stop)(void);
    int (*start_functions)(uint32_t);
    int (*stop_functions)(uint32_t);
    bool (*provider_available)(void);
    bool (*prepared)(void);
    uint32_t (*interrupt_count)(void);
    uint32_t (*raw_frame_count)(void);
    int (*last_error)(void);
    const void *(*spo2_configuration)(void);
} openr1_optical_zephyr_api;

static const struct gpio_dt_spec optical_interrupt =
    GPIO_DT_SPEC_GET(OPENR1_OPTICAL_NODE, optical_interrupt_gpios);
static const struct gpio_dt_spec optical_emitter =
    GPIO_DT_SPEC_GET(OPENR1_OPTICAL_NODE, optical_emitter_gpios);
static const struct gpio_dt_spec optical_reset =
    GPIO_DT_SPEC_GET(OPENR1_OPTICAL_NODE, optical_reset_gpios);

K_MUTEX_DEFINE(optical_provider_mutex);

static struct gpio_callback optical_interrupt_callback;
static struct k_work optical_interrupt_work;
static r1_goodix_adapter optical_adapter;
static atomic_t optical_interrupts;
static atomic_t raw_frames;
static atomic_t last_error;
static atomic_t worn_state;
static atomic_t interrupt_armed;
static atomic_t board_prepared;
static bool interrupt_callback_installed;
static bool module_initialized;
static r1_gh3x2x_provider_composer algorithm_composer;
static r1_gh3x2x_algo_provider algorithm_provider;
static r1_gh3x2x_hba_root_context hba_root;
static r1_gh3x2x_hba_reconstructed_state hba_reconstructed_state;
static r1_gh3x2x_hrv_root_context hrv_root;
static r1_gh3x2x_hrv_reconstructed_state hrv_reconstructed_state;
static r1_gh3x2x_spo2_root_context spo2_root;
static r1_gh3x2x_spo2_reconstructed_state spo2_reconstructed_state;
static goodix_primitives_hr_configuration hba_configuration;
static quantized_runtime hba_quantized_runtime;
static goodix_primitives_hba_runtime_bindings hba_runtime_bindings;
static uint32_t hba_elapsed_slots[1] = {1u};
static goodix_primitives_elapsed_state hba_elapsed_state = {
    .slot_timestamps = hba_elapsed_slots,
    .slot_count = 1u,
};
static goodix_primitives_float_span hba_mode_buffers[3];
static const uint8_t hba_filter_code[1] = {0u};

/* Exact six words returned by retail 0x0006DA9C from 0x0009D5EC. */
static const goodix_primitives_hrv_configuration r1_hrv_configuration = {
    .identity = 1u,
    .sample_count = 100u,
    .calibration = {200000, 100000, 30000, 30000},
};

static void *optical_algorithm_allocate(void *context, size_t bytes) {
    (void)context;
    return k_malloc(bytes);
}

static void optical_algorithm_release(void *context, void *allocation) {
    (void)context;
    k_free(allocation);
}

static float optical_algorithm_square_root(float value) {
    if (value <= 0.0f) {
        return 0.0f;
    }
    float estimate = value > 1.0f ? value : 1.0f;
    for (size_t index = 0u; index < 12u; ++index) {
        estimate = 0.5f * (estimate + value / estimate);
    }
    return estimate;
}

static double optical_algorithm_power(double base, double exponent) {
    return pow(base, exponent);
}

static int32_t optical_algorithm_integrity_encode(int32_t value) {
    union {
        uint32_t unsigned_value;
        int32_t signed_value;
    } converted = {.signed_value = value};
    converted.unsigned_value =
        goodix_primitives_integrity_encode(converted.unsigned_value);
    return converted.signed_value;
}

static void optical_algorithm_qsort(
    void *base, size_t count, size_t size,
    quantized_runtime_compare_fn compare) {
    qsort(base, count, size, compare);
}

static bool optical_prepare_hba_runtime(void) {
    const uint32_t *const words = r1_goodix_hba_configuration_words;
    hba_configuration = (goodix_primitives_hr_configuration){
        .algorithm_mode = (uint8_t)words[0],
        .sample_rate = words[1],
        .minimum_batch = (int32_t)words[2],
        .secondary_window_override = words[3],
        .primary_window_override = words[4],
        .feature_stride = (int32_t)words[5],
        .terminal_default = (int32_t)words[6],
        .candidate_limit = words[7],
        .owner_word = words[8],
    };
    const quantized_runtime_providers providers = {
        .fminf_fn = fminf,
        .fmaxf_fn = fmaxf,
        .floorf_fn = floorf,
        .expf_fn = expf,
        .qsort_fn = optical_algorithm_qsort,
        .vector_95b20 =
            (uintptr_t)&quantized_runtime_float_multiply_execute,
        .vector_36dcc =
            (uintptr_t)&quantized_runtime_float_concatenate_two_execute,
        .vector_30534 =
            (uintptr_t)&quantized_runtime_int8_to_float_execute,
        .vector_35d12 =
            (uintptr_t)&quantized_runtime_float_strided_copy_2d_execute,
        .vector_7ca94 =
            (uintptr_t)&quantized_runtime_float_pool_1d_execute,
    };
    quantized_runtime_initialize(&hba_quantized_runtime, &providers);
    hba_runtime_bindings = (goodix_primitives_hba_runtime_bindings){
        .integrity_transform = optical_algorithm_integrity_encode,
        .quantized = &hba_quantized_runtime,
        .elapsed_state = &hba_elapsed_state,
        .mode_buffers = hba_mode_buffers,
        .exponential = expf,
        .logarithm_base_10 = log10f,
        .square_root = optical_algorithm_square_root,
    };
    return hba_configuration.algorithm_mode == 0u &&
        hba_configuration.sample_rate == 25u &&
        hba_configuration.minimum_batch == 4;
}

static bool optical_bind_reconstructed_algorithms(void) {
    r1_gh3x2x_algo_unbind_provider();
    r1_gh3x2x_provider_composer_initialize(&algorithm_composer);
    hba_root = (r1_gh3x2x_hba_root_context){
        .filter_code = hba_filter_code,
        .filter_code_count = sizeof(hba_filter_code),
    };
    hba_reconstructed_state = (r1_gh3x2x_hba_reconstructed_state){
        .configuration = &hba_configuration,
        .runtime_bindings = &hba_runtime_bindings,
        .allocate = optical_algorithm_allocate,
        .release = optical_algorithm_release,
    };
    hrv_root = (r1_gh3x2x_hrv_root_context){0};
    hrv_reconstructed_state = (r1_gh3x2x_hrv_reconstructed_state){
        .configuration = &r1_hrv_configuration,
        .allocate = optical_algorithm_allocate,
        .release = optical_algorithm_release,
        .square_root = optical_algorithm_square_root,
    };
    spo2_root = (r1_gh3x2x_spo2_root_context){0};
    spo2_reconstructed_state = (r1_gh3x2x_spo2_reconstructed_state){
        .bindings = {
            .quantized = &hba_quantized_runtime,
            .power = optical_algorithm_power,
            .square_root = optical_algorithm_square_root,
            .floor = floorf,
            .exponential = expf,
            .arc_tangent = atan,
            .double_exponential = exp,
            .allocate = optical_algorithm_allocate,
            .release = optical_algorithm_release,
        },
        .weights_version = "gh3x2x-v2.23_7ecd2a",
    };
    r1_gh3x2x_root_binding binding;
    if (!optical_prepare_hba_runtime() ||
            !r1_gh3x2x_make_reconstructed_hba_root_binding(
                &hba_root, &hba_reconstructed_state, &binding) ||
            !r1_gh3x2x_provider_composer_bind_root(
                &algorithm_composer, R1_GH3X2X_ALGO_FUNCTION_HR,
                &binding) ||
            !r1_gh3x2x_make_reconstructed_hrv_root_binding(
            &hrv_root, &hrv_reconstructed_state, &binding) ||
            !r1_gh3x2x_provider_composer_bind_root(
                &algorithm_composer, R1_GH3X2X_ALGO_FUNCTION_HRV,
                &binding) ||
            !r1_gh3x2x_make_reconstructed_spo2_root_binding(
                &spo2_root, &spo2_reconstructed_state, &binding) ||
            !r1_gh3x2x_provider_composer_bind_root(
                &algorithm_composer, R1_GH3X2X_ALGO_FUNCTION_SPO2,
                &binding) ||
            !r1_gh3x2x_provider_composer_build(
                &algorithm_composer, &algorithm_provider)) {
        return false;
    }
    r1_gh3x2x_algo_bind_provider(&algorithm_provider);
    return r1_gh3x2x_algo_provider_bound();
}

static void record_error(int error) {
    if (error != 0) {
        atomic_set(&last_error, (atomic_val_t)error);
    }
}

static void zero_bytes(uint8_t *bytes, uint16_t length) {
    if (bytes != NULL) {
        memset(bytes, 0, length);
    }
}

static uint32_t optical_bus_open(void) {
    const int error = openr1_software_twi_zephyr_open(
        SOFTWARE_TWI_BUS_I2C_4);
    if (error != 0) {
        record_error(-EIO);
    }
    return error == 0 ? SOFTWARE_TWI_STATUS_OK
                      : SOFTWARE_TWI_STATUS_BAD_ARGUMENT;
}

static void optical_i2c_init(void *context) {
    (void)context;
    (void)optical_bus_open();
}

static void optical_i2c_write(void *context, uint8_t device_id,
                              const uint8_t *data, uint16_t length) {
    (void)context;
    if (device_id != OPENR1_GOODIX_DEVICE_ID ||
        (length != 0u && data == NULL)) {
        record_error(-EINVAL);
        return;
    }
    const software_twi_write_request request = {
        .address = device_id,
        .buffer = data,
        .length = length,
    };
    if (openr1_software_twi_zephyr_write(
            SOFTWARE_TWI_BUS_I2C_4, &request) != 0) {
        record_error(-EIO);
    }
}

static void optical_i2c_read(void *context, uint8_t device_id,
                             const uint8_t *command,
                             uint16_t command_length, uint8_t *data,
                             uint16_t data_length) {
    (void)context;
    zero_bytes(data, data_length);
    if (device_id != OPENR1_GOODIX_DEVICE_ID || data == NULL ||
        command == NULL || command_length != OPENR1_GOODIX_COMMAND_BYTES ||
        data_length == 0u) {
        record_error(-EINVAL);
        return;
    }
    const software_twi_read_request request = {
        .address = device_id,
        .register_address =
            (uint16_t)(((uint16_t)command[0] << 8u) | command[1]),
        .buffer = data,
        .length = data_length,
    };
    if (openr1_software_twi_zephyr_read(
            SOFTWARE_TWI_BUS_I2C_4, &request) != 0) {
        zero_bytes(data, data_length);
        record_error(-EIO);
    }
}

static void optical_interrupt_handler(const struct device *port,
                                      struct gpio_callback *callback,
                                      gpio_port_pins_t pins) {
    (void)port;
    (void)callback;
    (void)pins;
    if (atomic_get(&interrupt_armed) == 0) {
        return;
    }
    (void)atomic_inc(&optical_interrupts);
    hal_gh3x2x_int_handler_call_back();
    (void)k_work_submit(&optical_interrupt_work);
}

static void optical_interrupt_process(struct k_work *work) {
    (void)work;
    if (atomic_get(&interrupt_armed) == 0 ||
        atomic_get(&board_prepared) == 0 ||
        k_mutex_lock(&optical_provider_mutex, K_FOREVER) != 0) {
        return;
    }
    if (atomic_get(&interrupt_armed) != 0 &&
        atomic_get(&board_prepared) != 0) {
        Gh3x2xDemoInterruptProcess();
    }
    (void)k_mutex_unlock(&optical_provider_mutex);
}

static void optical_int_pin_init(void *context) {
    (void)context;
    int error = gpio_pin_configure_dt(&optical_interrupt, GPIO_INPUT);
    if (error == 0 && !interrupt_callback_installed) {
        gpio_init_callback(&optical_interrupt_callback,
                           optical_interrupt_handler,
                           BIT(optical_interrupt.pin));
        error = gpio_add_callback(optical_interrupt.port,
                                  &optical_interrupt_callback);
        if (error == 0) {
            interrupt_callback_installed = true;
        }
    }
    if (error == 0) {
        error = gpio_pin_interrupt_configure_dt(
            &optical_interrupt, GPIO_INT_EDGE_TO_ACTIVE);
    }
    if (error == 0) {
        atomic_set(&interrupt_armed, 1);
    } else {
        record_error(error);
    }
}

static void optical_reset_pin_init(void *context) {
    (void)context;
    const int error = gpio_pin_configure_dt(&optical_reset,
                                            GPIO_OUTPUT_INACTIVE);
    record_error(error);
}

static void optical_reset_pin_ctrl(void *context, uint8_t level) {
    (void)context;
    record_error(gpio_pin_set_dt(&optical_reset, level != 0u));
}

static void optical_gsensor_get(void *context,
                                r1_gh3x2x_gsensor_sample *samples,
                                uint16_t *count) {
    (void)context;
    if (samples == NULL || count == NULL ||
        !openr1_motion_zephyr_is_enabled()) {
        return;
    }
    r1_motion_sample motion_samples[OPENR1_GOODIX_GSENSOR_LIMIT];
    size_t sample_count = 0u;
    const int error = openr1_motion_zephyr_read_fifo(
        motion_samples, OPENR1_GOODIX_GSENSOR_LIMIT, &sample_count);
    if (error == 0) {
        for (size_t index = 0u; index < sample_count; ++index) {
            samples[index].x = motion_samples[index].x;
            samples[index].y = motion_samples[index].y;
            samples[index].z = motion_samples[index].z;
        }
        *count = (uint16_t)sample_count;
    } else {
        record_error(error);
    }
}

static void optical_delay_us(void *context, uint32_t microseconds) {
    (void)context;
    k_busy_wait(microseconds);
}

static void optical_rawdata_notify(void *context, const uint32_t *rawdata,
                                   uint32_t count) {
    (void)context;
    if (rawdata != NULL && count != 0u) {
        (void)atomic_inc(&raw_frames);
    }
}

static void optical_wear_notify(void *context, bool worn) {
    (void)context;
    atomic_set(&worn_state, worn ? 1 : 0);
}

static bool optical_board_prepare(void *context) {
    (void)context;
    if (atomic_get(&board_prepared) != 0) {
        return true;
    }
    if (!openr1_yhm2710_zephyr_optical_acquire()) {
        record_error(-EACCES);
        return false;
    }
    int error = gpio_pin_set_dt(&optical_reset, 0);
    if (error == 0) {
        error = gpio_pin_set_dt(&optical_emitter, 1);
    }
    if (error != 0) {
        (void)openr1_yhm2710_zephyr_optical_release();
        record_error(error);
        return false;
    }
    atomic_set(&board_prepared, 1);
    return true;
}

static void optical_board_shutdown(void *context) {
    (void)context;
    atomic_clear(&interrupt_armed);
    if (interrupt_callback_installed) {
        record_error(gpio_pin_interrupt_configure_dt(
            &optical_interrupt, GPIO_INT_DISABLE));
    }
    record_error(gpio_pin_set_dt(&optical_reset, 0));
    record_error(gpio_pin_set_dt(&optical_emitter, 0));
    openr1_software_twi_zephyr_close(SOFTWARE_TWI_BUS_I2C_4);
    if (atomic_get(&board_prepared) != 0 &&
        !openr1_yhm2710_zephyr_optical_release()) {
        record_error(-EIO);
    }
    atomic_clear(&board_prepared);
}

static void optical_board_delay_ms(void *context, uint32_t milliseconds) {
    (void)context;
    k_msleep(milliseconds);
}

static int map_error(r1_error error) {
    if (error == R1_OK) {
        return 0;
    }
    if (error == R1_ERROR_ARGUMENT) {
        return -EINVAL;
    }
    if (error == R1_ERROR_UNSUPPORTED) {
        return -ENOTSUP;
    }
    return -EIO;
}

int openr1_optical_zephyr_initialize(void) {
    static const r1_gh3x2x_hal goodix_hal = {
        .context = NULL,
        .i2c_init = optical_i2c_init,
        .i2c_write = optical_i2c_write,
        .i2c_read = optical_i2c_read,
        .int_pin_init = optical_int_pin_init,
        .reset_pin_init = optical_reset_pin_init,
        .reset_pin_ctrl = optical_reset_pin_ctrl,
        .gsensor_get = optical_gsensor_get,
        .delay_us = optical_delay_us,
        .log = NULL,
        .rawdata_notify = optical_rawdata_notify,
        .wear_notify = optical_wear_notify,
    };
    static const r1_goodix_board_ops board_ops = {
        .prepare = optical_board_prepare,
        .shutdown = optical_board_shutdown,
        .delay_ms = optical_board_delay_ms,
    };
    if (module_initialized) {
        return -EALREADY;
    }
    if (!gpio_is_ready_dt(&optical_interrupt) ||
        !gpio_is_ready_dt(&optical_emitter) ||
        !gpio_is_ready_dt(&optical_reset)) {
        return -ENODEV;
    }
    int error = gpio_pin_configure_dt(&optical_emitter,
                                      GPIO_OUTPUT_INACTIVE);
    if (error == 0) {
        error = gpio_pin_configure_dt(&optical_reset,
                                      GPIO_OUTPUT_INACTIVE);
    }
    if (error != 0) {
        return error;
    }
    interrupt_callback_installed = false;
    atomic_clear(&interrupt_armed);
    atomic_clear(&board_prepared);
    atomic_clear(&optical_interrupts);
    atomic_clear(&raw_frames);
    atomic_clear(&last_error);
    atomic_clear(&worn_state);
    k_work_init(&optical_interrupt_work, optical_interrupt_process);
    error = openr1_software_twi_zephyr_initialize();
    if (error != 0 && error != -EALREADY) {
        return error;
    }
    r1_gh3x2x_port_bind_hal(&goodix_hal);
    if (!optical_bind_reconstructed_algorithms()) {
        r1_gh3x2x_port_unbind_hal();
        record_error(-EIO);
        return -EIO;
    }
    r1_goodix_adapter_initialize(&optical_adapter);
    error = map_error(r1_goodix_adapter_bind(
        &optical_adapter, r1_gh3x2x_bind_provider_ops(), NULL,
        &board_ops, NULL));
    if (error != 0) {
        r1_gh3x2x_algo_unbind_provider();
        r1_gh3x2x_port_unbind_hal();
        record_error(error);
    } else {
        module_initialized = true;
    }
    return error;
}

int openr1_optical_zephyr_start(r1_goodix_stock_profile profile) {
    if (!module_initialized ||
        !openr1_yhm2710_zephyr_provider_available()) {
        return -EACCES;
    }
    if (k_mutex_lock(&optical_provider_mutex, K_FOREVER) != 0) {
        return -EAGAIN;
    }
    const int error = map_error(r1_goodix_start_stock_profile(
        &optical_adapter, profile));
    (void)k_mutex_unlock(&optical_provider_mutex);
    record_error(error);
    return error;
}

int openr1_optical_zephyr_switch(r1_goodix_switch_selection profile) {
    if (!module_initialized) {
        return -EACCES;
    }
    if (k_mutex_lock(&optical_provider_mutex, K_FOREVER) != 0) {
        return -EAGAIN;
    }
    const int error = map_error(r1_goodix_switch_profile(
        &optical_adapter, profile));
    (void)k_mutex_unlock(&optical_provider_mutex);
    record_error(error);
    return error;
}

int openr1_optical_zephyr_stop(void) {
    if (!module_initialized) {
        return -EACCES;
    }
    if (k_mutex_lock(&optical_provider_mutex, K_FOREVER) != 0) {
        return -EAGAIN;
    }
    const int error = map_error(r1_goodix_stop_stock_profiles(
        &optical_adapter));
    (void)k_mutex_unlock(&optical_provider_mutex);
    record_error(error);
    return error;
}

int openr1_optical_zephyr_start_functions(uint32_t function_mask) {
    if (!module_initialized ||
        !openr1_yhm2710_zephyr_provider_available()) {
        return -EACCES;
    }
    if (k_mutex_lock(&optical_provider_mutex, K_FOREVER) != 0) {
        return -EAGAIN;
    }
    const int error = map_error(r1_goodix_start_functions(
        &optical_adapter, function_mask));
    (void)k_mutex_unlock(&optical_provider_mutex);
    record_error(error);
    return error;
}

int openr1_optical_zephyr_stop_functions(uint32_t function_mask) {
    if (!module_initialized) {
        return -EACCES;
    }
    if (k_mutex_lock(&optical_provider_mutex, K_FOREVER) != 0) {
        return -EAGAIN;
    }
    const int error = map_error(r1_goodix_stop_functions(
        &optical_adapter, function_mask));
    (void)k_mutex_unlock(&optical_provider_mutex);
    record_error(error);
    return error;
}

bool openr1_optical_zephyr_provider_available(void) {
    return module_initialized &&
        openr1_yhm2710_zephyr_provider_available() &&
        r1_goodix_provider_available(&optical_adapter);
}

bool openr1_optical_zephyr_prepared(void) {
    return atomic_get(&board_prepared) != 0;
}

uint32_t openr1_optical_zephyr_interrupt_count(void) {
    return (uint32_t)atomic_get(&optical_interrupts);
}

uint32_t openr1_optical_zephyr_raw_frame_count(void) {
    return (uint32_t)atomic_get(&raw_frames);
}

int openr1_optical_zephyr_last_error(void) {
    return (int)atomic_get(&last_error);
}

__attribute__((used, section(".openr1_platform_api")))
static const openr1_optical_zephyr_api optical_zephyr_api = {
    openr1_optical_zephyr_initialize,
    openr1_optical_zephyr_start,
    openr1_optical_zephyr_switch,
    openr1_optical_zephyr_stop,
    openr1_optical_zephyr_start_functions,
    openr1_optical_zephyr_stop_functions,
    openr1_optical_zephyr_provider_available,
    openr1_optical_zephyr_prepared,
    openr1_optical_zephyr_interrupt_count,
    openr1_optical_zephyr_raw_frame_count,
    openr1_optical_zephyr_last_error,
    goodix_spo2_config_get_instance,
};
