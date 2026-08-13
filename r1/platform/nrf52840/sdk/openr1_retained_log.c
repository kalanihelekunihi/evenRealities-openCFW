#include <limits.h>

#include "SEGGER_RTT.h"
#include "openr1/r1_retained_log.h"

r1_error openr1_retained_log_rtt_write(
    void *context, const uint8_t *bytes, size_t length) {
    const unsigned channel = context == NULL
        ? 0u : *(const unsigned *)context;
    if (bytes == NULL || length > (size_t)UINT_MAX) {
        return R1_ERROR_ARGUMENT;
    }
    const unsigned written = SEGGER_RTT_Write(
        channel, bytes, (unsigned)length);
    return written == (unsigned)length ? R1_OK : R1_ERROR_CAPACITY;
}

typedef struct {
    void (*reset)(r1_retained_log *);
    r1_error (*append_rendered)(
        r1_retained_log *, const uint8_t *, size_t,
        r1_retained_log_first_use_fn, void *, r1_retained_log_write_fn,
        void *, r1_retained_log_result *);
    r1_retained_log_write_fn rtt_write;
} openr1_retained_log_api;

__attribute__((used, section(".openr1_retained_log_api")))
static const openr1_retained_log_api retained_log_api = {
    r1_retained_log_reset,
    r1_retained_log_append_rendered,
    openr1_retained_log_rtt_write,
};
