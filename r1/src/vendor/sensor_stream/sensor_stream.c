/*
 * Provenance banner
 * -----------------
 * Family:         unknown_sensor_stream_framework_candidate (Bravechip B210
 *                 "ChipletRing" platform generic named sensor-stream
 *                 subscription framework).
 * Stock image:    application image, load base 0x00027000, sha256
 *                 0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a.
 * Evidence:       r1/research/decompilation/application/decompiler-output.c
 *                 (all 32 Ghidra bodies) plus literal-pool/const reads from
 *                 the byte-exact rebuilt image
 *                 r1/research/decompilation/rebuild/rebuilt-application.bin.
 * Status:         RECONSTRUCTED FROM DECOMPILATION EVIDENCE; NOT VENDOR
 *                 SOURCE.  Never present this file as Even Realities or
 *                 Bravechip source.  Reduction is owner-authorized per
 *                 docs/SOURCE-ADMISSION.md ("Owner-authorized full reduction
 *                 (2026-08-14)").
 *
 * Per-function mapping (stock extent, end-exclusive / size -> symbol here):
 *
 *   0x0005D8FE..<0x0005D90D  16  -> sensor_stream_list_descriptor_init
 *   0x0005D90E..<0x0005D949  60  -> sensor_stream_list_push_front_allocate
 *   0x0005D986..<0x0005D997  18  -> sensor_stream_list_idle
 *   0x0007D0D8..<0x0007D153  122 -> sensor_stream_resample_copy
 *   0x000896F0..<0x000897B7  200 -> sensor_stream_object_create
 *   0x000897E8..<0x0008984B  100 -> sensor_stream_register_by_name
 *   0x00089890..<0x00089A60  464 -> sensor_stream_listener_register
 *   0x00089B08..<0x0008A1AA  562 -> sensor_stream_listener_unregister
 *                                   (noncontiguous: 0x89B08/0x89C20/0x8A068/
 *                                   0x8A180 ranges)
 *   0x00089D54..<0x00089D83  48  -> sensor_stream_object_lookup
 *   0x00089D88..<0x00089D93  12  -> sensor_stream_acc_object_create
 *   0x00089D9C..<0x00089DF7  92  -> sensor_stream_object_insert
 *   0x00089E50..<0x00089E87  56  -> sensor_stream_sink_triple_clamped_secondary
 *   0x00089E8C..<0x00089EC3  56  -> sensor_stream_sink_triple_clamped_primary
 *   0x00089EC8..<0x00089ED1  10  -> sensor_stream_sink_store4
 *   0x00089ED8..<0x00089EE5  14  -> sensor_stream_sink_store6
 *   0x0008A03C..<0x0008A04D  18  -> sensor_stream_sink_store6_sign_extended
 *   0x0008A1AC..<0x0008A1B7  12  -> sensor_stream_temp_object_create
 *   0x0008A1C4..<0x0008A1CF  12  -> sensor_stream_ticks_elapsed
 *   0x0008A1D0..<0x0008A1DB  12  -> sensor_stream_tick_now
 *   0x0008A1E0..<0x0008A310  422 -> sensor_stream_timer_dispatch
 *                                   (noncontiguous: 0x8A1E0 + 0x89BA8 tail)
 *   0x0008A310..<0x0008A363  84  -> sensor_stream_timer_create_front
 *   0x0008A368..<0x0008A3BB  84  -> sensor_stream_timer_create_back
 *   0x0008A3C0..<0x0008A3EB  44  -> sensor_stream_timer_release
 *   0x0008A3F0..<0x0008A3FD  14  -> sensor_stream_housekeeping_enable
 *   0x0008A404..<0x0008A457  84  -> sensor_stream_timer_expire
 *   0x0008A45C..<0x0008A539  222 -> sensor_stream_timer_poll
 *   0x0008A540..<0x0008A551  18  -> sensor_stream_housekeeping_kick
 *   0x0008A55C..<0x0008A57B  32  -> sensor_stream_initialize (recovered tail)
 *   0x0008A584..<0x0008A59D  26  -> sensor_stream_timer_stop
 *   0x0008A5C0..<0x0008A5CF  16  -> sensor_stream_object_set_back_insert
 *   0x0008A5D0..<0x0008A5E3  20  -> sensor_stream_timer_set_period
 *   0x0008A5E4..<0x0008A5FB  24  -> sensor_stream_timer_remaining
 *
 * Observable behavior is preserved; restructuring is limited to explicit
 * provider bindings (FreeRTOS heap, registry-family list walkers, CMSIS tick,
 * nRF_LOG diagnostics, app fault path), pointer/argument validation in place
 * of the stock privileged fault loops, and a zero-initialized timer flags
 * word.  Every divergence is listed in
 * docs/correlation/SENSOR-STREAM-REDUCTION-CORRELATION.md.
 */

#include "sensor_stream/sensor_stream.h"

/* The recovered field offsets are a property of the 32-bit target ABI; on
 * wider host pointer ABIs the C layout legitimately differs, so the exact
 * layout asserts apply to the target ABI only. */
#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(sensor_stream_list_descriptor) == 12u,
               "recovered list descriptor is 12 bytes");
_Static_assert(offsetof(sensor_stream_listener, name) == 0x04u, "listener +0x04");
_Static_assert(offsetof(sensor_stream_listener, rate) == 0x0Du, "listener +0x0D");
_Static_assert(offsetof(sensor_stream_listener, mode) == 0x0Eu, "listener +0x0E");
_Static_assert(offsetof(sensor_stream_listener, callback) == 0x10u,
               "listener +0x10");
_Static_assert(offsetof(sensor_stream_listener, flags) == 0x14u, "listener +0x14");
_Static_assert(offsetof(sensor_stream_listener, link_previous) == 0x18u,
               "listener +0x18");
_Static_assert(sizeof(sensor_stream_listener) == 0x20u,
               "recovered listener node is 0x20 bytes");
