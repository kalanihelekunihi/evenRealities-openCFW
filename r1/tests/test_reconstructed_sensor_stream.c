/*
 * Host tests for the reconstructed sensor-stream framework (family
 * unknown_sensor_stream_framework_candidate, owner-authorized reduction; see
 * docs/correlation/SENSOR-STREAM-REDUCTION-CORRELATION.md).  Expected values
 * are derived from the recovered decompilation semantics; the registry-family
 * list walkers and the FreeRTOS heap are realized as explicit test oracles
 * bound through the provider interface.
 */

#include <assert.h>
#include <stdint.h>
#include <stdio.h>

#include "sensor_stream/sensor_stream.h"

/* -------------------------------------------------------------------------
 * Test allocator oracle (bounded pool, optional failure injection).
 * ------------------------------------------------------------------------- */

static uint64_t test_pool[16384 / 8]; /* 8-aligned like the target heap */
static size_t test_pool_used;
static size_t test_allocate_calls;
static size_t test_free_calls;
static size_t test_live_blocks;
static long test_fail_after;   /* -1 = never */

static void test_allocator_reset(void) {
    test_pool_used = 0u;
    test_allocate_calls = 0u;
    test_free_calls = 0u;
    test_live_blocks = 0u;
    test_fail_after = -1;
    uint8_t *bytes = (uint8_t *)test_pool;
    for (size_t index = 0u; index < sizeof(test_pool); ++index) {
        bytes[index] = 0u;
    }
}

static void *test_allocate(uint32_t size) {
    ++test_allocate_calls;
    if (test_fail_after >= 0 &&
            (long)(test_allocate_calls - 1u) >= test_fail_after) {
        return NULL;
    }
    if (size == 0u || test_pool_used + size > sizeof(test_pool)) {
        return NULL;
    }
    void *block = (void *)((uint8_t *)test_pool + test_pool_used);
    test_pool_used += (size + 7u) & ~7u;
    ++test_live_blocks;
    return block;
}

static void test_free(void *pointer) {
    assert(pointer != NULL);
    ++test_free_calls;
    assert(test_live_blocks > 0u);
    --test_live_blocks;
    if (test_live_blocks == 0u) {
        test_pool_used = 0u; /* bounded-pool reuse once fully drained */
    }
}

/* -------------------------------------------------------------------------
 * Registry-family list walker oracles (0x0005D8E6/0x0005D8EE/0x0005D998/
 * 0x0005D94A recovered semantics; the family itself is not reconstructed
 * here).
 * ------------------------------------------------------------------------- */

static void *test_list_first(sensor_stream_list_descriptor *descriptor) {
    return descriptor->head;
}

static void *test_list_next(sensor_stream_list_descriptor *descriptor,
                            void *node) {
    return *(void **)(void *)((uint8_t *)node + descriptor->stride +
                              sizeof(void *));
}

static void test_list_remove(sensor_stream_list_descriptor *descriptor,
                             void *node) {
    uint8_t *entry = (uint8_t *)node;
    void *previous =
        *(void **)(void *)(entry + descriptor->stride);
    void *next =
        *(void **)(void *)(entry + descriptor->stride + sizeof(void *));
    if (previous != NULL) {
        *(void **)(void *)((uint8_t *)previous + descriptor->stride +
                           sizeof(void *)) = next;
    } else {
        descriptor->head = next;
    }
    if (next != NULL) {
        *(void **)(void *)((uint8_t *)next + descriptor->stride) = previous;
    } else {
        descriptor->tail = previous;
    }
}

static void *test_list_push_back_allocate(
    sensor_stream_list_descriptor *descriptor) {
    uint8_t *node = (uint8_t *)test_allocate(
        descriptor->stride + 2u * (uint32_t)sizeof(void *));
    if (node == NULL) {
        return NULL;
    }
    *(void **)(void *)(node + descriptor->stride + sizeof(void *)) = NULL;
    *(void **)(void *)(node + descriptor->stride) = descriptor->tail;
    if (descriptor->tail != NULL) {
        *(void **)(void *)((uint8_t *)descriptor->tail + descriptor->stride +
                           sizeof(void *)) = node;
    }
    descriptor->tail = node;
    if (descriptor->head == NULL) {
        descriptor->head = node;
    }
    return node;
}

/* -------------------------------------------------------------------------
 * Tick, diagnostic, fault, wake, provider oracles.
 * ------------------------------------------------------------------------- */

static uint32_t test_tick;
static uint32_t test_hook_tick;
static uint32_t test_hook_step;

static uint32_t test_tick_fallback(void) {
    return test_tick;
}

static uint32_t test_tick_hook(void) {
    uint32_t value = test_hook_tick;
    test_hook_tick += test_hook_step;
    return value;
}

static char test_diagnostic_last[64];
static size_t test_diagnostic_calls;
static char test_diagnostic_detail[16];

static void test_diagnostic(const char *message, const char *detail,
                            uint32_t value) {
    size_t index = 0u;
    ++test_diagnostic_calls;
    (void)value;
    while (message[index] != '\0' && index + 1u < sizeof(test_diagnostic_last)) {
        test_diagnostic_last[index] = message[index];
        ++index;
    }
    test_diagnostic_last[index] = '\0';
    index = 0u;
    test_diagnostic_detail[0] = '\0';
    if (detail != NULL) {
        while (detail[index] != '\0' &&
                index + 1u < sizeof(test_diagnostic_detail)) {
            test_diagnostic_detail[index] = detail[index];
            ++index;
        }
        test_diagnostic_detail[index] = '\0';
    }
}

static bool test_diagnostic_seen(const char *message) {
    size_t index = 0u;
    while (message[index] != '\0' || test_diagnostic_last[index] != '\0') {
        if (message[index] != test_diagnostic_last[index]) {
            return false;
        }
        ++index;
    }
    return true;
}

static size_t test_fault_calls;

static void test_fault(void) {
    ++test_fault_calls;
}

static size_t test_wake_calls;
static void *test_wake_context_seen;
static int test_wake_context_value;

static void test_wake(void *context) {
    ++test_wake_calls;
    test_wake_context_seen = context;
}

static size_t test_open_calls;
static size_t test_close_calls;
static void *test_hook_context_seen;
static uint8_t test_read_fill;
static uint32_t test_read_result; /* 0 = report sample_size */
static size_t test_read_calls;

static void test_provider_open(void *context) {
    ++test_open_calls;
    test_hook_context_seen = context;
}

static void test_provider_close(void *context) {
    ++test_close_calls;
    test_hook_context_seen = context;
}

static uint32_t test_provider_read(uint8_t *destination, uint32_t length,
                                   void *context) {
    (void)context;
    ++test_read_calls;
    for (uint32_t index = 0u; index < length; ++index) {
        destination[index] = test_read_fill;
    }
    return test_read_result != 0u ? test_read_result : length;
}

