#include "openr1_sensor_stream_zephyr.h"

#include <errno.h>
#include <stddef.h>
#include <stdint.h>

#include <zephyr/kernel.h>
#include <zephyr/sys/atomic.h>

#include "generic_device_registry/generic_device_registry.h"
#include "gomore_primitives/gomore_primitives.h"
#include "openr1_databases_zephyr.h"
#include "openr1_motion_zephyr.h"
#include "openr1_temperature_zephyr.h"

typedef struct {
    int (*initialize)(void);
    uint32_t (*poll)(void);
    bool (*is_ready)(void);
    sensor_stream *(*framework)(void);
    sensor_stream_listener *(*register_accelerometer)(
        const char *, sensor_stream_listener_callback, uint8_t);
    void (*unregister_accelerometer)(sensor_stream_listener *);
    sensor_stream_listener *(*register_temperature)(
        const char *, sensor_stream_listener_callback, uint8_t);
    void (*unregister_temperature)(sensor_stream_listener *);
    int (*temperature_once_set)(bool);
    bool (*temperature_once_active)(void);
    uint32_t (*temperature_once_successes)(void);
    uint32_t (*temperature_once_timeouts)(void);
    int (*gomore_accelerometer_stage_set)(bool);
    bool (*gomore_accelerometer_stage_active)(void);
    uint32_t (*gomore_accelerometer_stage_batches)(void);
    uint32_t (*gomore_accelerometer_stage_failures)(void);
    uint32_t (*motion_batch_count)(void);
    uint32_t (*motion_failure_count)(void);
    uint32_t (*temperature_sample_count)(void);
    uint32_t (*temperature_failure_count)(void);
} openr1_sensor_stream_zephyr_api;

static sensor_stream stream_framework;
static sensor_stream_object *accelerometer_object;
static sensor_stream_object *temperature_object;
static k_tid_t owner_thread;
static atomic_t motion_batches;
static atomic_t motion_failures;
static atomic_t temperature_samples;
static atomic_t temperature_failures;
static atomic_t temperature_once_successes;
static atomic_t temperature_once_timeouts;
static atomic_t gomore_accelerometer_stage_batches;
static atomic_t gomore_accelerometer_stage_failures;
static atomic_t framework_faults;
static gomore_primitives_scaled_sample_state temperature_once_state;
static sensor_stream_listener *temperature_once_listener;
static gomore_primitives_topic_input_state gomore_topic_input;
static sensor_stream_listener *gomore_accelerometer_stage_listener;
static bool stream_ready;

static void *stream_allocate(uint32_t size) {
    return size == 0u ? NULL : k_malloc((size_t)size);
}

static void *registry_allocate(size_t size) {
    return size == 0u ? NULL : k_malloc(size);
}

static void stream_free(void *pointer) {
    k_free(pointer);
}

static generic_device_registry_link_list list_bridge(
    const sensor_stream_list_descriptor *descriptor) {
    return (generic_device_registry_link_list){
        .link_offset = descriptor->stride,
        .head = descriptor->head,
        .tail = descriptor->tail,
    };
}

static void *stream_list_first(sensor_stream_list_descriptor *descriptor) {
    if (descriptor == NULL) {
        return NULL;
    }
    const generic_device_registry_link_list bridge = list_bridge(descriptor);
    return generic_device_registry_list_head(&bridge);
}

static void *stream_list_next(sensor_stream_list_descriptor *descriptor,
                              void *node) {
    if (descriptor == NULL) {
        return NULL;
    }
    const generic_device_registry_link_list bridge = list_bridge(descriptor);
    return generic_device_registry_list_next(&bridge, node);
}

static void stream_list_remove(sensor_stream_list_descriptor *descriptor,
                               void *node) {
    if (descriptor == NULL) {
        return;
    }
    generic_device_registry_link_list bridge = list_bridge(descriptor);
    generic_device_registry_list_remove(&bridge, node);
    descriptor->head = bridge.head;
    descriptor->tail = bridge.tail;
}

static void *stream_list_push_back_allocate(
    sensor_stream_list_descriptor *descriptor) {
    if (descriptor == NULL) {
        return NULL;
    }
    generic_device_registry_link_list bridge = list_bridge(descriptor);
    void *node = generic_device_registry_list_append_alloc(
        &bridge, registry_allocate);
    descriptor->head = bridge.head;
    descriptor->tail = bridge.tail;
    return node;
}

static uint32_t stream_tick(void) {
    /* prj.conf pins the recovered scheduler base to exactly 1024 Hz. */
    return (uint32_t)k_uptime_ticks();
}

static void stream_diagnostic(const char *message, const char *detail,
                              uint32_t value) {
    (void)message;
    (void)detail;
    (void)value;
}

static void stream_fault(void) {
    (void)atomic_inc(&framework_faults);
}