_Static_assert(offsetof(sensor_stream_timer, last) == 0x04u, "timer +0x04");
_Static_assert(offsetof(sensor_stream_timer, callback) == 0x08u, "timer +0x08");
_Static_assert(offsetof(sensor_stream_timer, context) == 0x0Cu, "timer +0x0C");
_Static_assert(offsetof(sensor_stream_timer, repeat) == 0x10u, "timer +0x10");
_Static_assert(offsetof(sensor_stream_timer, flags) == 0x14u, "timer +0x14");
_Static_assert(offsetof(sensor_stream_timer, link_previous) == 0x18u,
               "timer +0x18");
_Static_assert(sizeof(sensor_stream_timer) == 0x20u,
               "recovered timer node is 0x20 bytes");
_Static_assert(offsetof(sensor_stream_object, provider) == 0x0Cu, "object +0x0C");
_Static_assert(offsetof(sensor_stream_object, rate) == 0x10u, "object +0x10");
_Static_assert(offsetof(sensor_stream_object, sample_buffer) == 0x14u,
               "object +0x14");
_Static_assert(offsetof(sensor_stream_object, cursor) == 0x18u, "object +0x18");
_Static_assert(offsetof(sensor_stream_object, sample_size) == 0x1Cu,
               "object +0x1C");
_Static_assert(offsetof(sensor_stream_object, timer) == 0x20u, "object +0x20");
_Static_assert(offsetof(sensor_stream_object, context) == 0x24u, "object +0x24");
_Static_assert(offsetof(sensor_stream_object, flags) == 0x28u, "object +0x28");
_Static_assert(offsetof(sensor_stream_object, listeners) == 0x2Cu, "object +0x2C");
_Static_assert(sizeof(sensor_stream_object) == SENSOR_STREAM_OBJECT_BYTES,
               "recovered object is 0x38 bytes");
_Static_assert(offsetof(sensor_stream_registry_node, object) == 0x04u,
               "registry node +0x04");
_Static_assert(sizeof(sensor_stream_registry_node) == 0x10u,
               "recovered registry node is 0x10 bytes");
_Static_assert(offsetof(sensor_stream_housekeeping, enabled) == 0x0Cu, "hk +0x0C");
_Static_assert(offsetof(sensor_stream_housekeeping, drift_correction) == 0x0Du,
               "hk +0x0D");
_Static_assert(offsetof(sensor_stream_housekeeping, released) == 0x0Eu, "hk +0x0E");
_Static_assert(offsetof(sensor_stream_housekeeping, created) == 0x0Fu, "hk +0x0F");
_Static_assert(offsetof(sensor_stream_housekeeping, next_wakeup) == 0x10u,
               "hk +0x10");
_Static_assert(offsetof(sensor_stream_housekeeping, poll_active) == 0x14u,
               "hk +0x14");
_Static_assert(offsetof(sensor_stream_housekeeping, drift_accumulator) == 0x1Cu,
               "hk +0x1C");
_Static_assert(offsetof(sensor_stream_housekeeping, drift_mark) == 0x20u,
               "hk +0x20");
_Static_assert(offsetof(sensor_stream_housekeeping, zero_tick_counter) == 0x24u,
               "hk +0x24");
_Static_assert(offsetof(sensor_stream_housekeeping, wake) == 0x28u, "hk +0x28");
_Static_assert(offsetof(sensor_stream_housekeeping, wake_context) == 0x2Cu,
               "hk +0x2C");
_Static_assert(sizeof(sensor_stream_housekeeping) == 0x30u,
               "recovered housekeeping block is 0x30 bytes");
_Static_assert(offsetof(sensor_stream_sink_block, descriptor6) == 0x10u,
               "sinks +0x10");
_Static_assert(offsetof(sensor_stream_sink_block, descriptor6s) == 0x28u,
               "sinks +0x28");
_Static_assert(offsetof(sensor_stream_sink_block, clamped_primary) == 0xC0u,
               "sinks +0xC0");
_Static_assert(offsetof(sensor_stream_sink_block, clamped_secondary) == 0xCCu,
               "sinks +0xCC");
_Static_assert(sizeof(sensor_stream_sink_block) == 0xD8u,
               "recovered sink block is 0xD8 bytes");
#endif

/* Link arithmetic.  On the recovered 32-bit target ABI the links sit at
 * node + stride (previous) and node + stride + 4 (next), and a node
 * allocation is stride + 8 bytes.  On wider host pointer ABIs the link
 * words legitimately widen (the pilot documents the same clause), so the
 * offset/allocation use the pointer width while the recovered payload
 * strides below keep their stock values. */
#define SENSOR_STREAM_LINK_WIDTH ((uint32_t)sizeof(void *))

/* Effective per-list payload sizes handed to the descriptor init.  Target:
 * the recovered values.  Host: the typed payload size so the links stay
 * clear of the widened fields. */
#if UINTPTR_MAX == UINT32_MAX
#define LISTENER_LINK_PAYLOAD SENSOR_STREAM_LISTENER_PAYLOAD
#define TIMER_LINK_PAYLOAD SENSOR_STREAM_TIMER_PAYLOAD
#define REGISTRY_LINK_PAYLOAD SENSOR_STREAM_REGISTRY_PAYLOAD
#else
#define LISTENER_LINK_PAYLOAD \
    ((uint32_t)offsetof(sensor_stream_listener, link_previous))
#define TIMER_LINK_PAYLOAD \
    ((uint32_t)offsetof(sensor_stream_timer, link_previous))
#define REGISTRY_LINK_PAYLOAD \
    ((uint32_t)offsetof(sensor_stream_registry_node, link_previous))
#endif

/* Recovered diagnostic message strings (stock: paired [RING]-tagged and
 * plain nRF_LOG copies; emission itself belongs to the Nordic/SEGGER logging
 * providers and is surfaced here through the optional diagnostic hook). */
#define SENSOR_STREAM_MSG_OBJECT_ALLOC_FAIL "obj malloc fail"
#define SENSOR_STREAM_MSG_LISTENER_REGISTER_FAIL "lisent register fail" /* sic */
#define SENSOR_STREAM_MSG_ORDER_CAP "only support 1 ord"
#define SENSOR_STREAM_MSG_RESET_TIMER "reset timer,%s, tick:%d"
#define SENSOR_STREAM_MSG_REGISTER_NOT_FOUND "register not find obj:%s"
#define SENSOR_STREAM_MSG_UNREGISTER_NOT_FOUND "unregister not find obj:%s"
#define SENSOR_STREAM_MSG_LISTENER_NOT_FOUND "%s not found in %s, skip unregister"
#define SENSOR_STREAM_MSG_LIST_INSERT_FAIL "list insert fail"