static const sensor_stream_provider_ops test_provider = {
    test_provider_open, test_provider_close, test_provider_read
};

/* Listener callback oracle. */
static size_t test_listener_calls;
static sensor_stream_listener *test_listener_seen;
static uint32_t test_listener_length_seen;
static uint8_t test_listener_data_first;
static const uint8_t *test_listener_data_seen;

static void test_listener_callback(sensor_stream_listener *listener,
                                   const uint8_t *data, uint32_t length) {
    ++test_listener_calls;
    test_listener_seen = listener;
    test_listener_data_seen = data;
    test_listener_length_seen = length;
    test_listener_data_first = length != 0u ? data[0] : 0u;
}

/* Timer callback oracle. */
static size_t test_timer_callback_calls;
static sensor_stream_timer *test_timer_callback_node;

static void test_timer_callback(sensor_stream *framework,
                                sensor_stream_timer *timer) {
    (void)framework;
    ++test_timer_callback_calls;
    test_timer_callback_node = timer;
}

static sensor_stream_providers test_providers(void) {
    sensor_stream_providers providers;
    providers.allocate = test_allocate;
    providers.free = test_free;
    providers.list_first = test_list_first;
    providers.list_next = test_list_next;
    providers.list_remove = test_list_remove;
    providers.list_push_back_allocate = test_list_push_back_allocate;
    providers.tick_fallback = test_tick_fallback;
    providers.diagnostic = test_diagnostic;
    providers.fault = test_fault;
    return providers;
}

static void test_reset(sensor_stream *framework) {
    sensor_stream_providers providers = test_providers();
    test_allocator_reset();
    test_tick = 0u;
    test_hook_tick = 0u;
    test_hook_step = 0u;
    test_diagnostic_last[0] = '\0';
    test_diagnostic_detail[0] = '\0';
    test_diagnostic_calls = 0u;
    test_fault_calls = 0u;
    test_wake_calls = 0u;
    test_wake_context_seen = NULL;
    test_open_calls = 0u;
    test_close_calls = 0u;
    test_hook_context_seen = NULL;
    test_read_fill = 0u;
    test_read_result = 0u;
    test_read_calls = 0u;
    test_listener_calls = 0u;
    test_listener_seen = NULL;
    test_timer_callback_calls = 0u;
    assert(sensor_stream_initialize(framework, &providers) ==
           SENSOR_STREAM_STATUS_OK);
    /* Drop the keep-alive timer so each test starts from an empty list. */
    sensor_stream_timer_release(framework,
                                (sensor_stream_timer *)
                                framework->housekeeping.timers.head);
    test_diagnostic_calls = 0u;
    test_diagnostic_last[0] = '\0';
}

/* ------------------------------------------------------------------------- */

static void test_sensor_stream_list_primitives(void) {
    sensor_stream framework;
    test_reset(&framework);

    sensor_stream_list_descriptor descriptor;
    sensor_stream_list_descriptor_init(&descriptor, 5u);
    assert(descriptor.stride == 8u); /* align4 */
    assert(descriptor.head == NULL && descriptor.tail == NULL);
    sensor_stream_list_descriptor_init(NULL, 5u); /* no-op */
    sensor_stream_list_descriptor_init(&descriptor, 0x18u);
    assert(descriptor.stride == 0x18u);

    assert(sensor_stream_list_idle(NULL)); /* recovered: NULL -> idle */
    assert(sensor_stream_list_idle(&descriptor));
    descriptor.head = (void *)1;
    assert(!sensor_stream_list_idle(&descriptor));
    descriptor.head = NULL;
    descriptor.tail = (void *)1;
    assert(!sensor_stream_list_idle(&descriptor));
    descriptor.tail = NULL;

    void *first =
        sensor_stream_list_push_front_allocate(&framework, &descriptor);
    assert(first != NULL);
    assert(descriptor.head == first && descriptor.tail == first);
    assert(test_list_next(&descriptor, first) == NULL);
    void *second =
        sensor_stream_list_push_front_allocate(&framework, &descriptor);
    assert(second != NULL);
    assert(descriptor.head == second);
    assert(descriptor.tail == first);
    assert(test_list_next(&descriptor, second) == first);
    assert(test_list_next(&descriptor, first) == NULL);

    /* Allocation failure returns NULL without touching the list. */
    test_fail_after = (long)test_allocate_calls;
    assert(sensor_stream_list_push_front_allocate(&framework, &descriptor) ==
           NULL);
    assert(descriptor.head == second);
    test_fail_after = -1;

    /* Unbound allocator fails explicitly. */
    sensor_stream bare;
    assert(sensor_stream_initialize(&bare, NULL) ==
           SENSOR_STREAM_STATUS_BAD_ARGUMENT);
    assert(sensor_stream_list_push_front_allocate(&bare, &descriptor) == NULL);
    assert(sensor_stream_list_push_front_allocate(NULL, &descriptor) == NULL);
    assert(sensor_stream_list_push_front_allocate(&framework, NULL) == NULL);
}

static void test_sensor_stream_resample_copy(void) {
    uint8_t source[8];
    uint8_t destination[8];
    for (uint8_t index = 0u; index < 8u; ++index) {
        source[index] = (uint8_t)(10u + index);
        destination[index] = 0u;
    }
    /* Identity: 4 one-byte samples -> 4, valid = 4 bytes. */
    assert(sensor_stream_resample_copy(source, 4u, 4u, destination, 4u, 1u) ==
           4u);
    for (uint8_t index = 0u; index < 4u; ++index) {
        assert(destination[index] == (uint8_t)(10u + index));
    }
    /* Downsample 4 -> 2: produced = (4*2 + 2)/4 = 2; indices 0, 2. */
    assert(sensor_stream_resample_copy(source, 4u, 4u, destination, 2u, 1u) ==
           2u);
    assert(destination[0] == 10u && destination[1] == 12u);
    /* Upsample 2 -> 4: produced = (2*4 + 1)/2 = 4; indices 0, 0, 1, 1. */
    assert(sensor_stream_resample_copy(source, 2u, 2u, destination, 4u, 1u) ==
           4u);
    assert(destination[0] == 10u && destination[1] == 10u);
    assert(destination[2] == 11u && destination[3] == 11u);
    /* Valid shorter than source: valid = 1 sample, target 4 -> produced
     * (1*4 + 1)/2 = 2, source index clamped to 0. */
    assert(sensor_stream_resample_copy(source, 2u, 1u, destination, 4u, 1u) ==
           2u);
    assert(destination[0] == 10u && destination[1] == 10u);
    /* Element size 2. */
    assert(sensor_stream_resample_copy(source, 2u, 4u, destination, 2u, 2u) ==
           4u);
    assert(destination[0] == 10u && destination[1] == 11u);
    assert(destination[2] == 12u && destination[3] == 13u);
    /* Malformed: every zero/NULL argument returns 0. */
    assert(sensor_stream_resample_copy(NULL, 4u, 4u, destination, 4u, 1u) == 0u);
    assert(sensor_stream_resample_copy(source, 4u, 4u, NULL, 4u, 1u) == 0u);
    assert(sensor_stream_resample_copy(source, 0u, 4u, destination, 4u, 1u) == 0u);
    assert(sensor_stream_resample_copy(source, 4u, 0u, destination, 4u, 1u) == 0u);
    assert(sensor_stream_resample_copy(source, 4u, 4u, destination, 0u, 1u) == 0u);
    assert(sensor_stream_resample_copy(source, 4u, 4u, destination, 4u, 0u) == 0u);
    /* Rounded-to-zero production returns 0 (valid 1, target 1, source 4:
     * produced = (1*1 + 2)/4 = 0). */
    assert(sensor_stream_resample_copy(source, 4u, 1u, destination, 1u, 1u) == 0u);
}