static void stream_wake(void *context) {
    (void)context;
    if (owner_thread != NULL) {
        k_wakeup(owner_thread);
    }
}

static void accelerometer_open(void *context) {
    (void)context;
    if (!openr1_motion_zephyr_is_enabled()) {
        const int error = openr1_motion_zephyr_initialize();
        if (error != 0 && error != -EALREADY) {
            (void)atomic_inc(&motion_failures);
        }
    }
}

static void accelerometer_close(void *context) {
    (void)context;
    /* Stock close hook 0x0006F300 returns success without changing state. */
}

static uint32_t accelerometer_read(uint8_t *destination, uint32_t length,
                                   void *context) {
    (void)context;
    if (destination == NULL || length != R1_MOTION_BATCH_BYTES) {
        (void)atomic_inc(&motion_failures);
        return 0u;
    }
    r1_motion_sample samples[R1_MOTION_BATCH_SAMPLE_LIMIT];
    size_t sample_count = 0u;
    if (openr1_motion_zephyr_read_fifo(
            samples, R1_MOTION_BATCH_SAMPLE_LIMIT, &sample_count) != 0) {
        (void)atomic_inc(&motion_failures);
        return 0u;
    }
    r1_motion_axis_calibration calibration;
    const r1_motion_axis_calibration *calibration_pointer =
        openr1_databases_zephyr_accelerometer_calibration(&calibration)
            ? &calibration : NULL;
    if (r1_motion_batch_encode(
            samples, sample_count, calibration_pointer,
            false, stream_tick(), destination, length) != R1_OK) {
        (void)atomic_inc(&motion_failures);
        return 0u;
    }
    (void)atomic_inc(&motion_batches);
    return R1_MOTION_BATCH_BYTES;
}

static const sensor_stream_provider_ops accelerometer_provider = {
    accelerometer_open,
    accelerometer_close,
    accelerometer_read,
};

static void temperature_open(void *context) {
    (void)context;
    /* Stock hook 0x000918F8 is a no-op success stub. */
}

static void temperature_close(void *context) {
    (void)context;
    /* Stock hook 0x000918FC is the same no-op success stub. */
}

static uint32_t temperature_read(uint8_t *destination, uint32_t length,
                                 void *context) {
    (void)context;
    if (destination == NULL || length != 2u) {
        (void)atomic_inc(&temperature_failures);
        return 0u;
    }
    uint16_t value = 0u;
    if (openr1_temperature_zephyr_read_stream(&value) != 0) {
        (void)atomic_inc(&temperature_failures);
        return 0u;
    }
    destination[0] = (uint8_t)value;
    destination[1] = (uint8_t)(value >> 8u);
    (void)atomic_inc(&temperature_samples);
    return 2u;
}

static const sensor_stream_provider_ops temperature_provider = {
    temperature_open,
    temperature_close,
    temperature_read,
};

static void temperature_once_publish(
    uint32_t topic, const void *payload, size_t payload_length) {
    if (topic == 9u &&
        openr1_databases_zephyr_consume_temperature_event(
            payload, payload_length) == R1_OK) {
        (void)atomic_inc(&temperature_once_successes);
    } else {
        (void)atomic_inc(&temperature_failures);
    }
}

static void temperature_once_sample(
    sensor_stream_listener *listener, const uint8_t *data, uint32_t length) {
    if (listener == NULL || data == NULL || length != 2u) {
        (void)atomic_inc(&temperature_failures);
        return;
    }
    const uint16_t sample = (uint16_t)(
        (uint16_t)data[0] | (uint16_t)((uint16_t)data[1] << 8u));
    const gomore_primitives_temperature_measurement_result result =
        gomore_primitives_temperature_measurement_step(
            &temperature_once_state, sample);
    if (result == GOMORE_PRIMITIVES_TEMPERATURE_MEASUREMENT_CONTINUE) {
        return;
    }
    if (result == GOMORE_PRIMITIVES_TEMPERATURE_MEASUREMENT_COMPLETE) {
        if (!gomore_primitives_scaled_sample_publish(
                &temperature_once_state, true, temperature_once_publish)) {
            (void)atomic_inc(&temperature_failures);
        }
    } else if (result ==
               GOMORE_PRIMITIVES_TEMPERATURE_MEASUREMENT_TIMEOUT) {
        (void)atomic_inc(&temperature_once_timeouts);
    } else {
        (void)atomic_inc(&temperature_failures);
    }
    openr1_sensor_stream_zephyr_unregister_temperature(listener);
    temperature_once_listener = NULL;
}

static void gomore_accelerometer_stage_sample(
    sensor_stream_listener *listener, const uint8_t *data, uint32_t length) {
    if (listener == NULL ||
            !gomore_primitives_topic_accelerometer_ingest(
                &gomore_topic_input, data, (size_t)length)) {
        (void)atomic_inc(&gomore_accelerometer_stage_failures);
        return;
    }
    (void)atomic_inc(&gomore_accelerometer_stage_batches);
}

