#ifndef OPENR1_R1_EVENT_H
#define OPENR1_R1_EVENT_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "openr1/r1_protocol.h"

#define R1_NORMAL_QUEUE_CAPACITY 20u
#define R1_EUS_QUEUE_CAPACITY 50u
#define R1_HVN_CREDIT_MAX 4u
#define R1_TX_ENQUEUE_WAIT_TICKS 100u
#define R1_EUS_CREDIT_WAIT_TICKS 200u
#define R1_EUS_RESOURCE_RETRY_TICKS 1000u
#define R1_DELAYED_EVENT_CAPACITY 64u
#define R1_DELAYED_EVENT_ELAPSED_TAG UINT32_C(0xff000000)
#define R1_DELAYED_EVENT_ELAPSED_MASK UINT32_C(0x00ffffff)

typedef struct {
    uint16_t connection;
    uint8_t channel;
    uint8_t bytes[R1_BLE_VALUE_MAX];
    size_t length;
    uint8_t resource_retries;
    bool credit_wait_started;
    bool resource_retry_pending;
    uint32_t deadline_tick;
} r1_tx_event;

typedef struct {
    r1_tx_event entries[R1_EUS_QUEUE_CAPACITY];
    size_t head;
    size_t count;
    size_t capacity;
} r1_event_queue;

typedef struct {
    r1_event_queue normal;
    r1_event_queue eus;
    uint8_t hvn_credits;
} r1_event_plane;

typedef struct {
    uint32_t event;
    uint32_t context;
    uint32_t remaining_milliseconds;
} r1_delayed_event_slot;

typedef struct {
    r1_delayed_event_slot slots[R1_DELAYED_EVENT_CAPACITY];
    uint32_t last_timer_delay_milliseconds;
    uint32_t last_timer_start_milliseconds;
} r1_delayed_event_state;

typedef struct {
    uint32_t event;
    uint32_t context;
} r1_delayed_event_due;

typedef struct {
    r1_delayed_event_due due[R1_DELAYED_EVENT_CAPACITY];
    size_t due_count;
    uint32_t elapsed_milliseconds;
    uint32_t next_delay_milliseconds;
    bool elapsed_override_used;
    bool timer_start_requested;
    bool stock_empty_reload_quirk;
    bool stock_int32_max_suppression_quirk;
} r1_delayed_event_step_result;

typedef enum {
    R1_DELAYED_EVENT_IMMEDIATE = 0,
    R1_DELAYED_EVENT_SCHEDULED,
    R1_DELAYED_EVENT_TABLE_FULL
} r1_delayed_event_schedule_action;

typedef struct {
    r1_delayed_event_schedule_action action;
    size_t slot_index;
    uint32_t elapsed_milliseconds;
    bool immediate_push_requested;
    bool worker_wakeup_requested;
    r1_delayed_event_step_result timer_step;
} r1_delayed_event_schedule_result;

void r1_event_plane_initialize(r1_event_plane *plane);
r1_error r1_event_enqueue(r1_event_plane *plane, bool eus, const r1_tx_event *event);
bool r1_event_take(r1_event_plane *plane, bool eus, r1_tx_event *event);
bool r1_event_peek(const r1_event_plane *plane, bool eus, r1_tx_event *event);
r1_tx_event *r1_event_front(r1_event_plane *plane, bool eus);
bool r1_event_drop(r1_event_plane *plane, bool eus);
void r1_event_remove_connection(r1_event_plane *plane, uint16_t connection);
bool r1_event_consume_credit(r1_event_plane *plane);
void r1_event_complete(r1_event_plane *plane, uint8_t completed);
void r1_event_disconnect(r1_event_plane *plane);
r1_error r1_delayed_event_timer_step(
    r1_delayed_event_state *state, uint32_t callback_argument,
    uint32_t kernel_tick, r1_delayed_event_step_result *result);
r1_error r1_delayed_event_schedule(
    r1_delayed_event_state *state, uint32_t event, uint32_t context,
    uint32_t delay_milliseconds, uint32_t kernel_tick,
    r1_delayed_event_schedule_result *result);

#endif