static void test_sensor_stream_object_lifecycle(void) {
    sensor_stream framework;
    test_reset(&framework);
    int context_value = 7;

    sensor_stream_object *object = sensor_stream_object_create(
        &framework, "hr", 4u, &test_provider, &context_value);
    assert(object != NULL);
    assert(object->name[0] == 'h' && object->name[1] == 'r' &&
           object->name[2] == '\0');
    assert(object->provider == &test_provider);
    assert(object->sample_size == 4u);
    assert(object->context == &context_value);
    assert(object->flags == 0u);
#if UINTPTR_MAX == UINT32_MAX
    assert(object->listeners.stride == 0x18u); /* recovered stride (target) */
#else
    assert(object->listeners.stride >= 0x18u); /* widened host link layout */
#endif
    assert(object->rate == 0u && object->sample_buffer == NULL &&
           object->timer == NULL);
    /* Reachable through the registry. */
    assert(sensor_stream_object_lookup(&framework, "hr") == object);
    assert(sensor_stream_object_lookup(&framework, "spo2") == NULL);
    /* Long names are capped at eight bytes. */
    sensor_stream_object *long_named = sensor_stream_object_create(
        &framework, "factorymode", 2u, &test_provider, NULL);
    assert(long_named != NULL);
    assert(long_named->name[7] == 'm');
    assert(sensor_stream_object_lookup(&framework, "factorym") == long_named);
    assert(sensor_stream_object_lookup(&framework, "factorymo") == NULL);
    /* NULL context stays NULL (recovered conditional store). */
    assert(long_named->context == NULL);

    /* Bad arguments: stock hard-faults; the reconstruction faults via the
     * hook and returns NULL. */
    size_t faults = test_fault_calls;
    assert(sensor_stream_object_create(&framework, NULL, 4u, &test_provider,
                                       NULL) == NULL);
    assert(sensor_stream_object_create(&framework, "x", 4u, NULL, NULL) ==
           NULL);
    assert(sensor_stream_object_create(&framework, "x", 0u, &test_provider,
                                       NULL) == NULL);
    assert(test_fault_calls == faults + 3u);
    assert(sensor_stream_object_create(NULL, "x", 4u, &test_provider, NULL) ==
           NULL);

    /* Allocation failure: diagnostic + NULL. */
    test_fail_after = (long)test_allocate_calls;
    assert(sensor_stream_object_create(&framework, "spo2", 4u, &test_provider,
                                       NULL) == NULL);
    assert(test_diagnostic_seen("obj malloc fail"));
    test_fail_after = -1;

    /* Uninitialized registry lookup returns NULL (recovered stride guard). */
    sensor_stream fresh;
    fresh.registry.stride = 0u;
    fresh.registry.head = NULL;
    fresh.registry.tail = NULL;
    fresh.providers = test_providers();
    assert(sensor_stream_object_lookup(&fresh, "hr") == NULL);
    /* Unbound list providers fail explicitly. */
    sensor_stream unbound = framework;
    unbound.providers.list_first = NULL;
    assert(sensor_stream_object_lookup(&unbound, "hr") == NULL);
    unbound = framework;
    unbound.providers.list_next = NULL;
    assert(sensor_stream_object_lookup(&unbound, "hr") == NULL);
    assert(sensor_stream_object_lookup(NULL, "hr") == NULL);
    assert(sensor_stream_object_lookup(&framework, NULL) == NULL);
}

static void test_sensor_stream_object_insert_paths(void) {
    sensor_stream framework;
    test_reset(&framework);

    sensor_stream_object *first = sensor_stream_object_create(
        &framework, "a", 2u, &test_provider, NULL);
    sensor_stream_object *second = sensor_stream_object_create(
        &framework, "b", 2u, &test_provider, NULL);
    assert(first != NULL && second != NULL);
    /* Registry nodes chain in insertion order (push back). */
    sensor_stream_registry_node *node =
        (sensor_stream_registry_node *)framework.registry.head;
    assert(node != NULL && node->object == first);
    node = (sensor_stream_registry_node *)
        test_list_next(&framework.registry, node);
    assert(node != NULL && node->object == second);
    assert(test_list_next(&framework.registry, node) == NULL);

    /* Insert failure: push-back allocation fails -> false + diagnostic; the
     * created object is still returned (recovered quirk). */
    test_fail_after = (long)test_allocate_calls + 1; /* object ok, node fails */
    sensor_stream_object *third = sensor_stream_object_create(
        &framework, "c", 2u, &test_provider, NULL);
    assert(third != NULL);
    assert(test_diagnostic_seen("list insert fail"));
    assert(sensor_stream_object_lookup(&framework, "c") == NULL);
    test_fail_after = -1;

    /* Direct insert API: NULL args and unbound provider fail explicitly. */
    assert(!sensor_stream_object_insert(NULL, third));
    assert(!sensor_stream_object_insert(&framework, NULL));
    sensor_stream unbound = framework;
    unbound.providers.list_push_back_allocate = NULL;
    assert(!sensor_stream_object_insert(&unbound, third));
    assert(sensor_stream_object_insert(&framework, third));
    assert(sensor_stream_object_lookup(&framework, "c") == third);
}

static sensor_stream_listener *test_register_first_listener(
    sensor_stream *framework, sensor_stream_object **object_out) {
    sensor_stream_object *object = sensor_stream_object_create(
        framework, "raw_hr", 4u, &test_provider, NULL);
    assert(object != NULL);
    *object_out = object;
    sensor_stream_listener *listener = sensor_stream_listener_register(
        framework, object, "gomore", test_listener_callback, 1u,
        SENSOR_STREAM_MODE_PER_SAMPLE);
    assert(listener != NULL);
    return listener;
}

