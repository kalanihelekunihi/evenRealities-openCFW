#include "openr1_sensor_stream_zephyr.h"

#include <errno.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/sys/atomic.h>

#include "generic_device_registry/generic_device_registry.h"
#include "gomore_primitives/gomore_primitives.h"
#include "openr1/r1_goodix.h"
#include "openr1_databases_zephyr.h"
#include "openr1_motion_zephyr.h"
#include "openr1_optical_zephyr.h"
#include "openr1_temperature_zephyr.h"

#define OPENR1_GOODIX_TOPIC_STATE_BYTES 240u
#define OPENR1_GOODIX_HR_OFFSET 0u
#define OPENR1_GOODIX_HRV_OFFSET 16u
#define OPENR1_GOODIX_RAW_HR_OFFSET 64u
#define OPENR1_GOODIX_HR_RECORD_BYTES 4u
#define OPENR1_GOODIX_HRV_RECORD_BYTES 10u

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
    int (*gomore_health_stage_set)(bool);
    void (*health_policy_request)(bool);
    int (*gomore_authorization_set)(uint32_t, bool);
    bool (*gomore_health_stage_active)(void);
    int (*gomore_consume_ready)(openr1_gomore_topic_consume_fn, void *);
    bool (*goodix_raw_hr_append)(uint32_t);
    bool (*goodix_heart_rate_update)(const int32_t[4]);
    bool (*goodix_hrv_update)(const int32_t[6]);
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
static sensor_stream_object *goodix_heart_rate_object;
static sensor_stream_object *goodix_hrv_object;
static sensor_stream_object *goodix_raw_hr_object;
static k_tid_t owner_thread;
K_MUTEX_DEFINE(goodix_topic_mutex);
K_MUTEX_DEFINE(gomore_topic_mutex);
static atomic_t motion_batches;
static atomic_t motion_failures;
static atomic_t temperature_samples;
static atomic_t temperature_failures;
static atomic_t temperature_once_successes;
static atomic_t temperature_once_timeouts;
static atomic_t gomore_accelerometer_stage_batches;
static atomic_t gomore_accelerometer_stage_failures;
static atomic_t framework_faults;
static atomic_t gomore_health_requested;
static gomore_primitives_scaled_sample_state temperature_once_state;
static sensor_stream_listener *temperature_once_listener;
static gomore_primitives_topic_input_state gomore_topic_input;
static gomore_primitives_authorization_state gomore_authorization;
static sensor_stream_listener *gomore_accelerometer_stage_listener;
static sensor_stream_listener *gomore_raw_hr_stage_listener;
static sensor_stream_listener *gomore_heart_rate_stage_listener;
static sensor_stream_listener *gomore_hrv_stage_listener;
static uint8_t goodix_topic_state[OPENR1_GOODIX_TOPIC_STATE_BYTES];
static bool stream_ready;

typedef struct {
    uint8_t mode;
    uint32_t function_mask;
} goodix_stream_context;

static const goodix_stream_context goodix_heart_rate_context = {
    .mode = 1u,
    .function_mask = R1_GOODIX_MASK_SWITCH_2,
};
static const goodix_stream_context goodix_hrv_context = {
    .mode = 4u,
    .function_mask = R1_GOODIX_MASK_HRV,
};
static const goodix_stream_context goodix_raw_hr_context = {
    .mode = 5u,
    .function_mask = R1_GOODIX_MASK_HSM,
};

static uint32_t topic_load_u32(const uint8_t *bytes) {
    return (uint32_t)bytes[0] | ((uint32_t)bytes[1] << 8u) |
        ((uint32_t)bytes[2] << 16u) | ((uint32_t)bytes[3] << 24u);
}

static void topic_store_u32(uint8_t *bytes, uint32_t value) {
    bytes[0] = (uint8_t)value;
    bytes[1] = (uint8_t)(value >> 8u);
    bytes[2] = (uint8_t)(value >> 16u);
    bytes[3] = (uint8_t)(value >> 24u);
}

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

