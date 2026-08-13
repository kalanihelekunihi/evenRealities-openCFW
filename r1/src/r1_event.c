#include "openr1/r1_event.h"

static void initialize_queue(r1_event_queue *queue, size_t capacity) {
    queue->head = 0u;
    queue->count = 0u;
    queue->capacity = capacity;
}

void r1_event_plane_initialize(r1_event_plane *plane) {
    if (plane == NULL) {
        return;
    }
    initialize_queue(&plane->normal, R1_NORMAL_QUEUE_CAPACITY);
    initialize_queue(&plane->eus, R1_EUS_QUEUE_CAPACITY);
    plane->hvn_credits = R1_HVN_CREDIT_MAX;
}

r1_error r1_event_enqueue(r1_event_plane *plane, bool eus, const r1_tx_event *event) {
    if (plane == NULL || event == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (event->length > R1_BLE_VALUE_MAX) {
        return R1_ERROR_LENGTH;
    }
    r1_event_queue *queue = eus ? &plane->eus : &plane->normal;
    if (queue->count >= queue->capacity) {
        return R1_ERROR_CAPACITY;
    }
    const size_t index = (queue->head + queue->count) % queue->capacity;
    queue->entries[index] = *event;
    queue->count += 1u;
    return R1_OK;
}

bool r1_event_take(r1_event_plane *plane, bool eus, r1_tx_event *event) {
    if (plane == NULL || event == NULL) {
        return false;
    }
    r1_event_queue *queue = eus ? &plane->eus : &plane->normal;
    if (queue->count == 0u) {
        return false;
    }
    *event = queue->entries[queue->head];
    queue->head = (queue->head + 1u) % queue->capacity;
    queue->count -= 1u;
    return true;
}

bool r1_event_peek(const r1_event_plane *plane, bool eus, r1_tx_event *event) {
    if (plane == NULL || event == NULL) {
        return false;
    }
    const r1_event_queue *queue = eus ? &plane->eus : &plane->normal;
    if (queue->count == 0u) {
        return false;
    }
    *event = queue->entries[queue->head];
    return true;
}

r1_tx_event *r1_event_front(r1_event_plane *plane, bool eus) {
    if (plane == NULL) {
        return NULL;
    }
    r1_event_queue *queue = eus ? &plane->eus : &plane->normal;
    if (queue->count == 0u) {
        return NULL;
    }
    return &queue->entries[queue->head];
}

bool r1_event_drop(r1_event_plane *plane, bool eus) {
    if (plane == NULL) {
        return false;
    }
    r1_event_queue *queue = eus ? &plane->eus : &plane->normal;
    if (queue->count == 0u) {
        return false;
    }
    queue->head = (queue->head + 1u) % queue->capacity;
    queue->count -= 1u;
    return true;
}

static void remove_from_queue(r1_event_queue *queue, uint16_t connection) {
    size_t kept = 0u;
    const size_t original = queue->count;
    for (size_t offset = 0u; offset < original; ++offset) {
        const size_t source = (queue->head + offset) % queue->capacity;
        if (queue->entries[source].connection == connection) {
            continue;
        }
        const size_t destination = (queue->head + kept) % queue->capacity;
        if (destination != source) {
            queue->entries[destination] = queue->entries[source];
        }
        kept += 1u;
    }
    queue->count = kept;
}

void r1_event_remove_connection(r1_event_plane *plane, uint16_t connection) {
    if (plane == NULL) {
        return;
    }
    remove_from_queue(&plane->normal, connection);
    remove_from_queue(&plane->eus, connection);
}

bool r1_event_consume_credit(r1_event_plane *plane) {
    if (plane == NULL || plane->hvn_credits == 0u) {
        return false;
    }
    plane->hvn_credits -= 1u;
    return true;
}

void r1_event_complete(r1_event_plane *plane, uint8_t completed) {
    if (plane == NULL) {
        return;
    }
    const uint16_t sum = (uint16_t)plane->hvn_credits + completed;
    plane->hvn_credits = sum > R1_HVN_CREDIT_MAX
        ? R1_HVN_CREDIT_MAX : (uint8_t)sum;
}

void r1_event_disconnect(r1_event_plane *plane) {
    r1_event_plane_initialize(plane);
}

r1_error r1_delayed_event_timer_step(
    r1_delayed_event_state *state, uint32_t callback_argument,
    uint32_t kernel_tick, r1_delayed_event_step_result *result) {
    if (state == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *result = (r1_delayed_event_step_result){0};
    result->elapsed_override_used =
        (callback_argument >> 24u) == UINT32_C(0xff);
    result->elapsed_milliseconds = result->elapsed_override_used
        ? callback_argument & R1_DELAYED_EVENT_ELAPSED_MASK
        : state->last_timer_delay_milliseconds;

    for (size_t index = 0u; index < R1_DELAYED_EVENT_CAPACITY; ++index) {
        r1_delayed_event_slot *slot = &state->slots[index];
        if (slot->event == 0u) {
            continue;
        }
        slot->remaining_milliseconds =
            slot->remaining_milliseconds > result->elapsed_milliseconds
            ? slot->remaining_milliseconds - result->elapsed_milliseconds
            : 0u;
        if (slot->remaining_milliseconds == 0u) {
            result->due[result->due_count++] =
                (r1_delayed_event_due){slot->event, slot->context};
            slot->event = 0u;
        }
    }

    uint32_t next_delay = UINT32_MAX;
    bool has_active = false;
    for (size_t index = 0u; index < R1_DELAYED_EVENT_CAPACITY; ++index) {
        const r1_delayed_event_slot *slot = &state->slots[index];
        if (slot->event != 0u) {
            has_active = true;
            if (slot->remaining_milliseconds < next_delay) {
                next_delay = slot->remaining_milliseconds;
            }
        }
    }
    result->next_delay_milliseconds = next_delay;

    /* Preserve and label both recovered comparisons. An empty table leaves
     * UINT32_MAX, which passes the stock INT32_MAX sentinel test and requests
     * a maximum-delay timer. Conversely an exact INT32_MAX delay is skipped. */
    result->stock_empty_reload_quirk = !has_active;
    result->stock_int32_max_suppression_quirk =
        has_active && next_delay == (uint32_t)INT32_MAX;
    if (next_delay != (uint32_t)INT32_MAX && next_delay != 0u) {
        state->last_timer_delay_milliseconds = next_delay;
        state->last_timer_start_milliseconds =
            (kernel_tick * UINT32_C(1000)) >> 10u;
        result->timer_start_requested = true;
    }
    return R1_OK;
}

r1_error r1_delayed_event_schedule(
    r1_delayed_event_state *state, uint32_t event, uint32_t context,
    uint32_t delay_milliseconds, uint32_t kernel_tick,
    r1_delayed_event_schedule_result *result) {
    if (state == NULL || result == NULL || event == 0u) {
        return R1_ERROR_ARGUMENT;
    }
    *result = (r1_delayed_event_schedule_result){0};
    if (delay_milliseconds < 2u) {
        result->action = R1_DELAYED_EVENT_IMMEDIATE;
        result->immediate_push_requested = true;
        return R1_OK;
    }

    size_t slot_index = R1_DELAYED_EVENT_CAPACITY;
    for (size_t index = 0u; index < R1_DELAYED_EVENT_CAPACITY; ++index) {
        if (state->slots[index].event == 0u) {
            slot_index = index;
            break;
        }
    }
    if (slot_index == R1_DELAYED_EVENT_CAPACITY) {
        result->action = R1_DELAYED_EVENT_TABLE_FULL;
        result->slot_index = R1_DELAYED_EVENT_CAPACITY;
        return R1_ERROR_CAPACITY;
    }

    const uint32_t now_milliseconds =
        (kernel_tick * UINT32_C(1000)) >> 10u;
    const uint32_t elapsed = now_milliseconds
        - state->last_timer_start_milliseconds;
    state->slots[slot_index] = (r1_delayed_event_slot){
        event, context, delay_milliseconds + elapsed,
    };
    result->action = R1_DELAYED_EVENT_SCHEDULED;
    result->slot_index = slot_index;
    result->elapsed_milliseconds = elapsed;
    result->worker_wakeup_requested = true;
    return r1_delayed_event_timer_step(
        state, R1_DELAYED_EVENT_ELAPSED_TAG
            | (elapsed & R1_DELAYED_EVENT_ELAPSED_MASK),
        kernel_tick, &result->timer_step);
}

r1_error r1_delayed_event_cancel(
    r1_delayed_event_state *state, uint32_t event, uint32_t context,
    uint32_t kernel_tick, r1_delayed_event_cancel_result *result) {
    if (state == NULL || result == NULL || event == 0u) {
        return R1_ERROR_ARGUMENT;
    }
    *result = (r1_delayed_event_cancel_result){0};
    for (size_t index = 0u; index < R1_DELAYED_EVENT_CAPACITY; ++index) {
        r1_delayed_event_slot *slot = &state->slots[index];
        if (slot->event == event &&
            (context == 0u || slot->context == context)) {
            slot->event = 0u;
            result->removed_count += 1u;
        }
    }
    if (result->removed_count == 0u) {
        return R1_OK;
    }
    const uint32_t now_milliseconds =
        (kernel_tick * UINT32_C(1000)) >> 10u;
    result->elapsed_milliseconds =
        now_milliseconds - state->last_timer_start_milliseconds;
    result->worker_wakeup_requested = true;
    return r1_delayed_event_timer_step(
        state, R1_DELAYED_EVENT_ELAPSED_TAG |
            (result->elapsed_milliseconds & R1_DELAYED_EVENT_ELAPSED_MASK),
        kernel_tick, &result->timer_step);
}