static void test_sensor_stream_registration(void) {
    sensor_stream framework;
    test_reset(&framework);

    /* By-name registration against an unknown stream fails with the
     * recovered diagnostic. */
    assert(sensor_stream_register_by_name(&framework, "nosuch", "l",
                                          test_listener_callback, 1u, 1u) ==
           NULL);
    assert(test_diagnostic_seen("register not find obj:%s"));
    assert(sensor_stream_register_by_name(NULL, "hr", "l",
                                          test_listener_callback, 1u, 1u) ==
           NULL);
    assert(sensor_stream_register_by_name(&framework, NULL, "l",
                                          test_listener_callback, 1u, 1u) ==
           NULL);

    sensor_stream_object *object;
    size_t faults = test_fault_calls;
    assert(sensor_stream_listener_register(&framework, NULL, "l",
                                           test_listener_callback, 1u, 1u) ==
           NULL);
    object = sensor_stream_object_create(&framework, "hr", 4u, &test_provider,
                                         NULL);
    assert(object != NULL);
    assert(sensor_stream_listener_register(&framework, object, NULL,
                                           test_listener_callback, 1u, 1u) ==
           NULL);
    assert(test_fault_calls == faults + 2u);
    assert(sensor_stream_listener_register(NULL, object, "l",
                                           test_listener_callback, 1u, 1u) ==
           NULL);

    /* First listener: buffer, open hook, timer at 1024/rate ticks. */
    test_tick = 50u;
    sensor_stream_listener *listener = sensor_stream_listener_register(
        &framework, object, "wearledx", test_listener_callback, 1u,
        SENSOR_STREAM_MODE_PER_SAMPLE);
    assert(listener != NULL);
    assert(listener->owner == object);
    assert(listener->rate == 1u);
    assert(listener->mode == SENSOR_STREAM_MODE_PER_SAMPLE);
    assert(listener->flags == 0u);
    assert(listener->callback == test_listener_callback);
    assert(listener->name[0] == 'w' && listener->name[6] == 'd');
    assert(listener->name[7] == 'x'); /* 8 bytes, no NUL: recovered cap */
    assert(object->rate == 1u);
    assert(object->sample_buffer != NULL);
    assert(test_open_calls == 1u);
    assert(object->timer != NULL);
    assert(object->timer->period == 1024u);
    assert(object->timer->callback == sensor_stream_timer_dispatch);
    assert(object->timer->context == object);
    assert(object->timer->repeat == SENSOR_STREAM_TIMER_REPEAT_FOREVER);
    assert(object->timer->last == 50u);
    assert((object->timer->flags & SENSOR_STREAM_TIMER_FLAG_ACTIVE) != 0u);
    /* Front insertion (bit 0 clear): the stream timer heads the list. */
    assert((sensor_stream_timer *)framework.housekeeping.timers.head ==
           object->timer);
    assert(framework.housekeeping.created == 1u);

    /* Rate above one is capped with the recovered diagnostic (typo-free
     * "only support 1 ord"). */
    sensor_stream_listener *second = sensor_stream_listener_register(
        &framework, object, "aging", test_listener_callback, 25u,
        SENSOR_STREAM_MODE_BATCH);
    assert(second != NULL);
    assert(second->rate == 1u);
    assert(test_diagnostic_seen("only support 1 ord"));
    /* Same aggregate rate: no resize, no retime. */
    assert(object->rate == 1u);
    assert(object->timer->period == 1024u);

    /* Back-insert selection via object flags bit 0 (0x0008A5C0). */
    sensor_stream_object_set_back_insert(&framework, object, 1u);
    assert((object->flags & 1u) == 1u);
    sensor_stream_object_set_back_insert(&framework, object, 0u);
    assert((object->flags & 1u) == 0u);
    sensor_stream_object_set_back_insert(&framework, NULL, 1u); /* no-op */

    /* A second object with back-insert sends its timer to the list tail. */
    sensor_stream_object *other = sensor_stream_object_create(
        &framework, "spo2", 2u, &test_provider, NULL);
    assert(other != NULL);
    sensor_stream_object_set_back_insert(&framework, other, 1u);
    sensor_stream_listener *third = sensor_stream_listener_register(
        &framework, other, "detect", test_listener_callback, 1u, 1u);
    assert(third != NULL);
    assert(framework.housekeeping.timers.tail == other->timer);
    assert(framework.housekeeping.timers.head == object->timer);

    /* Zero rate on the first listener: stock faults via a zero-byte
     * allocation; the reconstruction faults explicitly. */
    sensor_stream_object *zero_rate = sensor_stream_object_create(
        &framework, "wear", 2u, &test_provider, NULL);
    assert(zero_rate != NULL);
    faults = test_fault_calls;
    assert(sensor_stream_listener_register(&framework, zero_rate, "z",
                                           test_listener_callback, 0u, 1u) ==
           NULL);
    assert(test_fault_calls == faults + 1u);
    assert(zero_rate->sample_buffer == NULL);
    /* The listener itself stayed registered (recovered partial state). */
    assert(!sensor_stream_list_idle(&zero_rate->listeners));

    /* Buffer allocation failure on the first listener faults explicitly. */
    sensor_stream_object *oom = sensor_stream_object_create(
        &framework, "gray", 2u, &test_provider, NULL);
    assert(oom != NULL);
    test_fail_after = (long)test_allocate_calls + 1; /* listener node ok, buffer fails */
    faults = test_fault_calls;
    assert(sensor_stream_listener_register(&framework, oom, "g",
                                           test_listener_callback, 1u, 1u) ==
           NULL);
    assert(test_fault_calls == faults + 1u);
    test_fail_after = -1;
}

