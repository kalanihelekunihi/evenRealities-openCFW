#ifndef OPENR1_CONNECTION_CONTROL_H
#define OPENR1_CONNECTION_CONTROL_H

#include <stdint.h>

#include "openr1/r1_peer_target.h"

/*
 * advStart two-target connection-control composition (R1-191,
 * docs/correlation/CONNECTION-CONTROL-CORRELATION.md).
 *
 * openr1_connection_control_adv_start composes the recovered event-0x200
 * consumer policy over production providers: both targets persist at kv
 * dev_info offsets 8/14 through r1_kv_store, the connected glasses peer
 * address comes from the GAP connected-event cache in openr1_bae8, a
 * mismatching peer is scheduled for delayed disconnect through
 * r1_delayed_event_schedule, and the role-aware advertising action drives
 * the Nordic ble_advertising provider.
 *
 * Fail-closed posture is unchanged: the externally callable advStart
 * command stays REFUSED in the normal dispatcher, so nothing calls this
 * entry point on target today.  It is retained in the image so the
 * composition is bound and reviewable; unrefusing requires end-to-end
 * product authorization and owned-hardware validation.
 *
 * The caller must not be the SoftDevice event thread: the kv commit
 * mutates flash, which openr1_storage rejects there.  The delayed-event
 * timer driver is now bound: a CMSIS one-shot timer steps the portable
 * r1_delayed_event_state and fires the scheduled disconnect through
 * sd_ble_gap_disconnect.  One binding stays deliberately unbound rather
 * than inventing behavior: command-to-composition byte order
 * reconciliation with the first-party sender (an e2e concern).
 */

uint32_t openr1_connection_control_adv_start(
    const uint8_t first_target[R1_PEER_ADDRESS_SIZE],
    const uint8_t second_target[R1_PEER_ADDRESS_SIZE]);
uint32_t openr1_connection_control_last_error(void);

#endif
