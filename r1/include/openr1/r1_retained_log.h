#ifndef OPENR1_R1_RETAINED_LOG_H
#define OPENR1_R1_RETAINED_LOG_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "openr1/r1_protocol.h"

#define R1_RETAINED_LOG_BYTES 3008u
#define R1_RETAINED_LOG_APPEND_LIMIT 3007u
#define R1_RETAINED_LOG_PAYLOAD_LIMIT 3006u

typedef r1_error (*r1_retained_log_first_use_fn)(void *context);
typedef r1_error (*r1_retained_log_write_fn)(
    void *context, const uint8_t *bytes, size_t length);

typedef struct {
    bool initialized;
    uint16_t length;
    uint8_t bytes[R1_RETAINED_LOG_BYTES];
} r1_retained_log;

typedef struct {
    bool initialized_now;
    bool appended;
    bool truncated;
    size_t captured_length;
    r1_error first_use_error;
    r1_error transport_error;
} r1_retained_log_result;

/* Provider-neutral form of the registered channel-0 RTT transmit callback. */
typedef struct {
    bool write;
    unsigned channel;
    const uint8_t *bytes;
    size_t length;
} r1_rtt_write_plan;

void r1_retained_log_reset(r1_retained_log *log);
r1_error r1_retained_log_append_rendered(
    r1_retained_log *log, const uint8_t *rendered, size_t rendered_length,
    r1_retained_log_first_use_fn first_use, void *first_use_context,
    r1_retained_log_write_fn write, void *write_context,
    r1_retained_log_result *result);
r1_error r1_rtt_channel0_write_plan_build(
    const uint8_t *bytes, size_t length, r1_rtt_write_plan *plan);

#endif