static void test_sensor_stream_dispatch_per_sample(void) {
    sensor_stream framework;
    test_reset(&framework);
    sensor_stream_object *object;
    sensor_stream_listener *listener =
        test_register_first_listener(&framework, &object);

    /* Short read: no cursor advance, no dispatch. */
    test_read_result = 2u; /* sample_size is 4 */
    test_read_fill = 0xAAu;
    sensor_stream_timer_dispatch(&framework, object->timer);
    assert(object->cursor == 0u);
    assert(test_listener_calls == 0u);
    test_read_result = 0u;

    /* Full read: mode-1 listener at the object rate fires every tick with
     * the freshly read sample. */
    test_tick = 100u;
    sensor_stream_timer_dispatch(&framework, object->timer);
    assert(test_listener_calls == 1u);
    assert(test_listener_seen == listener);
    assert(test_listener_length_seen == 4u);
    assert(test_listener_data_first == 0xAAu);
    assert(test_listener_data_seen == object->sample_buffer);
    /* rate 1: one sample wraps the chunk every tick, cursor resets. */
    assert(object->cursor == 0u);
    assert((object->flags & SENSOR_STREAM_OBJECT_FLAG_DISPATCH_ACTIVE) == 0u);

    /* Fractional rate accumulator (mode 1, listener rate below the object
     * rate): with the cap at 1 the only in-stock lower rate is 0, which
     * never accumulates, so this path is exercised with a constructed
     * aggregate rate of 2 against two rate-1 listeners. */
    sensor_stream_listener *slow = sensor_stream_listener_register(
        &framework, object, "slow", test_listener_callback, 1u,
        SENSOR_STREAM_MODE_PER_SAMPLE);
    assert(slow != NULL);
    object->rate = 2u;
    listener->flags = 0u;
    slow->flags = 0u;
    /* Tick 1: both accumulators 0 + 1 = 1 < 2 -> no fire. */
    test_listener_calls = 0u;
    sensor_stream_timer_dispatch(&framework, object->timer);
    assert(test_listener_calls == 0u);
    assert(listener->flags == (uint16_t)(1u << 1));
    assert(slow->flags == (uint16_t)(1u << 1));
    /* Tick 2: both accumulators 1 + 1 = 2 >= 2 -> fire, residue 0. */
    sensor_stream_timer_dispatch(&framework, object->timer);
    assert(test_listener_calls == 2u);
    assert(listener->flags == 0u);
    assert(slow->flags == 0u);

    /* NULL callback listeners are skipped without disturbing others. */
    sensor_stream_listener *silent = sensor_stream_listener_register(
        &framework, object, "silent", NULL, 1u, 1u);
    assert(silent != NULL);
    test_listener_calls = 0u;
    sensor_stream_timer_dispatch(&framework, object->timer); /* accumulate */
    sensor_stream_timer_dispatch(&framework, object->timer); /* fire tick */
    assert(test_listener_calls == 2u); /* silent never fires */

    /* Deferred-delete listeners are skipped (accumulator not advanced). */
    slow->flags |= SENSOR_STREAM_LISTENER_FLAG_DEFERRED;
    test_listener_calls = 0u;
    sensor_stream_timer_dispatch(&framework, object->timer); /* accumulate */
    sensor_stream_timer_dispatch(&framework, object->timer); /* fire tick */
    assert(test_listener_calls == 1u);
    slow->flags = 0u;

    /* Missing read hook / buffer / rate short-circuit the whole dispatch. */
    size_t reads = test_read_calls;
    object->rate = 0u;
    sensor_stream_timer_dispatch(&framework, object->timer);
    assert(test_read_calls == reads);
    object->rate = 2u;
    uint8_t *buffer = object->sample_buffer;
    object->sample_buffer = NULL;
    sensor_stream_timer_dispatch(&framework, object->timer);
    assert(test_read_calls == reads);
    object->sample_buffer = buffer;
    sensor_stream_timer_dispatch(NULL, object->timer);
    sensor_stream_timer_dispatch(&framework, NULL);
    assert(test_read_calls == reads);
}

static void test_sensor_stream_dispatch_batch(void) {
    sensor_stream framework;
    test_reset(&framework);
    sensor_stream_object *object = sensor_stream_object_create(
        &framework, "acc", 4u, &test_provider, NULL);
    assert(object != NULL);
    sensor_stream_listener *listener = sensor_stream_listener_register(
        &framework, object, "batch", test_listener_callback, 1u,
        SENSOR_STREAM_MODE_BATCH);
    assert(listener != NULL);

    /* Batch listener at the object rate: fires on wrap with the chunk
     * length (16-bit truncation of rate*sample_size). */
    test_read_fill = 0x5Cu;
    sensor_stream_timer_dispatch(&framework, object->timer);
    assert(test_listener_calls == 1u);
    assert(test_listener_length_seen == 4u); /* chunk 1*4 */
    assert(test_listener_data_seen == object->sample_buffer);

    /* Rate mismatch: resampled into the second half of the buffer. */
    sensor_stream_listener *half = sensor_stream_listener_register(
        &framework, object, "half", test_listener_callback, 1u,
        SENSOR_STREAM_MODE_BATCH);
    assert(half != NULL);
    object->rate = 2u; /* constructed: chunk 8, half-buffer scratch at +8? no:
                          chunk = 2*4 = 8, scratch = buffer + 8 */
    half->rate = 1u;
    /* Preload two samples; the dispatch reads at the cursor. */
    test_read_calls = 0u;
    test_listener_calls = 0u;
    test_listener_seen = NULL;
    sensor_stream_timer_dispatch(&framework, object->timer); /* sample 1 of 2 */
    assert(test_listener_seen == NULL ||
           test_listener_seen != half); /* no wrap yet */
    sensor_stream_timer_dispatch(&framework, object->timer); /* wrap */
    assert(test_listener_seen == half || test_listener_seen == listener);
    /* The mismatched listener received one resampled element from the
     * scratch half: produced = (2*1 + 1)/2 = 1 sample = 4 bytes. */
    size_t fires = test_listener_calls;
    assert(fires == 2u); /* both batch listeners fired on the wrap tick */
    (void)fires;

    /* Mode bytes other than 0/1 never fire. */
    sensor_stream_listener *odd = sensor_stream_listener_register(
        &framework, object, "odd", test_listener_callback, 1u, 7u);
    assert(odd != NULL);
    test_listener_calls = 0u;
    sensor_stream_timer_dispatch(&framework, object->timer);
    sensor_stream_timer_dispatch(&framework, object->timer);
    assert(test_listener_seen != odd);
}