/* Local byte/text helpers; the freestanding build does not use libc
 * string.h. */
static void copy_bytes(uint8_t *destination, const uint8_t *source,
                       uint32_t count) {
    for (uint32_t index = 0u; index < count; ++index) {
        destination[index] = source[index];
    }
}

static void zero_bytes(void *destination, size_t count) {
    uint8_t *bytes = (uint8_t *)destination;
    for (size_t index = 0u; index < count; ++index) {
        bytes[index] = 0u;
    }
}

static uint32_t text_length(const char *text) {
    uint32_t length = 0u;
    while (text[length] != '\0') {
        ++length;
    }
    return length;
}

static bool text_equal(const char *left, const char *right) {
    while (*left != '\0' && *left == *right) {
        ++left;
        ++right;
    }
    return *left == *right;
}

static void fault(sensor_stream *framework) {
    if (framework != NULL && framework->providers.fault != NULL) {
        /* Stock reaches a privileged hang (setBasePriority + infinite loop)
         * on these paths; the bound target fault handler does not return. */
        framework->providers.fault();
    }
}

static void diagnose(sensor_stream *framework, const char *message,
                     const char *detail, uint32_t value) {
    if (framework != NULL && framework->providers.diagnostic != NULL) {
        framework->providers.diagnostic(message, detail, value);
    }
}

void sensor_stream_list_descriptor_init(
    sensor_stream_list_descriptor *descriptor, uint32_t payload_size) {
    if (descriptor == NULL) {
        return;
    }
    descriptor->stride = (payload_size + 3u) & ~UINT32_C(3);
    descriptor->head = NULL;
    descriptor->tail = NULL;
}

void *sensor_stream_list_push_front_allocate(
    sensor_stream *framework, sensor_stream_list_descriptor *descriptor) {
    if (framework == NULL || descriptor == NULL) {
        return NULL;
    }
    if (framework->providers.allocate == NULL) {
        return NULL;
    }
    uint8_t *node = (uint8_t *)framework->providers.allocate(
        descriptor->stride + 2u * SENSOR_STREAM_LINK_WIDTH);
    if (node == NULL) {
        return NULL;
    }
    /* Recovered link layout: previous at node + stride, next at
     * node + stride + link width (stock one-instruction setters
     * 0x00077E3C/0x00077E30 inlined here). */
    uint8_t **previous = (uint8_t **)(void *)(node + descriptor->stride);
    uint8_t **next = (uint8_t **)(void *)(node + descriptor->stride +
                                         SENSOR_STREAM_LINK_WIDTH);
    *previous = NULL;
    *next = (uint8_t *)descriptor->head;
    if (descriptor->head != NULL) {
        uint8_t *head = (uint8_t *)descriptor->head;
        *(uint8_t **)(void *)(head + descriptor->stride) = node;
    }
    descriptor->head = node;
    if (descriptor->tail == NULL) {
        descriptor->tail = node;
    }
    return node;
}

bool sensor_stream_list_idle(const sensor_stream_list_descriptor *descriptor) {
    if (descriptor != NULL &&
            (descriptor->head != NULL || descriptor->tail != NULL)) {
        return false;
    }
    return true;
}

uint32_t sensor_stream_resample_copy(const uint8_t *source,
                                     uint32_t source_samples,
                                     uint32_t source_bytes,
                                     uint8_t *destination,
                                     uint32_t target_samples,
                                     uint32_t element_bytes) {
    if (source == NULL || destination == NULL || element_bytes == 0u ||
            source_samples == 0u || target_samples == 0u) {
        return 0u;
    }
    uint32_t valid = source_bytes / element_bytes;
    if (valid == 0u) {
        return 0u;
    }
    if (valid > source_samples) {
        valid = source_samples;
    }
    uint32_t produced =
        (valid * target_samples + (source_samples >> 1)) / source_samples;
    uint32_t count = target_samples < produced ? target_samples : produced;
    if (count == 0u) {
        return 0u;
    }
    for (uint32_t index = 0u; index < count; ++index) {
        uint32_t source_index = (index * source_samples) / target_samples;
        if (valid <= source_index) {
            source_index = valid - 1u;
        }
        copy_bytes(destination + index * element_bytes,
                   source + source_index * element_bytes, element_bytes);
    }
    return count * element_bytes;
}

sensor_stream_object *sensor_stream_object_create(
    sensor_stream *framework, const char *name, uint32_t sample_size,
    const sensor_stream_provider_ops *provider, void *context) {
    if (framework == NULL) {
        return NULL;
    }
    if (name == NULL || provider == NULL || sample_size == 0u) {
        /* Stock hard-faults on each of these. */
        fault(framework);
        return NULL;
    }
    if (framework->providers.allocate == NULL) {
        return NULL;
    }
    /* sizeof equals the recovered 0x38 on the 32-bit target ABI (static
     * assert) and legitimately widens on host ABIs. */
    sensor_stream_object *object = (sensor_stream_object *)
        framework->providers.allocate((uint32_t)sizeof(sensor_stream_object));
    if (object == NULL) {
        diagnose(framework, SENSOR_STREAM_MSG_OBJECT_ALLOC_FAIL, NULL, 0u);
        return NULL;
    }
    zero_bytes(object, sizeof(*object));
    /* Recovered: dispatch/pending flags cleared at creation (& 0xF9). */
    object->flags &= (uint8_t)~(SENSOR_STREAM_OBJECT_FLAG_DISPATCH_ACTIVE |
                                SENSOR_STREAM_OBJECT_FLAG_PENDING_UNREGISTER);
    uint32_t name_length = text_length(name);
    if (name_length > SENSOR_STREAM_NAME_MAX) {
        name_length = SENSOR_STREAM_NAME_MAX;
    }
    copy_bytes((uint8_t *)object->name, (const uint8_t *)name, name_length);
    sensor_stream_list_descriptor_init(&object->listeners,
                                       LISTENER_LINK_PAYLOAD);
    if (context != NULL) {
        object->context = context;
    }
    object->provider = provider;
    object->sample_size = (uint16_t)sample_size;
    /* Recovered quirk: a registry-insert failure is logged inside the insert
     * routine but the object is still returned. */
    (void)sensor_stream_object_insert(framework, object);
    return object;
}