static void goodix_stream_open(void *context) {
    const goodix_stream_context *stream = context;
    if (stream == NULL ||
        openr1_optical_zephyr_start_functions(stream->function_mask) != 0) {
        (void)atomic_inc(&framework_faults);
    }
}

static void goodix_stream_close(void *context) {
    const goodix_stream_context *stream = context;
    if (stream == NULL ||
        openr1_optical_zephyr_stop_functions(stream->function_mask) != 0) {
        (void)atomic_inc(&framework_faults);
    }
}

static uint32_t goodix_stream_read(uint8_t *destination, uint32_t length,
                                   void *context) {
    const goodix_stream_context *stream = context;
    if (destination == NULL || stream == NULL ||
        k_mutex_lock(&goodix_topic_mutex, K_FOREVER) != 0) {
        (void)atomic_inc(&framework_faults);
        return 0u;
    }
    uint32_t written = 0u;
    if (stream->mode == 1u && length == OPENR1_GOODIX_HR_RECORD_BYTES) {
        const uint32_t heart_rate = topic_load_u32(
            &goodix_topic_state[OPENR1_GOODIX_HR_OFFSET]);
        if (heart_rate >= 41u && heart_rate <= 219u) {
            for (size_t index = 0u; index < 4u; ++index) {
                destination[index] = (uint8_t)topic_load_u32(
                    &goodix_topic_state[OPENR1_GOODIX_HR_OFFSET +
                                        index * 4u]);
            }
            written = OPENR1_GOODIX_HR_RECORD_BYTES;
        }
    } else if (stream->mode == 4u &&
               length == OPENR1_GOODIX_HRV_RECORD_BYTES) {
        if (topic_load_u32(
                &goodix_topic_state[OPENR1_GOODIX_HRV_OFFSET]) != 0u) {
            for (size_t index = 0u; index < 4u; ++index) {
                const uint32_t value = topic_load_u32(
                    &goodix_topic_state[OPENR1_GOODIX_HRV_OFFSET +
                                        index * 4u]);
                destination[index * 2u] = (uint8_t)value;
                destination[index * 2u + 1u] = (uint8_t)(value >> 8u);
            }
            destination[8] = (uint8_t)topic_load_u32(
                &goodix_topic_state[OPENR1_GOODIX_HRV_OFFSET + 16u]);
            destination[9] = (uint8_t)topic_load_u32(
                &goodix_topic_state[OPENR1_GOODIX_HRV_OFFSET + 20u]);
            written = OPENR1_GOODIX_HRV_RECORD_BYTES;
        }
    } else if (stream->mode == 5u &&
               length == R1_GOODIX_RAW_HR_RECORD_BYTES) {
        memcpy(destination,
               &goodix_topic_state[OPENR1_GOODIX_RAW_HR_OFFSET], length);
        /* The recovered source record is periodically cleared by the common
         * diagnostic refresh. A successful one-Hz delivery is the local
         * ownership boundary, so clear it here to retain each HSM value once
         * while preserving the exact count/reserved/value wire record. */
        memset(&goodix_topic_state[OPENR1_GOODIX_RAW_HR_OFFSET], 0, length);
        written = length;
    }
    (void)k_mutex_unlock(&goodix_topic_mutex);
    return written;
}

static const sensor_stream_provider_ops goodix_stream_provider = {
    goodix_stream_open,
    goodix_stream_close,
    goodix_stream_read,
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
    bool accepted = false;
    if (listener != NULL) {
        (void)k_mutex_lock(&gomore_topic_mutex, K_FOREVER);
        accepted = gomore_primitives_topic_accelerometer_ingest(
            &gomore_topic_input, data, (size_t)length);
        (void)k_mutex_unlock(&gomore_topic_mutex);
    }
    if (!accepted) {
        (void)atomic_inc(&gomore_accelerometer_stage_failures);
        return;
    }
    (void)atomic_inc(&gomore_accelerometer_stage_batches);
}

