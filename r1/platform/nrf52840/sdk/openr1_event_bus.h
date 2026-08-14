#ifndef OPENR1_NRF52840_SDK_EVENT_BUS_H
#define OPENR1_NRF52840_SDK_EVENT_BUS_H

#include "nrf.h"
#include "app_error.h"

#include "openr1/r1_event_bus.h"

/*
 * Platform queue sink and consumer for the R1 private event bus
 * (docs/correlation/EVENT-BUS-CORRELATION.md).
 *
 * openr1_event_bus_bind() recreates the stock queue handoff as bounded
 * CMSIS-FreeRTOS glue: one message queue per event-id window (sensor
 * 0x0001...0x0FFF, system 0x1000...0x1FFF, storage 0x2000...0x2FFF) carrying
 * the recovered 12-byte record {UInt32 event id, UInt32 payload length,
 * 4-byte inline payload or heap pointer}, plus one consumer thread that
 * drains the queues and delivers each record through
 * r1_event_bus_multicast.
 *
 * Fail-explicit posture: the sink never blocks the caller (queue put with a
 * zero timeout), so a full queue frees any heap copy and surfaces the stock
 * 0 return as R1_ERROR_CAPACITY from r1_event_bus_publish.  A bind failure
 * leaves the sink unbound, so publish keeps returning R1_ERROR_UNSUPPORTED.
 *
 * Documented divergence: the stock consumer-side per-id dispatch table
 * (0x0008D888) and the two-entry cross-context republish routing table are
 * not recovered (they depend on RTOS task identity and a mutable routing
 * table), so the consumer delivers same-context to every populated slot in
 * ascending order instead of republishing cross-context.
 */

/* Binds the three per-window queues and the consumer thread to `bus` via
 * r1_event_bus_bind_enqueue.  On NRF_SUCCESS the bus accepts publishes; on
 * any failure the sink stays unbound.  Binding a second bus is refused. */
ret_code_t openr1_event_bus_bind(r1_event_bus *bus);

/* Sticky first consumer-side failure; zero when none has been recorded. */
uint32_t openr1_event_bus_last_error(void);

#endif