bool sensor_stream_object_insert(sensor_stream *framework,
                                 sensor_stream_object *object) {
    if (framework == NULL || object == NULL) {
        return false;
    }
    sensor_stream_list_descriptor *registry = &framework->registry;
    if (registry->stride == 0u) {
        sensor_stream_list_descriptor_init(registry,
                                           REGISTRY_LINK_PAYLOAD);
    }
    if (framework->providers.list_push_back_allocate == NULL) {
        return false;
    }
    sensor_stream_registry_node *node = (sensor_stream_registry_node *)
        framework->providers.list_push_back_allocate(registry);
    if (node == NULL) {
        diagnose(framework, SENSOR_STREAM_MSG_LIST_INSERT_FAIL, NULL, 0u);
        return false;
    }
    node->object = object;
    return true;
}

sensor_stream_object *sensor_stream_object_lookup(sensor_stream *framework,
                                                  const char *name) {
    if (framework == NULL || name == NULL) {
        return NULL;
    }
    sensor_stream_list_descriptor *registry = &framework->registry;
    /* Recovered guard: the lookup walks only an initialized registry. */
    if (registry->stride == 0u) {
        return NULL;
    }
    if (framework->providers.list_first == NULL ||
            framework->providers.list_next == NULL) {
        return NULL;
    }
    sensor_stream_registry_node *node = (sensor_stream_registry_node *)
        framework->providers.list_first(registry);
    while (node != NULL) {
        sensor_stream_object *object = node->object;
        if (object != NULL && text_equal(object->name, name)) {
            return object;
        }
        node = (sensor_stream_registry_node *)
            framework->providers.list_next(registry, node);
    }
    return NULL;
}

/* Shared tail of unregistration and deferred dispatch cleanup (stock
 * duplicates the block at 0x0008A068/0x0008A180 and 0x00089BA8; the C
 * shares it, observable behavior identical).  Requires an existing listener
 * removal to have happened. */
static void stream_release_resources(sensor_stream *framework,
                                     sensor_stream_object *object) {
    if (object->sample_buffer != NULL) {
        if (framework->providers.free != NULL) {
            framework->providers.free(object->sample_buffer);
        }
        object->sample_buffer = NULL;
        object->cursor = 0u;
    }
    void *context = object->context;
    if (object->timer != NULL) {
        sensor_stream_timer_release(framework, object->timer);
        object->timer = NULL;
    }
    if (object->provider != NULL && object->provider->close != NULL) {
        object->provider->close(context);
    }
}

static void stream_shrink_to_maximum_rate(sensor_stream *framework,
                                          sensor_stream_object *object) {
    if (framework->providers.list_first == NULL ||
            framework->providers.list_next == NULL) {
        return;
    }
    uint32_t maximum = 0u;
    sensor_stream_listener *node = (sensor_stream_listener *)
        framework->providers.list_first(&object->listeners);
    while (node != NULL) {
        if (maximum < node->rate) {
            maximum = node->rate;
        }
        node = (sensor_stream_listener *)
            framework->providers.list_next(&object->listeners, node);
    }
    if (maximum != 0u && maximum < object->rate) {
        if (object->sample_buffer != NULL) {
            if (framework->providers.allocate == NULL ||
                    framework->providers.free == NULL) {
                return;
            }
            uint32_t buffer_size = maximum * object->sample_size * 2u;
            uint8_t *resized =
                (uint8_t *)framework->providers.allocate(buffer_size);
            if (resized == NULL) {
                /* Stock hard-faults here. */
                fault(framework);
                return;
            }
            object->cursor = sensor_stream_resample_copy(
                object->sample_buffer, object->rate, object->cursor, resized,
                maximum, object->sample_size);
            framework->providers.free(object->sample_buffer);
            object->sample_buffer = resized;
        }
        object->rate = (uint8_t)maximum;
        uint32_t period = SENSOR_STREAM_TICK_HZ / maximum;
        sensor_stream_timer_set_period(framework, object->timer, period);
        diagnose(framework, SENSOR_STREAM_MSG_RESET_TIMER, object->name,
                 period);
    }
}

static void stream_after_listener_removal(sensor_stream *framework,
                                          sensor_stream_object *object) {
    if (!sensor_stream_list_idle(&object->listeners)) {
        stream_shrink_to_maximum_rate(framework, object);
        return;
    }
    stream_release_resources(framework, object);
}