int openr1_sensor_stream_zephyr_initialize(void) {
    if (stream_ready) {
        return -EALREADY;
    }
    if (!openr1_motion_zephyr_is_enabled() ||
        !openr1_databases_zephyr_kv_ready()) {
        return -EACCES;
    }
    const sensor_stream_providers providers = {
        .allocate = stream_allocate,
        .free = stream_free,
        .list_first = stream_list_first,
        .list_next = stream_list_next,
        .list_remove = stream_list_remove,
        .list_push_back_allocate = stream_list_push_back_allocate,
        .tick_fallback = stream_tick,
        .diagnostic = stream_diagnostic,
        .fault = stream_fault,
    };
    owner_thread = k_current_get();
    atomic_clear(&motion_batches);
    atomic_clear(&motion_failures);
    atomic_clear(&temperature_samples);
    atomic_clear(&temperature_failures);
    atomic_clear(&temperature_once_successes);
    atomic_clear(&temperature_once_timeouts);
    atomic_clear(&gomore_accelerometer_stage_batches);
    atomic_clear(&gomore_accelerometer_stage_failures);
    atomic_clear(&framework_faults);
    temperature_once_listener = NULL;
    gomore_accelerometer_stage_listener = NULL;
    gomore_topic_input = (gomore_primitives_topic_input_state){0};
    if (sensor_stream_initialize(&stream_framework, &providers) !=
        SENSOR_STREAM_STATUS_OK) {
        owner_thread = NULL;
        return -ENOMEM;
    }
    sensor_stream_set_tick_hook(&stream_framework, stream_tick);
    sensor_stream_set_wake_callback(
        &stream_framework, stream_wake, NULL);
    sensor_stream_bind_singleton_providers(
        &stream_framework, &accelerometer_provider, &temperature_provider);
    accelerometer_object = sensor_stream_acc_object_create(&stream_framework);
    temperature_object = sensor_stream_temp_object_create(&stream_framework);
    if (accelerometer_object == NULL || temperature_object == NULL) {
        owner_thread = NULL;
        return -ENOMEM;
    }
    stream_ready = true;
    return 0;
}

uint32_t openr1_sensor_stream_zephyr_poll(void) {
    if (!stream_ready) {
        return UINT32_MAX;
    }
    const uint32_t ticks = sensor_stream_timer_poll(&stream_framework);
    if (ticks == UINT32_MAX) {
        return UINT32_MAX;
    }
    const uint64_t scaled = (uint64_t)ticks * UINT64_C(1000) +
                            SENSOR_STREAM_TICK_HZ - 1u;
    const uint32_t milliseconds =
        (uint32_t)(scaled / SENSOR_STREAM_TICK_HZ);
    return milliseconds == 0u ? 1u : milliseconds;
}

bool openr1_sensor_stream_zephyr_is_ready(void) {
    return stream_ready;
}

sensor_stream *openr1_sensor_stream_zephyr_framework(void) {
    return stream_ready ? &stream_framework : NULL;
}

sensor_stream_listener *openr1_sensor_stream_zephyr_register_accelerometer(
    const char *listener_name, sensor_stream_listener_callback callback,
    uint8_t mode) {
    if (!stream_ready || listener_name == NULL || callback == NULL ||
        (mode != SENSOR_STREAM_MODE_BATCH &&
         mode != SENSOR_STREAM_MODE_PER_SAMPLE)) {
        return NULL;
    }
    return sensor_stream_listener_register(
        &stream_framework, accelerometer_object, listener_name,
        callback, 1u, mode);
}

void openr1_sensor_stream_zephyr_unregister_accelerometer(
    sensor_stream_listener *listener) {
    if (stream_ready && listener != NULL) {
        sensor_stream_listener_unregister(
            &stream_framework, "acc", listener);
    }
}

sensor_stream_listener *openr1_sensor_stream_zephyr_register_temperature(
    const char *listener_name, sensor_stream_listener_callback callback,
    uint8_t mode) {
    if (!stream_ready || listener_name == NULL || callback == NULL ||
        (mode != SENSOR_STREAM_MODE_BATCH &&
         mode != SENSOR_STREAM_MODE_PER_SAMPLE)) {
        return NULL;
    }
    return sensor_stream_listener_register(
        &stream_framework, temperature_object, listener_name,
        callback, 1u, mode);
}

void openr1_sensor_stream_zephyr_unregister_temperature(
    sensor_stream_listener *listener) {
    if (stream_ready && listener != NULL) {
        sensor_stream_listener_unregister(
            &stream_framework, "temp", listener);
    }
}

