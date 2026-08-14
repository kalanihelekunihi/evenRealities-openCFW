#include "openr1/r1_event_bus.h"

void r1_event_bus_reset(r1_event_bus *bus) {
    if (bus == NULL) {
        return;
    }
    for (size_t slot = 0u; slot < R1_EVENT_BUS_SLOT_COUNT; ++slot) {
        for (size_t index = 0u; index < R1_EVENT_BUS_SLOT_CAPACITY; ++index) {
            bus->listeners[slot][index] = NULL;
            bus->contexts[slot][index] = NULL;
        }
        bus->counts[slot] = 0u;
    }
    bus->enqueue = NULL;
    bus->enqueue_context = NULL;
}

r1_error r1_event_bus_bind_enqueue(
    r1_event_bus *bus, r1_event_bus_enqueue_sink sink, void *context) {
    if (bus == NULL || sink == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    bus->enqueue = sink;
    bus->enqueue_context = context;
    return R1_OK;
}

bool r1_event_bus_classify(uint16_t event_id, r1_event_bus_window *window) {
    r1_event_bus_window classified;
    if (event_id >= R1_EVENT_BUS_SENSOR_WINDOW_FIRST &&
        event_id <= R1_EVENT_BUS_SENSOR_WINDOW_LAST) {
        classified = R1_EVENT_BUS_WINDOW_SENSOR;
    }
    else if (event_id >= R1_EVENT_BUS_SYSTEM_WINDOW_FIRST &&
             event_id <= R1_EVENT_BUS_SYSTEM_WINDOW_LAST) {
        classified = R1_EVENT_BUS_WINDOW_SYSTEM;
    }
    else if (event_id >= R1_EVENT_BUS_STORAGE_WINDOW_FIRST &&
             event_id <= R1_EVENT_BUS_STORAGE_WINDOW_LAST) {
        classified = R1_EVENT_BUS_WINDOW_STORAGE;
    }
    else {
        return false;
    }
    if (window != NULL) {
        *window = classified;
    }
    return true;
}

r1_error r1_event_bus_subscribe(
    r1_event_bus *bus, uint8_t slot,
    r1_event_bus_listener listener, void *context) {
    if (bus == NULL || listener == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (slot >= R1_EVENT_BUS_SLOT_COUNT) {
        return R1_ERROR_ARGUMENT;
    }
    const size_t count = bus->counts[slot];
    for (size_t index = 0u; index < count; ++index) {
        if (bus->listeners[slot][index] == listener) {
            return R1_ERROR_STATE;
        }
    }
    if (count >= R1_EVENT_BUS_SLOT_CAPACITY) {
        return R1_ERROR_CAPACITY;
    }
    bus->listeners[slot][count] = listener;
    bus->contexts[slot][count] = context;
    bus->counts[slot] = count + 1u;
    return R1_OK;
}

size_t r1_event_bus_subscriber_count(const r1_event_bus *bus, uint8_t slot) {
    if (bus == NULL || slot >= R1_EVENT_BUS_SLOT_COUNT) {
        return 0u;
    }
    return bus->counts[slot];
}

r1_error r1_event_bus_multicast(
    const r1_event_bus *bus, uint8_t slot,
    const uint8_t *payload, size_t length, size_t *delivered) {
    if (bus == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (slot >= R1_EVENT_BUS_SLOT_COUNT) {
        return R1_ERROR_ARGUMENT;
    }
    if (payload == NULL && length != 0u) {
        return R1_ERROR_ARGUMENT;
    }
    const size_t count = bus->counts[slot];
    for (size_t index = 0u; index < count; ++index) {
        bus->listeners[slot][index](payload, length, bus->contexts[slot][index]);
    }
    if (delivered != NULL) {
        *delivered = count;
    }
    return R1_OK;
}

r1_error r1_event_bus_publish(
    r1_event_bus *bus, uint16_t event_id,
    const uint8_t *payload, size_t length) {
    if (bus == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    r1_event_bus_window window;
    if (!r1_event_bus_classify(event_id, &window)) {
        return R1_ERROR_ARGUMENT;
    }
    if (payload == NULL && length != 0u) {
        return R1_ERROR_ARGUMENT;
    }
    if (length > R1_EVENT_BUS_PAYLOAD_LIMIT) {
        return R1_ERROR_LENGTH;
    }
    if (bus->enqueue == NULL) {
        return R1_ERROR_UNSUPPORTED;
    }
    for (size_t index = 0u; index < length; ++index) {
        bus->staging[index] = payload[index];
    }
    const r1_event_bus_event event = {
        event_id, window, length == 0u ? NULL : bus->staging, length,
    };
    if (!bus->enqueue(&event, bus->enqueue_context)) {
        return R1_ERROR_CAPACITY;
    }
    return R1_OK;
}