sensor_stream_listener *sensor_stream_listener_register(
    sensor_stream *framework, sensor_stream_object *object,
    const char *listener_name, sensor_stream_listener_callback callback,
    uint32_t rate, uint8_t mode) {
    if (framework == NULL) {
        return NULL;
    }
    if (object == NULL || listener_name == NULL) {
        /* Stock hard-faults on both. */
        fault(framework);
        return NULL;
    }
    bool was_idle = sensor_stream_list_idle(&object->listeners);
    sensor_stream_listener *listener = (sensor_stream_listener *)
        sensor_stream_list_push_front_allocate(framework, &object->listeners);
    if (listener == NULL) {
        diagnose(framework, SENSOR_STREAM_MSG_LISTENER_REGISTER_FAIL, NULL, 0u);
        return NULL;
    }
    if (rate > 1u) {
        diagnose(framework, SENSOR_STREAM_MSG_ORDER_CAP, NULL, 0u);
        rate = 1u;
    }
    listener->callback = callback;
    listener->rate = (uint8_t)rate;
    listener->mode = mode;
    listener->flags = 0u;
    uint32_t name_length = text_length(listener_name);
    if (name_length > SENSOR_STREAM_NAME_MAX) {
        name_length = SENSOR_STREAM_NAME_MAX;
    }
    /* Recovered: only the capped name bytes are copied; the tail of the
     * 8-byte field keeps the heap content. */
    copy_bytes((uint8_t *)listener->name, (const uint8_t *)listener_name,
               name_length);
    listener->owner = object;
    if (was_idle) {
        object->rate = (uint8_t)rate;
        uint32_t buffer_size = rate * object->sample_size * 2u;
        if (buffer_size == 0u || framework->providers.allocate == NULL) {
            /* Stock allocates 0 bytes, gets NULL, and hard-faults. */
            fault(framework);
            return NULL;
        }
        object->sample_buffer =
            (uint8_t *)framework->providers.allocate(buffer_size);
        if (object->sample_buffer == NULL) {
            /* Stock hard-faults here. */
            fault(framework);
            return NULL;
        }
        if (object->provider->open != NULL) {
            object->provider->open(object->context);
        }
        uint32_t period = SENSOR_STREAM_TICK_HZ / rate;
        sensor_stream_timer *timer;
        if ((object->flags & SENSOR_STREAM_OBJECT_FLAG_BACK_INSERT) == 0u) {
            timer = sensor_stream_timer_create_front(
                framework, sensor_stream_timer_dispatch, period, object);
        } else {
            timer = sensor_stream_timer_create_back(
                framework, sensor_stream_timer_dispatch, period, object);
        }
        object->timer = timer;
        if (timer == NULL) {
            return NULL;
        }
    } else if (object->rate < rate) {
        if (object->sample_buffer != NULL) {
            if (framework->providers.allocate == NULL ||
                    framework->providers.free == NULL) {
                return NULL;
            }
            uint32_t buffer_size = rate * object->sample_size * 2u;
            uint8_t *resized =
                (uint8_t *)framework->providers.allocate(buffer_size);
            if (resized == NULL) {
                /* Stock hard-faults here. */
                fault(framework);
                return NULL;
            }
            object->cursor = sensor_stream_resample_copy(
                object->sample_buffer, object->rate, object->cursor, resized,
                rate, object->sample_size);
            framework->providers.free(object->sample_buffer);
            object->sample_buffer = resized;
        }
        object->rate = (uint8_t)rate;
        uint32_t period = SENSOR_STREAM_TICK_HZ / rate;
        sensor_stream_timer_set_period(framework, object->timer, period);
        diagnose(framework, SENSOR_STREAM_MSG_RESET_TIMER, object->name,
                 period);
    }
    return listener;
}

sensor_stream_listener *sensor_stream_register_by_name(
    sensor_stream *framework, const char *stream_name,
    const char *listener_name, sensor_stream_listener_callback callback,
    uint32_t rate, uint8_t mode) {
    if (framework == NULL || stream_name == NULL) {
        return NULL;
    }
    sensor_stream_object *object =
        sensor_stream_object_lookup(framework, stream_name);
    if (object == NULL) {
        diagnose(framework, SENSOR_STREAM_MSG_REGISTER_NOT_FOUND, stream_name,
                 0u);
        return NULL;
    }
    return sensor_stream_listener_register(framework, object, listener_name,
                                           callback, rate, mode);
}

void sensor_stream_listener_unregister(sensor_stream *framework,
                                       const char *stream_name,
                                       sensor_stream_listener *listener) {
    if (framework == NULL || stream_name == NULL) {
        return;
    }
    sensor_stream_object *object =
        sensor_stream_object_lookup(framework, stream_name);
    if (object == NULL) {
        diagnose(framework, SENSOR_STREAM_MSG_UNREGISTER_NOT_FOUND,
                 stream_name, 0u);
        return;
    }
    if (listener == NULL) {
        /* Stock hard-faults here. */
        fault(framework);
        return;
    }
    if (framework->providers.list_first == NULL ||
            framework->providers.list_next == NULL) {
        return;
    }
    sensor_stream_listener *node = (sensor_stream_listener *)
        framework->providers.list_first(&object->listeners);
    for (;;) {
        if (node == NULL) {
            diagnose(framework, SENSOR_STREAM_MSG_LISTENER_NOT_FOUND,
                     listener->name, 0u);
            return;
        }
        if (node == listener) {
            break;
        }
        node = (sensor_stream_listener *)
            framework->providers.list_next(&object->listeners, node);
    }
    if ((object->flags & SENSOR_STREAM_OBJECT_FLAG_DISPATCH_ACTIVE) != 0u) {
        listener->flags =
            (uint16_t)(listener->flags | SENSOR_STREAM_LISTENER_FLAG_DEFERRED);
        object->flags = (uint8_t)(object->flags |
                                  SENSOR_STREAM_OBJECT_FLAG_PENDING_UNREGISTER);
        return;
    }
    if (framework->providers.list_remove == NULL ||
            framework->providers.free == NULL) {
        return;
    }
    framework->providers.list_remove(&object->listeners, listener);
    framework->providers.free(listener);
    stream_after_listener_removal(framework, object);
}