static void gomore_raw_hr_stage_sample(
    sensor_stream_listener *listener, const uint8_t *data, uint32_t length) {
    bool accepted = false;
    if (listener != NULL) {
        (void)k_mutex_lock(&gomore_topic_mutex, K_FOREVER);
        accepted = gomore_primitives_topic_raw_optical_ingest(
            &gomore_topic_input, data, (size_t)length);
        (void)k_mutex_unlock(&gomore_topic_mutex);
    }
    if (!accepted) {
        (void)atomic_inc(&gomore_accelerometer_stage_failures);
    }
}

static void gomore_heart_rate_stage_sample(
    sensor_stream_listener *listener, const uint8_t *data, uint32_t length) {
    bool accepted = false;
    if (listener != NULL) {
        (void)k_mutex_lock(&gomore_topic_mutex, K_FOREVER);
        accepted = gomore_primitives_topic_heart_rate_ingest(
            &gomore_topic_input, data, (size_t)length);
        (void)k_mutex_unlock(&gomore_topic_mutex);
    }
    if (!accepted) {
        (void)atomic_inc(&gomore_accelerometer_stage_failures);
    }
}

static void gomore_hrv_stage_sample(
    sensor_stream_listener *listener, const uint8_t *data, uint32_t length) {
    bool accepted = false;
    if (listener != NULL) {
        (void)k_mutex_lock(&gomore_topic_mutex, K_FOREVER);
        accepted = gomore_primitives_topic_hrv_ingest(
            &gomore_topic_input, data, (size_t)length);
        (void)k_mutex_unlock(&gomore_topic_mutex);
    }
    if (!accepted) {
        (void)atomic_inc(&gomore_accelerometer_stage_failures);
    }
}

static uintptr_t gomore_authorization_register_stream(
    void *context, uint8_t stream_index) {
    (void)context;
    sensor_stream_listener **handle = NULL;
    sensor_stream_object *object = NULL;
    sensor_stream_listener_callback callback = NULL;
    if (stream_index == 0u) {
        handle = &gomore_accelerometer_stage_listener;
        object = accelerometer_object;
        callback = gomore_accelerometer_stage_sample;
    } else if (stream_index == 1u) {
        handle = &gomore_raw_hr_stage_listener;
        object = goodix_raw_hr_object;
        callback = gomore_raw_hr_stage_sample;
    } else if (stream_index == 2u) {
        handle = &gomore_heart_rate_stage_listener;
        object = goodix_heart_rate_object;
        callback = gomore_heart_rate_stage_sample;
    } else if (stream_index == 3u) {
        handle = &gomore_hrv_stage_listener;
        object = goodix_hrv_object;
        callback = gomore_hrv_stage_sample;
    }
    if (handle == NULL || object == NULL || callback == NULL) {
        return (uintptr_t)0;
    }
    if (*handle == NULL) {
        *handle = sensor_stream_listener_register(
            &stream_framework, object, "gomore", callback, 1u,
            SENSOR_STREAM_MODE_BATCH);
    }
    return (uintptr_t)*handle;
}

static void gomore_authorization_unregister_stream(
    void *context, uint8_t stream_index, uintptr_t opaque_handle) {
    (void)context;
    sensor_stream_listener *const handle =
        (sensor_stream_listener *)opaque_handle;
    if (handle == NULL) {
        return;
    }
    if (stream_index == 0u &&
        handle == gomore_accelerometer_stage_listener) {
        openr1_sensor_stream_zephyr_unregister_accelerometer(handle);
        gomore_accelerometer_stage_listener = NULL;
    } else if (stream_index == 1u &&
               handle == gomore_raw_hr_stage_listener) {
        sensor_stream_listener_unregister(
            &stream_framework, "raw_hr", handle);
        gomore_raw_hr_stage_listener = NULL;
    } else if (stream_index == 2u &&
               handle == gomore_heart_rate_stage_listener) {
        sensor_stream_listener_unregister(&stream_framework, "hr", handle);
        gomore_heart_rate_stage_listener = NULL;
    } else if (stream_index == 3u &&
               handle == gomore_hrv_stage_listener) {
        sensor_stream_listener_unregister(&stream_framework, "hrv", handle);
        gomore_hrv_stage_listener = NULL;
    }
}