static void test_sensor_stream_unregistration(void) {
    sensor_stream framework;
    test_reset(&framework);
    sensor_stream_object *object;
    sensor_stream_listener *listener =
        test_register_first_listener(&framework, &object);
    int closing = 0;
    object->context = &closing;

    /* Unknown stream: diagnostic only. */
    sensor_stream_listener_unregister(&framework, "nosuch", listener);
    assert(test_diagnostic_seen("unregister not find obj:%s"));
    /* Unknown listener: diagnostic only. */
    sensor_stream_listener stranger;
    sensor_stream_listener_unregister(&framework, "raw_hr", &stranger);
    assert(test_diagnostic_seen("%s not found in %s, skip unregister"));
    /* NULL listener faults explicitly (stock hard-fault). */
    size_t faults = test_fault_calls;
    sensor_stream_listener_unregister(&framework, "raw_hr", NULL);
    assert(test_fault_calls == faults + 1u);
    sensor_stream_listener_unregister(NULL, "raw_hr", listener);
    sensor_stream_listener_unregister(&framework, NULL, listener);

    /* Deferred removal while dispatch is active. */
    object->flags |= SENSOR_STREAM_OBJECT_FLAG_DISPATCH_ACTIVE;
    sensor_stream_listener_unregister(&framework, "raw_hr", listener);
    assert((listener->flags & SENSOR_STREAM_LISTENER_FLAG_DEFERRED) != 0u);
    assert((object->flags & SENSOR_STREAM_OBJECT_FLAG_PENDING_UNREGISTER) !=
           0u);
    assert(!sensor_stream_list_idle(&object->listeners)); /* still linked */
    size_t frees = test_free_calls;
    /* The dispatch tail performs the removal and, with the list empty,
     * releases buffer and timer and invokes the close hook. */
    sensor_stream_timer_dispatch(&framework, object->timer);
    assert(sensor_stream_list_idle(&object->listeners));
    assert((object->flags & SENSOR_STREAM_OBJECT_FLAG_PENDING_UNREGISTER) ==
           0u);
    assert(test_free_calls == frees + 3u); /* listener + buffer + timer */
    assert(object->sample_buffer == NULL && object->cursor == 0u);
    assert(object->timer == NULL);
    assert(test_close_calls == 1u);
    assert(test_hook_context_seen == &closing);
}

static void test_sensor_stream_unregister_rebalance(void) {
    sensor_stream framework;
    test_reset(&framework);
    sensor_stream_object *object;
    sensor_stream_listener *first =
        test_register_first_listener(&framework, &object);
    sensor_stream_listener *second = sensor_stream_listener_register(
        &framework, object, "timing", test_listener_callback, 1u, 1u);
    assert(second != NULL);

    /* Removing one of two same-rate listeners: no shrink, no retime. */
    sensor_stream_listener_unregister(&framework, "raw_hr", second);
    assert(sensor_stream_object_lookup(&framework, "raw_hr") == object);
    assert(!sensor_stream_list_idle(&object->listeners));
    assert(object->rate == 1u);
    assert(object->timer != NULL && object->timer->period == 1024u);
    assert(test_close_calls == 0u);

    /* Constructed multi-rate state: removing the fastest listener shrinks
     * the buffer through the resample helper and retimes the timer. */
    object->rate = 4u;
    object->cursor = 16u; /* four 4-byte samples valid */
    first->rate = 2u;
    sensor_stream_listener *fast = sensor_stream_listener_register(
        &framework, object, "fast", test_listener_callback, 1u, 1u);
    assert(fast != NULL);
    fast->rate = 4u;
    uint8_t *old_buffer = object->sample_buffer;
    size_t diagnostics = test_diagnostic_calls;
    sensor_stream_listener_unregister(&framework, "raw_hr", fast);
    /* Maximum remaining rate 2 < 4: resize + retime. */
    assert(object->rate == 2u);
    assert(object->timer->period == 512u);
    assert(object->sample_buffer != old_buffer);
    /* produced = min(2, (4*2 + 2)/4) = 2 samples = 8 bytes. */
    assert(object->cursor == 8u);
    assert(test_diagnostic_calls == diagnostics + 1u);
    assert(test_diagnostic_seen("reset timer,%s, tick:%d"));

    /* Removing the last listener releases everything. */
    sensor_stream_listener_unregister(&framework, "raw_hr", first);
    assert(sensor_stream_list_idle(&object->listeners));
    assert(object->sample_buffer == NULL && object->timer == NULL);
    assert(test_close_calls == 1u);
}

static void test_sensor_stream_timer_creation_and_release(void) {
    sensor_stream framework;
    test_reset(&framework);

    test_tick = 300u;
    sensor_stream_timer *front = sensor_stream_timer_create_front(
        &framework, test_timer_callback, 40u, NULL);
    assert(front != NULL);
    assert(front->period == 40u);
    assert(front->last == 300u);
    assert(front->callback == test_timer_callback);
    assert(front->repeat == SENSOR_STREAM_TIMER_REPEAT_FOREVER);
    assert(front->flags == SENSOR_STREAM_TIMER_FLAG_ACTIVE);
    assert(framework.housekeeping.created == 1u);
    assert(framework.housekeeping.next_wakeup == 0u); /* kicked */

    sensor_stream_timer *back = sensor_stream_timer_create_back(
        &framework, test_timer_callback, 80u, NULL);
    assert(back != NULL);
    assert(framework.housekeeping.timers.head == front);
    assert(framework.housekeeping.timers.tail == back);
    assert(test_list_next(&framework.housekeeping.timers, front) == back);

    /* Wake hook fires on kick with the stored context. */
    sensor_stream_set_wake_callback(&framework, test_wake,
                                    &test_wake_context_value);
    size_t wakes = test_wake_calls;
    sensor_stream_housekeeping_kick(&framework);
    assert(test_wake_calls == wakes + 1u);
    assert(test_wake_context_seen == &test_wake_context_value);
    sensor_stream_housekeeping_kick(NULL); /* no-op */

    /* Release: unlinks, marks, frees. */
    size_t frees = test_free_calls;
    sensor_stream_timer_release(&framework, front);
    assert(framework.housekeeping.released == 1u);
    assert(test_free_calls == frees + 1u);
    assert(framework.housekeeping.timers.head == back);
    size_t faults = test_fault_calls;
    sensor_stream_timer_release(&framework, NULL);
    assert(test_fault_calls == faults + 1u);
    sensor_stream_timer_release(NULL, back);

    /* Creation failure faults explicitly (allocation exhausted). */
    test_fail_after = (long)test_allocate_calls;
    faults = test_fault_calls;
    assert(sensor_stream_timer_create_front(&framework, test_timer_callback,
                                            10u, NULL) == NULL);
    assert(test_fault_calls == faults + 1u);
    test_fail_after = -1;

    /* Back creation without the provider fails explicitly. */
    sensor_stream unbound = framework;
    unbound.providers.list_push_back_allocate = NULL;
    assert(sensor_stream_timer_create_back(&unbound, test_timer_callback, 10u,
                                           NULL) == NULL);
    assert(sensor_stream_timer_create_front(NULL, test_timer_callback, 10u,
                                            NULL) == NULL);
}