void sensor_stream_timer_dispatch(sensor_stream *framework,
                                  sensor_stream_timer *timer) {
    if (framework == NULL || timer == NULL) {
        return;
    }
    sensor_stream_object *object = (sensor_stream_object *)timer->context;
    if (object == NULL || object->provider == NULL ||
            object->provider->read == NULL || object->sample_buffer == NULL ||
            object->rate == 0u || object->sample_size == 0u) {
        return;
    }
    uint32_t chunk = (uint32_t)object->sample_size * object->rate;
    if (chunk == 0u) {
        return;
    }
    if (framework->providers.list_first == NULL ||
            framework->providers.list_next == NULL) {
        return;
    }
    /* Recovered: a stale cursor (e.g. left over from a pre-shrink buffer) is
     * discarded. */
    if (chunk <= object->cursor) {
        object->cursor = 0u;
    }
    uint32_t cursor = object->cursor;
    uint32_t got = object->provider->read(object->sample_buffer + cursor,
                                          object->sample_size,
                                          object->context);
    if (got != object->sample_size) {
        return;
    }
    bool wrapped;
    uint32_t base;
    if (cursor + object->sample_size != chunk) {
        object->cursor = cursor + object->sample_size;
        base = cursor;
        wrapped = false;
    } else {
        object->cursor = 0u;
        base = chunk - object->sample_size;
        wrapped = true;
    }
    object->flags =
        (uint8_t)(object->flags | SENSOR_STREAM_OBJECT_FLAG_DISPATCH_ACTIVE);
    sensor_stream_listener *node = (sensor_stream_listener *)
        framework->providers.list_first(&object->listeners);
    while (node != NULL) {
        sensor_stream_listener *listener = node;
        if ((listener->flags & SENSOR_STREAM_LISTENER_FLAG_DEFERRED) == 0u &&
                listener->callback != NULL) {
            if (listener->mode == SENSOR_STREAM_MODE_PER_SAMPLE) {
                bool fire = false;
                if (listener->rate == object->rate) {
                    fire = true;
                } else {
                    uint16_t accumulator = (uint16_t)(
                        ((listener->flags >> 1) + listener->rate) & 0x7fffu);
                    listener->flags = (uint16_t)(
                        (listener->flags & SENSOR_STREAM_LISTENER_FLAG_DEFERRED) |
                        (uint16_t)(accumulator << 1));
                    if (object->rate <= accumulator) {
                        accumulator = (uint16_t)(
                            (accumulator - object->rate) & 0x7fffu);
                        listener->flags = (uint16_t)(
                            (listener->flags &
                             SENSOR_STREAM_LISTENER_FLAG_DEFERRED) |
                            (uint16_t)(accumulator << 1));
                        fire = true;
                    }
                }
                if (fire) {
                    listener->callback(listener,
                                       object->sample_buffer + base,
                                       object->sample_size);
                }
            } else if (listener->mode == SENSOR_STREAM_MODE_BATCH && wrapped) {
                if (listener->rate == object->rate) {
                    /* Recovered quirk: the chunk length is truncated to 16
                     * bits. */
                    listener->callback(listener, object->sample_buffer,
                                       chunk & 0xffffu);
                } else {
                    uint32_t copied = sensor_stream_resample_copy(
                        object->sample_buffer, object->rate, chunk,
                        object->sample_buffer + chunk, listener->rate,
                        object->sample_size);
                    listener->callback(listener, object->sample_buffer + chunk,
                                       copied);
                }
            }
        }
        node = (sensor_stream_listener *)
            framework->providers.list_next(&object->listeners, listener);
    }
    object->flags =
        (uint8_t)(object->flags & ~SENSOR_STREAM_OBJECT_FLAG_DISPATCH_ACTIVE);
    if ((object->flags & SENSOR_STREAM_OBJECT_FLAG_PENDING_UNREGISTER) == 0u) {
        return;
    }
    /* Deferred cleanup continuation (stock 0x00089BA8..<0x00089C1E). */
    if (framework->providers.list_remove == NULL ||
            framework->providers.free == NULL) {
        /* Fail explicit: the marks stay set and the removal is retried on
         * the next dispatch. */
        return;
    }
    node = (sensor_stream_listener *)
        framework->providers.list_first(&object->listeners);
    while (node != NULL) {
        sensor_stream_listener *listener = node;
        node = (sensor_stream_listener *)
            framework->providers.list_next(&object->listeners, listener);
        if ((listener->flags & SENSOR_STREAM_LISTENER_FLAG_DEFERRED) != 0u) {
            framework->providers.list_remove(&object->listeners, listener);
            framework->providers.free(listener);
        }
    }
    object->flags = (uint8_t)(object->flags &
                              ~SENSOR_STREAM_OBJECT_FLAG_PENDING_UNREGISTER);
    stream_after_listener_removal(framework, object);
}

static sensor_stream_timer *timer_create(sensor_stream *framework,
                                         sensor_stream_timer_callback callback,
                                         uint32_t period, void *context,
                                         bool back) {
    sensor_stream_timer *timer;
    if (!back) {
        timer = (sensor_stream_timer *)sensor_stream_list_push_front_allocate(
            framework, &framework->housekeeping.timers);
    } else {
        if (framework->providers.list_push_back_allocate == NULL) {
            return NULL;
        }
        timer = (sensor_stream_timer *)
            framework->providers.list_push_back_allocate(
                &framework->housekeeping.timers);
    }
    if (timer == NULL) {
        /* Stock hard-faults here. */
        fault(framework);
        return NULL;
    }
    timer->callback = callback;
    timer->period = period;
    timer->repeat = SENSOR_STREAM_TIMER_REPEAT_FOREVER;
    /* Divergence: the stock node memory is not cleared, so the upper flags
     * bits held heap garbage; the reconstruction zeroes the word before the
     * recovered bit operations. */
    timer->flags = 0u;
    timer->context = context;
    timer->last = sensor_stream_tick_now(framework);
    timer->flags |= SENSOR_STREAM_TIMER_FLAG_ACTIVE;
    framework->housekeeping.created = 1u;
    sensor_stream_housekeeping_kick(framework);
    return timer;
}

sensor_stream_timer *sensor_stream_timer_create_front(
    sensor_stream *framework, sensor_stream_timer_callback callback,
    uint32_t period, void *context) {
    if (framework == NULL) {
        return NULL;
    }
    return timer_create(framework, callback, period, context, false);
}

sensor_stream_timer *sensor_stream_timer_create_back(
    sensor_stream *framework, sensor_stream_timer_callback callback,
    uint32_t period, void *context) {
    if (framework == NULL) {
        return NULL;
    }
    return timer_create(framework, callback, period, context, true);
}

void sensor_stream_timer_release(sensor_stream *framework,
                                 sensor_stream_timer *timer) {
    if (framework == NULL) {
        return;
    }
    if (timer == NULL) {
        /* Stock hard-faults here. */
        fault(framework);
        return;
    }
    if (framework->providers.list_remove == NULL ||
            framework->providers.free == NULL) {
        return;
    }
    framework->providers.list_remove(&framework->housekeeping.timers, timer);
    framework->housekeeping.released = 1u;
    framework->providers.free(timer);
}