int openr1_sensor_stream_zephyr_temperature_once_set(bool enabled) {
    if (!stream_ready) {
        return -EACCES;
    }
    if (!enabled) {
        if (temperature_once_listener != NULL) {
            openr1_sensor_stream_zephyr_unregister_temperature(
                temperature_once_listener);
            temperature_once_listener = NULL;
        }
        return 0;
    }
    if (temperature_once_listener != NULL) {
        return 0;
    }
    if (!gomore_primitives_temperature_measurement_begin(
            &temperature_once_state)) {
        return -EINVAL;
    }
    temperature_once_listener =
        openr1_sensor_stream_zephyr_register_temperature(
            "once", temperature_once_sample,
            SENSOR_STREAM_MODE_PER_SAMPLE);
    return temperature_once_listener != NULL ? 0 : -ENOMEM;
}

bool openr1_sensor_stream_zephyr_temperature_once_active(void) {
    return temperature_once_listener != NULL;
}

uint32_t openr1_sensor_stream_zephyr_temperature_once_successes(void) {
    return (uint32_t)atomic_get(&temperature_once_successes);
}

uint32_t openr1_sensor_stream_zephyr_temperature_once_timeouts(void) {
    return (uint32_t)atomic_get(&temperature_once_timeouts);
}

int openr1_sensor_stream_zephyr_gomore_accelerometer_stage_set(bool enabled) {
    if (!stream_ready) {
        return -EACCES;
    }
    if (!enabled) {
        if (gomore_accelerometer_stage_listener != NULL) {
            openr1_sensor_stream_zephyr_unregister_accelerometer(
                gomore_accelerometer_stage_listener);
            gomore_accelerometer_stage_listener = NULL;
        }
        return 0;
    }
    if (gomore_accelerometer_stage_listener != NULL) {
        return 0;
    }
    gomore_topic_input = (gomore_primitives_topic_input_state){0};
    gomore_accelerometer_stage_listener =
        openr1_sensor_stream_zephyr_register_accelerometer(
            "gomore", gomore_accelerometer_stage_sample,
            SENSOR_STREAM_MODE_BATCH);
    return gomore_accelerometer_stage_listener != NULL ? 0 : -ENOMEM;
}

bool openr1_sensor_stream_zephyr_gomore_accelerometer_stage_active(void) {
    return gomore_accelerometer_stage_listener != NULL;
}

uint32_t openr1_sensor_stream_zephyr_gomore_accelerometer_stage_batches(void) {
    return (uint32_t)atomic_get(&gomore_accelerometer_stage_batches);
}

uint32_t openr1_sensor_stream_zephyr_gomore_accelerometer_stage_failures(void) {
    return (uint32_t)atomic_get(&gomore_accelerometer_stage_failures);
}

uint32_t openr1_sensor_stream_zephyr_motion_batches(void) {
    return (uint32_t)atomic_get(&motion_batches);
}

uint32_t openr1_sensor_stream_zephyr_motion_failures(void) {
    return (uint32_t)atomic_get(&motion_failures) +
           (uint32_t)atomic_get(&framework_faults);
}

uint32_t openr1_sensor_stream_zephyr_temperature_samples(void) {
    return (uint32_t)atomic_get(&temperature_samples);
}

uint32_t openr1_sensor_stream_zephyr_temperature_failures(void) {
    return (uint32_t)atomic_get(&temperature_failures);
}

__attribute__((used, section(".openr1_platform_api")))
static const openr1_sensor_stream_zephyr_api sensor_stream_zephyr_api = {
    openr1_sensor_stream_zephyr_initialize,
    openr1_sensor_stream_zephyr_poll,
    openr1_sensor_stream_zephyr_is_ready,
    openr1_sensor_stream_zephyr_framework,
    openr1_sensor_stream_zephyr_register_accelerometer,
    openr1_sensor_stream_zephyr_unregister_accelerometer,
    openr1_sensor_stream_zephyr_register_temperature,
    openr1_sensor_stream_zephyr_unregister_temperature,
    openr1_sensor_stream_zephyr_temperature_once_set,
    openr1_sensor_stream_zephyr_temperature_once_active,
    openr1_sensor_stream_zephyr_temperature_once_successes,
    openr1_sensor_stream_zephyr_temperature_once_timeouts,
    openr1_sensor_stream_zephyr_gomore_accelerometer_stage_set,
    openr1_sensor_stream_zephyr_gomore_accelerometer_stage_active,
    openr1_sensor_stream_zephyr_gomore_accelerometer_stage_batches,
    openr1_sensor_stream_zephyr_gomore_accelerometer_stage_failures,
    openr1_sensor_stream_zephyr_motion_batches,
    openr1_sensor_stream_zephyr_motion_failures,
    openr1_sensor_stream_zephyr_temperature_samples,
    openr1_sensor_stream_zephyr_temperature_failures,
};
