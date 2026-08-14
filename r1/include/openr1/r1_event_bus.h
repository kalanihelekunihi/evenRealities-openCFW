#ifndef OPENR1_R1_EVENT_BUS_H
#define OPENR1_R1_EVENT_BUS_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "openr1/r1_protocol.h"

/*
 * R1 private event bus (clean-room behavioral implementation).
 *
 * The stock publisher (`0x0008D8FC`, 202 bytes), subscriber multicast
 * (`0x0008B028`, 202 bytes), and subscription insert (`0x0008AF8C`, 146
 * bytes) are classified `r1_product_specific` / `clean_room_behavior_only`.
 * The pinned contract is documented in
 * docs/correlation/EVENT-BUS-CORRELATION.md:
 *
 * - a five-slot subscriber table (stock RAM `0x20015708`), append at tail,
 *   duplicate callback in the same slot rejected;
 * - three event-id windows with first-match-wins compare bases
 *   `0x0001...0x0FFF` (sensor), `0x1000...0x1FFF` (system), and
 *   `0x2000...0x2FFF` (storage; the third stock compare accepts any id
 *   below `0x3000`);
 * - inline payloads up to 4 bytes and bounded copies for larger ones,
 *   handed to an external queue as a 12-byte record in the stock image.
 *
 * The module is pure: no heap, no RTOS objects, no hardware access, and no
 * hidden globals.  The stock queue handoff is an injected sink and the
 * stock mutex (`0x20006794`) is the platform's concern; host tests drive
 * the module single-threaded.  Stock allocation-failure hangs and the
 * multicast's missing slot bounds check are replaced by explicit status
 * returns.
 */

#define R1_EVENT_BUS_SLOT_COUNT 5u
#define R1_EVENT_BUS_SLOT_CAPACITY 8u
#define R1_EVENT_BUS_INLINE_PAYLOAD_LIMIT 4u
#define R1_EVENT_BUS_PAYLOAD_LIMIT 128u

#define R1_EVENT_BUS_SENSOR_WINDOW_FIRST 0x0001u
#define R1_EVENT_BUS_SENSOR_WINDOW_LAST 0x0fffu
#define R1_EVENT_BUS_SYSTEM_WINDOW_FIRST 0x1000u
#define R1_EVENT_BUS_SYSTEM_WINDOW_LAST 0x1fffu
#define R1_EVENT_BUS_STORAGE_WINDOW_FIRST 0x2000u
#define R1_EVENT_BUS_STORAGE_WINDOW_LAST 0x2fffu

typedef enum {
    R1_EVENT_BUS_WINDOW_SENSOR = 0,
    R1_EVENT_BUS_WINDOW_SYSTEM,
    R1_EVENT_BUS_WINDOW_STORAGE
} r1_event_bus_window;

/* Clean-room listener shape: the stock callback receives only the payload
 * pointer and relies on implicit per-event length knowledge; the portable
 * bus passes the length explicitly along with the subscriber's opaque
 * owner context. */
typedef void (*r1_event_bus_listener)(
    const uint8_t *payload, size_t length, void *context);

typedef struct {
    uint16_t event_id;
    r1_event_bus_window window;
    const uint8_t *payload;
    size_t length;
} r1_event_bus_event;

/* Queue-handoff seam.  Returns true when the event record was accepted,
 * modelling the stock per-window RTOS queue send; the payload pointer is
 * valid only for the duration of the call. */
typedef bool (*r1_event_bus_enqueue_sink)(
    const r1_event_bus_event *event, void *context);

typedef struct {
    r1_event_bus_listener
        listeners[R1_EVENT_BUS_SLOT_COUNT][R1_EVENT_BUS_SLOT_CAPACITY];
    void *contexts[R1_EVENT_BUS_SLOT_COUNT][R1_EVENT_BUS_SLOT_CAPACITY];
    size_t counts[R1_EVENT_BUS_SLOT_COUNT];
    r1_event_bus_enqueue_sink enqueue;
    void *enqueue_context;
    uint8_t staging[R1_EVENT_BUS_PAYLOAD_LIMIT];
} r1_event_bus;

/* Returns the bus to its power-on state (the stock table is zero-filled
 * BSS): no subscribers and no queue binding. */
void r1_event_bus_reset(r1_event_bus *bus);

/* Binds the queue handoff used by r1_event_bus_publish. */
r1_error r1_event_bus_bind_enqueue(
    r1_event_bus *bus, r1_event_bus_enqueue_sink sink, void *context);

/* Classifies an event id into its window.  Returns false for id zero and
 * ids at or above 0x3000, which the stock publisher silently drops. */
bool r1_event_bus_classify(uint16_t event_id, r1_event_bus_window *window);

/* Appends a listener to a slot in registration order.  A callback already
 * present in the same slot yields R1_ERROR_STATE (the stock insert returns
 * 0); a full slot yields R1_ERROR_CAPACITY instead of the stock
 * allocation-failure halt. */
r1_error r1_event_bus_subscribe(
    r1_event_bus *bus, uint8_t slot,
    r1_event_bus_listener listener, void *context);

size_t r1_event_bus_subscriber_count(const r1_event_bus *bus, uint8_t slot);

/* Invokes a slot's listeners in registration order.  An empty slot is a
 * successful zero-delivery (the stock multicast returns 0); `delivered`
 * may be NULL. */
r1_error r1_event_bus_multicast(
    const r1_event_bus *bus, uint8_t slot,
    const uint8_t *payload, size_t length, size_t *delivered);

/* Validates the event-id window and payload, stages a bounded copy, and
 * hands the event to the bound queue sink.  Payloads above
 * R1_EVENT_BUS_PAYLOAD_LIMIT yield R1_ERROR_LENGTH (the stock bound is
 * heap availability); a missing sink yields R1_ERROR_UNSUPPORTED and a
 * rejecting sink yields R1_ERROR_CAPACITY, matching the stock 0 return. */
r1_error r1_event_bus_publish(
    r1_event_bus *bus, uint16_t event_id,
    const uint8_t *payload, size_t length);

#endif