void sensor_stream_housekeeping_enable(sensor_stream *framework,
                                       uint32_t enable) {
    if (framework == NULL) {
        return;
    }
    framework->housekeeping.enabled = (uint8_t)enable;
    if (enable != 0u) {
        sensor_stream_housekeeping_kick(framework);
    }
}

bool sensor_stream_timer_expire(sensor_stream *framework,
                                sensor_stream_timer *timer) {
    if (framework == NULL || timer == NULL) {
        return false;
    }
    if ((timer->flags & SENSOR_STREAM_TIMER_FLAG_STOPPED) != 0u) {
        return false;
    }
    bool fired = false;
    if (sensor_stream_timer_remaining(framework, timer) == 0u) {
        uint32_t repeat = timer->repeat;
        if ((int32_t)repeat > 0) {
            timer->repeat = repeat - 1u;
        }
        timer->last = sensor_stream_tick_now(framework);
        if (timer->callback != NULL && repeat != 0u) {
            timer->callback(framework, timer);
        }
        fired = true;
    }
    if (framework->housekeeping.released == 0u && timer->repeat == 0u) {
        if ((timer->flags & SENSOR_STREAM_TIMER_FLAG_ACTIVE) != 0u) {
            sensor_stream_timer_release(framework, timer);
        } else {
            sensor_stream_timer_stop(framework, timer);
        }
    }
    return fired;
}

uint32_t sensor_stream_timer_poll(sensor_stream *framework) {
    if (framework == NULL) {
        return 1u;
    }
    sensor_stream_housekeeping *housekeeping = &framework->housekeeping;
    if (housekeeping->poll_active != 0u) {
        return 1u;
    }
    housekeeping->poll_active = 1u;
    if (housekeeping->enabled == 0u) {
        housekeeping->poll_active = 0u;
        return 1u;
    }
    if (framework->providers.list_first == NULL ||
            framework->providers.list_next == NULL) {
        housekeeping->poll_active = 0u;
        return 1u;
    }
    uint32_t start = sensor_stream_tick_now(framework);
    if (start == 0u) {
        /* Recovered quirk: a zero tick bumps a counter that wraps past 100. */
        housekeeping->zero_tick_counter += 1u;
        if (housekeeping->zero_tick_counter > SENSOR_STREAM_ZERO_TICK_LIMIT) {
            housekeeping->zero_tick_counter = 0u;
        }
    }
    sensor_stream_timer *current;
    bool fired = false;
    do {
        housekeeping->released = 0u;
        housekeeping->created = 0u;
        sensor_stream_timer *node = (sensor_stream_timer *)
            framework->providers.list_first(&housekeeping->timers);
        do {
            current = node;
            if (current == NULL) {
                break;
            }
            node = (sensor_stream_timer *)
                framework->providers.list_next(&housekeeping->timers, current);
            fired = sensor_stream_timer_expire(framework, current);
        } while (!fired ||
                 (housekeeping->created == 0u && housekeeping->released == 0u));
    } while (current != NULL);
    uint32_t minimum = UINT32_C(0xFFFFFFFF);
    sensor_stream_timer *node = (sensor_stream_timer *)
        framework->providers.list_first(&housekeeping->timers);
    while (node != NULL) {
        if ((node->flags & SENSOR_STREAM_TIMER_FLAG_STOPPED) == 0u) {
            uint32_t remaining = sensor_stream_timer_remaining(framework, node);
            if (remaining < minimum) {
                minimum = remaining;
            }
        }
        node = (sensor_stream_timer *)
            framework->providers.list_next(&housekeeping->timers, node);
    }
    housekeeping->drift_accumulator +=
        sensor_stream_ticks_elapsed(framework, start);
    uint32_t span =
        sensor_stream_ticks_elapsed(framework, housekeeping->drift_mark);
    if (span > SENSOR_STREAM_DRIFT_WINDOW) {
        uint32_t percent = housekeeping->drift_accumulator * 100u / span;
        uint8_t correction;
        if ((percent & 0xffu) < 101u) {
            /* Recovered percent-encoded 'd' (100) correction byte. */
            correction = (uint8_t)(100u - (uint8_t)percent);
        } else {
            correction = 0u;
        }
        housekeeping->drift_correction = correction;
        housekeeping->drift_accumulator = 0u;
        housekeeping->drift_mark = sensor_stream_tick_now(framework);
    }
    housekeeping->next_wakeup = minimum;
    housekeeping->poll_active = 0u;
    return minimum;
}

void sensor_stream_housekeeping_kick(sensor_stream *framework) {
    if (framework == NULL) {
        return;
    }
    framework->housekeeping.next_wakeup = 0u;
    if (framework->housekeeping.wake != NULL) {
        framework->housekeeping.wake(framework->housekeeping.wake_context);
    }
}

void sensor_stream_timer_stop(sensor_stream *framework,
                              sensor_stream_timer *timer) {
    if (framework == NULL) {
        return;
    }
    if (timer == NULL) {
        /* Stock hard-faults here. */
        fault(framework);
        return;
    }
    timer->flags |= SENSOR_STREAM_TIMER_FLAG_STOPPED;
}

void sensor_stream_object_set_back_insert(sensor_stream *framework,
                                          sensor_stream_object *object,
                                          uint32_t value) {
    if (framework == NULL) {
        return;
    }
    if (object != NULL) {
        object->flags = (uint8_t)((object->flags & 0xFEu) | (value & 1u));
    }
}

void sensor_stream_timer_set_period(sensor_stream *framework,
                                    sensor_stream_timer *timer,
                                    uint32_t period) {
    if (framework == NULL) {
        return;
    }
    if (timer == NULL) {
        /* Stock hard-faults here. */
        fault(framework);
        return;
    }
    timer->period = period;
}

uint32_t sensor_stream_timer_remaining(sensor_stream *framework,
                                       const sensor_stream_timer *timer) {
    if (framework == NULL || timer == NULL) {
        return 0u;
    }
    uint32_t elapsed = sensor_stream_ticks_elapsed(framework, timer->last);
    if (timer->period <= elapsed) {
        return 0u;
    }
    return timer->period - elapsed;
}