static void test_sensor_stream_timer_expiry_and_poll(void) {
    sensor_stream framework;
    test_reset(&framework);

    test_tick = 1000u;
    sensor_stream_timer *timer = sensor_stream_timer_create_front(
        &framework, test_timer_callback, 100u, NULL);
    assert(timer != NULL);

    /* Not yet due: remaining 100 at creation tick. */
    assert(sensor_stream_timer_remaining(&framework, timer) == 100u);
    test_tick = 1050u;
    assert(sensor_stream_timer_remaining(&framework, timer) == 50u);
    assert(!sensor_stream_timer_expire(&framework, timer));
    assert(test_timer_callback_calls == 0u);

    /* Poll returns the minimum remaining across active timers. */
    assert(sensor_stream_timer_poll(&framework) == 50u);
    assert(framework.housekeeping.next_wakeup == 50u);

    /* Due: callback fires, expiry tick recorded, repeat stays forever. */
    test_tick = 1100u;
    assert(sensor_stream_timer_remaining(&framework, timer) == 0u);
    assert(sensor_stream_timer_expire(&framework, timer));
    assert(test_timer_callback_calls == 1u);
    assert(test_timer_callback_node == timer);
    assert(timer->last == 1100u);
    assert(timer->repeat == SENSOR_STREAM_TIMER_REPEAT_FOREVER);

    /* Saturating remaining beyond the period. */
    test_tick = 9999u;
    assert(sensor_stream_timer_remaining(&framework, timer) == 0u);

    /* One-shot timer: fires once, then auto-releases (flags bit 1). */
    test_tick = 20000u;
    sensor_stream_timer *one_shot = sensor_stream_timer_create_front(
        &framework, test_timer_callback, 10u, NULL);
    assert(one_shot != NULL);
    one_shot->repeat = 1u;
    test_tick = 20010u;
    size_t frees = test_free_calls;
    assert(sensor_stream_timer_expire(&framework, one_shot));
    assert(one_shot->repeat == 0u);
    assert(test_free_calls == frees + 1u); /* released */
    assert(framework.housekeeping.released == 1u);

    /* Exhausted timer without the active bit is stopped, not released. */
    sensor_stream_timer *stopped = sensor_stream_timer_create_front(
        &framework, test_timer_callback, 10u, NULL);
    assert(stopped != NULL);
    stopped->repeat = 0u;
    stopped->flags = 0u;
    framework.housekeeping.released = 0u;
    frees = test_free_calls;
    test_tick += 10u;
    assert(sensor_stream_timer_expire(&framework, stopped));
    assert((stopped->flags & SENSOR_STREAM_TIMER_FLAG_STOPPED) != 0u);
    assert(test_free_calls == frees); /* not released */
    /* A stopped timer never fires again. */
    size_t calls = test_timer_callback_calls;
    test_tick += 100u;
    assert(!sensor_stream_timer_expire(&framework, stopped));
    assert(test_timer_callback_calls == calls);

    /* NULL arguments fail explicitly. */
    assert(!sensor_stream_timer_expire(NULL, timer));
    assert(!sensor_stream_timer_expire(&framework, NULL));
    assert(sensor_stream_timer_remaining(NULL, timer) == 0u);
    assert(sensor_stream_timer_remaining(&framework, NULL) == 0u);

    /* Disabled housekeeping: poll returns 1 without scanning. */
    sensor_stream_housekeeping_enable(&framework, 0u);
    assert(framework.housekeeping.enabled == 0u);
    assert(sensor_stream_timer_poll(&framework) == 1u);
    sensor_stream_housekeeping_enable(&framework, 1u);
    assert(framework.housekeeping.enabled == 1u);
    sensor_stream_housekeeping_enable(NULL, 1u); /* no-op */

    /* Empty-but-enabled list reports 0xFFFFFFFF. */
    sensor_stream_timer_release(&framework, timer);
    sensor_stream_timer_release(&framework, stopped);
    assert(sensor_stream_timer_poll(&framework) == UINT32_C(0xFFFFFFFF));
}

static void test_sensor_stream_poll_rescan_and_drift(void) {
    sensor_stream framework;
    test_reset(&framework);

    /* A callback that creates a new timer sets the created mark and the poll
     * rescans from the head; both timers eventually expire in one poll. */
    test_tick = 10u;
    sensor_stream_timer *first = sensor_stream_timer_create_front(
        &framework, test_timer_callback, 5u, NULL);
    assert(first != NULL);
    test_tick = 20u;
    test_timer_callback_calls = 0u;
    /* Fires (10 ticks elapsed >= period 5); after firing, the remaining
     * time to the next expiry is the full period again. */
    assert(sensor_stream_timer_poll(&framework) == 5u);
    assert(test_timer_callback_calls == 1u);

    /* Drift: accumulate busy ticks across a >499 tick window. */
    sensor_stream fresh;
    test_reset(&fresh);
    test_tick = 0u;
    /* tick == 0 bumps the recovered zero-tick counter. */
    (void)sensor_stream_timer_poll(&fresh);
    assert(fresh.housekeeping.zero_tick_counter == 1u);
    fresh.housekeeping.zero_tick_counter = 100u;
    (void)sensor_stream_timer_poll(&fresh);
    assert(fresh.housekeeping.zero_tick_counter == 0u); /* wraps past 100 */

    test_tick = 1000u;
    (void)sensor_stream_timer_poll(&fresh); /* busy 0 in window of 1000 */
    assert(fresh.housekeeping.drift_correction == 100u); /* 100 - 0% */
    assert(fresh.housekeeping.drift_accumulator == 0u);
    assert(fresh.housekeeping.drift_mark == 1000u);
    /* Busy tick accumulation: the hook advances 50 ticks per call, so the
     * poll body itself consumes ticks between its tick reads. */
    sensor_stream_set_tick_hook(&fresh, test_tick_hook);
    test_hook_tick = 1100u;
    (void)sensor_stream_timer_poll(&fresh); /* span 100 < 500: no update */
    assert(fresh.housekeeping.drift_correction == 100u);
    /* start 1600, busy read 1650 (acc += 50), span read 1700 (span 700 >
     * 499): percent = 50*100/700 = 7 -> correction 100 - 7 = 93. */
    test_hook_tick = 1600u;
    test_hook_step = 50u;
    (void)sensor_stream_timer_poll(&fresh);
    assert(fresh.housekeeping.drift_correction == 93u);
    /* Unhooking returns to the fallback source. */
    test_hook_step = 0u;
    sensor_stream_set_tick_hook(&fresh, NULL);
    test_tick = 2000u;
    assert(sensor_stream_tick_now(&fresh) == 2000u);

    /* Reentrancy guard returns 1. */
    fresh.housekeeping.poll_active = 1u;
    assert(sensor_stream_timer_poll(&fresh) == 1u);
    fresh.housekeeping.poll_active = 0u;
    assert(sensor_stream_timer_poll(NULL) == 1u);

    /* Tick wraparound: elapsed uses 32-bit wrap arithmetic. */
    sensor_stream wrapped;
    test_reset(&wrapped);
    test_tick = 0xFFFFFFF0u;
    sensor_stream_timer *timer = sensor_stream_timer_create_front(
        &wrapped, test_timer_callback, 0x20u, NULL);
    assert(timer != NULL);
    test_tick = 0x10u; /* wrapped */
    assert(sensor_stream_ticks_elapsed(&wrapped, 0xFFFFFFF0u) == 0x20u);
    assert(sensor_stream_timer_remaining(&wrapped, timer) == 0u);
    assert(sensor_stream_ticks_elapsed(NULL, 0u) == 0u);
}