static uintptr_t gomore_authorization_create_timer(
    void *context, uint32_t period_milliseconds) {
    (void)context;
    /* sensor_stream_initialize already owns the recovered common keepalive;
     * this stable handle represents it in the authorization state. */
    return period_milliseconds == UINT32_C(1000)
        ? (uintptr_t)1 : (uintptr_t)0;
}

static void gomore_authorization_delete_timer(
    void *context, uintptr_t handle) {
    (void)context;
    (void)handle;
}

static const gomore_primitives_authorization_providers
    gomore_authorization_providers = {
        .context = NULL,
        .register_stream = gomore_authorization_register_stream,
        .unregister_stream = gomore_authorization_unregister_stream,
        .create_timer = gomore_authorization_create_timer,
        .delete_timer = gomore_authorization_delete_timer,
    };

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
    atomic_clear(&gomore_health_requested);
    temperature_once_listener = NULL;
    gomore_accelerometer_stage_listener = NULL;
    gomore_raw_hr_stage_listener = NULL;
    gomore_heart_rate_stage_listener = NULL;
    gomore_hrv_stage_listener = NULL;
    (void)k_mutex_lock(&gomore_topic_mutex, K_FOREVER);
    gomore_topic_input = (gomore_primitives_topic_input_state){0};
    (void)k_mutex_unlock(&gomore_topic_mutex);
    gomore_authorization = (gomore_primitives_authorization_state){0};
    gomore_authorization.initialized = true;
    gomore_authorization.idle_timer_handle = (uintptr_t)1;
    /* Exact seven 16-byte descriptor dependency masks at stock 0x49410.
     * Bit zero is the active flag; bits 1..4 select acc/raw_hr/hr/hrv. */
    static const uint8_t dependency_masks[GOMORE_PRIMITIVES_RECORD_COUNT] = {
        UINT8_C(0x02), UINT8_C(0x1e), UINT8_C(0x1e), UINT8_C(0x02),
        UINT8_C(0x04), UINT8_C(0x0c), UINT8_C(0x00),
    };
    for (size_t slot = 0u; slot < GOMORE_PRIMITIVES_RECORD_COUNT; ++slot) {
        gomore_authorization.slots[slot].flags = dependency_masks[slot];
    }
    memset(goodix_topic_state, 0, sizeof(goodix_topic_state));
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
    goodix_heart_rate_object = sensor_stream_object_create(
        &stream_framework, "hr", OPENR1_GOODIX_HR_RECORD_BYTES,
        &goodix_stream_provider, (void *)&goodix_heart_rate_context);
    goodix_hrv_object = sensor_stream_object_create(
        &stream_framework, "hrv", OPENR1_GOODIX_HRV_RECORD_BYTES,
        &goodix_stream_provider, (void *)&goodix_hrv_context);
    goodix_raw_hr_object = sensor_stream_object_create(
        &stream_framework, "raw_hr", R1_GOODIX_RAW_HR_RECORD_BYTES,
        &goodix_stream_provider, (void *)&goodix_raw_hr_context);
    if (accelerometer_object == NULL || temperature_object == NULL ||
        goodix_heart_rate_object == NULL || goodix_hrv_object == NULL ||
        goodix_raw_hr_object == NULL) {
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
    const bool requested = atomic_get(&gomore_health_requested) != 0;
    if (requested !=
            openr1_sensor_stream_zephyr_gomore_health_stage_active() &&
        openr1_sensor_stream_zephyr_gomore_health_stage_set(requested) != 0) {
        (void)atomic_inc(&framework_faults);
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

bool openr1_sensor_stream_zephyr_goodix_raw_hr_append(uint32_t value) {
    if (!stream_ready ||
        k_mutex_lock(&goodix_topic_mutex, K_FOREVER) != 0) {
        return false;
    }
    const bool appended = r1_goodix_raw_hr_append(
        &goodix_topic_state[OPENR1_GOODIX_RAW_HR_OFFSET], value);
    (void)k_mutex_unlock(&goodix_topic_mutex);
    return appended;
}

bool openr1_sensor_stream_zephyr_goodix_heart_rate_update(
    const int32_t values[4]) {
    if (!stream_ready || values == NULL ||
        k_mutex_lock(&goodix_topic_mutex, K_FOREVER) != 0) {
        return false;
    }
    for (size_t index = 0u; index < 4u; ++index) {
        topic_store_u32(
            &goodix_topic_state[OPENR1_GOODIX_HR_OFFSET + index * 4u],
            (uint32_t)values[index]);
    }
    (void)k_mutex_unlock(&goodix_topic_mutex);
    return true;
}

bool openr1_sensor_stream_zephyr_goodix_hrv_update(
    const int32_t values[6]) {
    if (!stream_ready || values == NULL ||
        k_mutex_lock(&goodix_topic_mutex, K_FOREVER) != 0) {
        return false;
    }
    for (size_t index = 0u; index < 6u; ++index) {
        topic_store_u32(
            &goodix_topic_state[OPENR1_GOODIX_HRV_OFFSET + index * 4u],
            (uint32_t)values[index]);
    }
    (void)k_mutex_unlock(&goodix_topic_mutex);
    return true;
}

uint32_t openr1_sensor_stream_zephyr_temperature_once_successes(void) {
    return (uint32_t)atomic_get(&temperature_once_successes);
}

uint32_t openr1_sensor_stream_zephyr_temperature_once_timeouts(void) {
    return (uint32_t)atomic_get(&temperature_once_timeouts);
}

int openr1_sensor_stream_zephyr_gomore_accelerometer_stage_set(bool enabled) {
    return openr1_sensor_stream_zephyr_gomore_health_stage_set(enabled);
}

int openr1_sensor_stream_zephyr_gomore_health_stage_set(bool enabled) {
    if (!stream_ready) {
        return -EACCES;
    }
    const uint8_t active = UINT8_C(0x01);
    if (enabled) {
        (void)k_mutex_lock(&gomore_topic_mutex, K_FOREVER);
        gomore_topic_input = (gomore_primitives_topic_input_state){0};
        (void)k_mutex_unlock(&gomore_topic_mutex);
    }
    const uint32_t slots[2] = {0u, 3u};
    int status = 0;
    for (size_t index = 0u; index < 2u; ++index) {
        const uint32_t slot = slots[index];
        const bool active_now =
            (gomore_authorization.slots[slot].flags & active) != 0u;
        if (active_now == enabled) {
            continue;
        }
        if (!gomore_primitives_authorization_dispatch(
                &gomore_authorization, slot, enabled,
                &gomore_authorization_providers)) {
            status = -EIO;
            break;
        }
    }
    if (enabled && gomore_authorization.stream_handles[0] == (uintptr_t)0) {
        status = -ENOMEM;
    }
    if (status != 0 && enabled) {
        for (size_t index = 0u; index < 2u; ++index) {
            const uint32_t slot = slots[index];
            if ((gomore_authorization.slots[slot].flags & active) != 0u) {
                (void)gomore_primitives_authorization_dispatch(
                    &gomore_authorization, slot, false,
                    &gomore_authorization_providers);
            }
        }
    }
    return status;
}

void openr1_sensor_stream_zephyr_health_policy_request(bool enabled) {
    atomic_set(&gomore_health_requested, enabled ? 1 : 0);
    stream_wake(NULL);
}

int openr1_sensor_stream_zephyr_gomore_authorization_set(
    uint32_t slot, bool enabled) {
    if (!stream_ready || slot >= GOMORE_PRIMITIVES_RECORD_COUNT) {
        return -EINVAL;
    }
    const bool active =
        (gomore_authorization.slots[slot].flags & UINT8_C(0x01)) != 0u;
    if (active == enabled) {
        return 0;
    }
    if (!gomore_primitives_authorization_dispatch(
            &gomore_authorization, slot, enabled,
            &gomore_authorization_providers)) {
        return -EIO;
    }
    if (enabled) {
        const uint8_t requirements =
            gomore_authorization.slots[slot].flags & UINT8_C(0x1e);
        for (uint8_t stream = 0u; stream < 4u; ++stream) {
            const uint8_t mask =
                (uint8_t)(UINT8_C(1) << (uint8_t)(stream + 1u));
            if ((requirements & mask) != 0u &&
                gomore_authorization.stream_handles[stream] ==
                    (uintptr_t)0) {
                (void)gomore_primitives_authorization_dispatch(
                    &gomore_authorization, slot, false,
                    &gomore_authorization_providers);
                return -ENOMEM;
            }
        }
    }
    return 0;
}

uint8_t openr1_sensor_stream_zephyr_gomore_active_slot_mask(void) {
    uint8_t mask = 0u;
    if (!stream_ready) {
        return mask;
    }
    for (uint8_t slot = 0u; slot < GOMORE_PRIMITIVES_RECORD_COUNT; ++slot) {
        if ((gomore_authorization.slots[slot].flags & UINT8_C(0x01)) != 0u) {
            mask |= (uint8_t)(UINT8_C(1) << slot);
        }
    }
    return mask;
}

bool openr1_sensor_stream_zephyr_gomore_health_stage_active(void) {
    return (gomore_authorization.slots[0].flags & UINT8_C(0x01)) != 0u &&
        (gomore_authorization.slots[3].flags & UINT8_C(0x01)) != 0u;
}

int openr1_sensor_stream_zephyr_gomore_consume_ready(
    openr1_gomore_topic_consume_fn consume, void *context) {
    if (!stream_ready || consume == NULL) {
        return -EINVAL;
    }
    const bool accelerometer_required =
        gomore_authorization.stream_handles[0] != (uintptr_t)0;
    const bool raw_optical_required =
        gomore_authorization.stream_handles[1] != (uintptr_t)0;

    (void)k_mutex_lock(&gomore_topic_mutex, K_FOREVER);
    if (!gomore_primitives_topic_update_take_ready(
            &gomore_topic_input, accelerometer_required,
            raw_optical_required)) {
        (void)k_mutex_unlock(&gomore_topic_mutex);
        return 0;
    }
    const gomore_primitives_topic_input_state snapshot = gomore_topic_input;
    const bool succeeded = consume(context, &snapshot);
    gomore_primitives_topic_update_complete(&gomore_topic_input, succeeded);
    (void)k_mutex_unlock(&gomore_topic_mutex);
    return succeeded ? 1 : -EIO;
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
    openr1_sensor_stream_zephyr_gomore_health_stage_set,
    openr1_sensor_stream_zephyr_health_policy_request,
    openr1_sensor_stream_zephyr_gomore_authorization_set,
    openr1_sensor_stream_zephyr_gomore_health_stage_active,
    openr1_sensor_stream_zephyr_gomore_consume_ready,
    openr1_sensor_stream_zephyr_goodix_raw_hr_append,
    openr1_sensor_stream_zephyr_goodix_heart_rate_update,
    openr1_sensor_stream_zephyr_goodix_hrv_update,
    openr1_sensor_stream_zephyr_gomore_accelerometer_stage_active,
    openr1_sensor_stream_zephyr_gomore_accelerometer_stage_batches,
    openr1_sensor_stream_zephyr_gomore_accelerometer_stage_failures,
    openr1_sensor_stream_zephyr_motion_batches,
    openr1_sensor_stream_zephyr_motion_failures,
    openr1_sensor_stream_zephyr_temperature_samples,
    openr1_sensor_stream_zephyr_temperature_failures,
};