uint32_t sensor_stream_ticks_elapsed(sensor_stream *framework, uint32_t then) {
    if (framework == NULL) {
        return 0u;
    }
    return sensor_stream_tick_now(framework) - then;
}

uint32_t sensor_stream_tick_now(sensor_stream *framework) {
    if (framework == NULL) {
        return 0u;
    }
    if (framework->tick_hook != NULL) {
        return framework->tick_hook();
    }
    if (framework->providers.tick_fallback != NULL) {
        return framework->providers.tick_fallback();
    }
    return 0u;
}

void sensor_stream_set_tick_hook(sensor_stream *framework,
                                 sensor_stream_tick_fn hook) {
    if (framework == NULL) {
        return;
    }
    framework->tick_hook = hook;
}

void sensor_stream_set_wake_callback(sensor_stream *framework,
                                     sensor_stream_wake_fn wake,
                                     void *context) {
    if (framework == NULL) {
        return;
    }
    framework->housekeeping.wake = wake;
    framework->housekeeping.wake_context = context;
}

void sensor_stream_bind_singleton_providers(
    sensor_stream *framework, const sensor_stream_provider_ops *acc_provider,
    const sensor_stream_provider_ops *temp_provider) {
    if (framework == NULL) {
        return;
    }
    framework->acc_provider = acc_provider;
    framework->temp_provider = temp_provider;
}

/* Stock 0x0008A558: the keep-alive timer callback is a bare `bx lr`. */
static void keepalive_nop(sensor_stream *framework,
                          sensor_stream_timer *timer) {
    (void)framework;
    (void)timer;
}

uint32_t sensor_stream_initialize(sensor_stream *framework,
                                  const sensor_stream_providers *providers) {
    if (framework == NULL) {
        return SENSOR_STREAM_STATUS_BAD_ARGUMENT;
    }
    zero_bytes(framework, sizeof(*framework));
    if (providers != NULL) {
        framework->providers = *providers;
    }
    /* Recovered 0x0008A55C body: timer-list descriptor init, enable with
     * kick, and the 1000-tick keep-alive timer. */
    sensor_stream_list_descriptor_init(&framework->housekeeping.timers,
                                       TIMER_LINK_PAYLOAD);
    sensor_stream_housekeeping_enable(framework, 1u);
    sensor_stream_timer *keepalive = sensor_stream_timer_create_front(
        framework, keepalive_nop, SENSOR_STREAM_KEEPALIVE_PERIOD, NULL);
    if (keepalive == NULL) {
        return SENSOR_STREAM_STATUS_BAD_ARGUMENT;
    }
    return SENSOR_STREAM_STATUS_OK;
}

sensor_stream_object *sensor_stream_acc_object_create(
    sensor_stream *framework) {
    if (framework == NULL || framework->acc_provider == NULL) {
        return NULL;
    }
    /* Recovered fixed configuration: name "acc" (pooled bytes at
     * 0x00089D98), sample size 0xBC, const vtable 0x0009A590, no context. */
    return sensor_stream_object_create(framework, "acc", 0xBCu,
                                       framework->acc_provider, NULL);
}

sensor_stream_object *sensor_stream_temp_object_create(
    sensor_stream *framework) {
    if (framework == NULL || framework->temp_provider == NULL) {
        return NULL;
    }
    /* Recovered fixed configuration: name "temp" (pooled bytes at
     * 0x0008A1BC), sample size 2, const vtable 0x0009A5A8, no context. */
    return sensor_stream_object_create(framework, "temp", 2u,
                                       framework->temp_provider, NULL);
}

void sensor_stream_sink_store4(sensor_stream *framework, uint32_t word0,
                               uint32_t word1, uint32_t word2,
                               uint32_t word3) {
    if (framework == NULL) {
        return;
    }
    framework->sinks.descriptor4[0] = word0;
    framework->sinks.descriptor4[1] = word1;
    framework->sinks.descriptor4[2] = word2;
    framework->sinks.descriptor4[3] = word3;
}

void sensor_stream_sink_store6(sensor_stream *framework, uint32_t word0,
                               uint32_t word1, uint32_t word2, uint32_t word3,
                               uint32_t word4, uint32_t word5) {
    if (framework == NULL) {
        return;
    }
    framework->sinks.descriptor6[0] = word0;
    framework->sinks.descriptor6[1] = word1;
    framework->sinks.descriptor6[2] = word2;
    framework->sinks.descriptor6[3] = word3;
    framework->sinks.descriptor6[4] = word4;
    framework->sinks.descriptor6[5] = word5;
}

void sensor_stream_sink_store6_sign_extended(
    sensor_stream *framework, uint32_t word0, uint32_t word1, uint32_t word2,
    uint32_t word3, uint32_t word4, uint32_t word5) {
    if (framework == NULL) {
        return;
    }
    framework->sinks.descriptor6s[0] = word0;
    framework->sinks.descriptor6s[1] = word1;
    framework->sinks.descriptor6s[2] = word2;
    framework->sinks.descriptor6s[3] = (uint32_t)(int32_t)(int8_t)word3;
    framework->sinks.descriptor6s[4] = word4;
    framework->sinks.descriptor6s[5] = word5;
}

static void store_clamped_triple(int32_t *destination, const int32_t *first,
                                 const int32_t *second, const int32_t *third) {
    destination[0] = *first < 0 ? 0 : *first;
    destination[1] = *second < 0 ? 0 : *second;
    destination[2] = *third < 0 ? 0 : *third;
}

void sensor_stream_sink_triple_clamped_primary(sensor_stream *framework,
                                               const int32_t *first,
                                               const int32_t *second,
                                               const int32_t *third) {
    if (framework == NULL || first == NULL || second == NULL ||
            third == NULL) {
        return;
    }
    store_clamped_triple(framework->sinks.clamped_primary, first, second,
                         third);
}

void sensor_stream_sink_triple_clamped_secondary(sensor_stream *framework,
                                                 const int32_t *first,
                                                 const int32_t *second,
                                                 const int32_t *third) {
    if (framework == NULL || first == NULL || second == NULL ||
            third == NULL) {
        return;
    }
    store_clamped_triple(framework->sinks.clamped_secondary, first, second,
                         third);
}