static void test_sensor_stream_tick_sources(void) {
    sensor_stream framework;
    test_reset(&framework);

    test_tick = 4242u;
    assert(sensor_stream_tick_now(&framework) == 4242u);
    test_hook_tick = 77u;
    sensor_stream_set_tick_hook(&framework, test_tick_hook);
    assert(sensor_stream_tick_now(&framework) == 77u); /* RAM hook wins */
    sensor_stream_set_tick_hook(&framework, NULL);
    assert(sensor_stream_tick_now(&framework) == 4242u);
    framework.providers.tick_fallback = NULL;
    assert(sensor_stream_tick_now(&framework) == 0u); /* explicit zero */
    assert(sensor_stream_tick_now(NULL) == 0u);
}

static void test_sensor_stream_singletons(void) {
    sensor_stream framework;
    test_reset(&framework);

    /* Unbound singleton providers fail explicitly. */
    assert(sensor_stream_acc_object_create(&framework) == NULL);
    assert(sensor_stream_temp_object_create(&framework) == NULL);
    assert(sensor_stream_acc_object_create(NULL) == NULL);

    sensor_stream_bind_singleton_providers(&framework, &test_provider,
                                           &test_provider);
    sensor_stream_object *acc = sensor_stream_acc_object_create(&framework);
    sensor_stream_object *temp = sensor_stream_temp_object_create(&framework);
    assert(acc != NULL && temp != NULL);
    assert(acc->name[0] == 'a' && acc->name[1] == 'c' && acc->name[2] == 'c' &&
           acc->name[3] == '\0');
    assert(acc->sample_size == 0xBCu);
    assert(acc->context == NULL);
    assert(temp->name[0] == 't' && temp->name[4] == '\0');
    assert(temp->sample_size == 2u);
    assert(sensor_stream_object_lookup(&framework, "acc") == acc);
    assert(sensor_stream_object_lookup(&framework, "temp") == temp);
    sensor_stream_bind_singleton_providers(NULL, &test_provider,
                                           &test_provider); /* no-op */
}

static void test_sensor_stream_sinks(void) {
    sensor_stream framework;
    test_reset(&framework);

    sensor_stream_sink_store4(&framework, 1u, 2u, 3u, 4u);
    assert(framework.sinks.descriptor4[0] == 1u &&
           framework.sinks.descriptor4[3] == 4u);
    sensor_stream_sink_store6(&framework, 5u, 6u, 7u, 8u, 9u, 10u);
    assert(framework.sinks.descriptor6[0] == 5u &&
           framework.sinks.descriptor6[5] == 10u);
    sensor_stream_sink_store6_sign_extended(&framework, 1u, 2u, 3u, 0xFFFFFF80u,
                                            5u, 6u);
    assert(framework.sinks.descriptor6s[3] == 0xFFFFFF80u); /* sign-extended */
    sensor_stream_sink_store6_sign_extended(&framework, 1u, 2u, 3u, 0x7Fu, 5u,
                                            6u);
    assert(framework.sinks.descriptor6s[3] == 0x7Fu);
    sensor_stream_sink_store4(NULL, 1u, 2u, 3u, 4u);
    sensor_stream_sink_store6(NULL, 1u, 2u, 3u, 4u, 5u, 6u);
    sensor_stream_sink_store6_sign_extended(NULL, 1u, 2u, 3u, 4u, 5u, 6u);

    int32_t minus = -5;
    int32_t zero = 0;
    int32_t plus = 42;
    sensor_stream_sink_triple_clamped_primary(&framework, &minus, &zero,
                                              &plus);
    assert(framework.sinks.clamped_primary[0] == 0);
    assert(framework.sinks.clamped_primary[1] == 0);
    assert(framework.sinks.clamped_primary[2] == 42);
    sensor_stream_sink_triple_clamped_secondary(&framework, &plus, &minus,
                                                &plus);
    assert(framework.sinks.clamped_secondary[0] == 42);
    assert(framework.sinks.clamped_secondary[1] == 0);
    assert(framework.sinks.clamped_secondary[2] == 42);
    /* NULL arguments are explicit no-ops. */
    sensor_stream_sink_triple_clamped_primary(NULL, &plus, &plus, &plus);
    sensor_stream_sink_triple_clamped_primary(&framework, NULL, &plus, &plus);
    sensor_stream_sink_triple_clamped_secondary(&framework, &plus, NULL,
                                                &plus);
    sensor_stream_sink_triple_clamped_secondary(&framework, &plus, &plus,
                                                NULL);
    assert(framework.sinks.clamped_primary[2] == 42);
}

static void test_sensor_stream_timer_small_ops(void) {
    sensor_stream framework;
    test_reset(&framework);
    sensor_stream_timer *timer = sensor_stream_timer_create_front(
        &framework, test_timer_callback, 100u, NULL);
    assert(timer != NULL);

    sensor_stream_timer_set_period(&framework, timer, 250u);
    assert(timer->period == 250u);
    size_t faults = test_fault_calls;
    sensor_stream_timer_set_period(&framework, NULL, 1u);
    assert(test_fault_calls == faults + 1u);
    sensor_stream_timer_set_period(NULL, timer, 1u);
    assert(timer->period == 250u);

    sensor_stream_timer_stop(&framework, timer);
    assert((timer->flags & SENSOR_STREAM_TIMER_FLAG_STOPPED) != 0u);
    sensor_stream_timer_stop(&framework, NULL);
    assert(test_fault_calls == faults + 2u);
    sensor_stream_timer_stop(NULL, timer);

    /* set_period is exercised through the recovered retiming paths too
     * (covered in the rebalance test). */
    sensor_stream_timer_release(&framework, timer);
}

void test_reconstructed_sensor_stream(void) {
    test_sensor_stream_list_primitives();
    test_sensor_stream_resample_copy();
    test_sensor_stream_object_lifecycle();
    test_sensor_stream_object_insert_paths();
    test_sensor_stream_registration();
    test_sensor_stream_dispatch_per_sample();
    test_sensor_stream_dispatch_batch();
    test_sensor_stream_unregistration();
    test_sensor_stream_unregister_rebalance();
    test_sensor_stream_timer_creation_and_release();
    test_sensor_stream_timer_expiry_and_poll();
    test_sensor_stream_poll_rescan_and_drift();
    test_sensor_stream_tick_sources();
    test_sensor_stream_singletons();
    test_sensor_stream_sinks();
    test_sensor_stream_timer_small_ops();
    puts("openR1: reconstructed sensor-stream framework tests passed");
}
