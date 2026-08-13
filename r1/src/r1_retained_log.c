#include "openr1/r1_retained_log.h"

static void clear_bytes(uint8_t *bytes, size_t length) {
    for (size_t index = 0u; index < length; ++index) {
        bytes[index] = 0u;
    }
}

void r1_retained_log_reset(r1_retained_log *log) {
    if (log == NULL) {
        return;
    }
    log->initialized = false;
    log->length = 0u;
    clear_bytes(log->bytes, sizeof(log->bytes));
}

r1_error r1_retained_log_append_rendered(
    r1_retained_log *log, const uint8_t *rendered, size_t rendered_length,
    r1_retained_log_first_use_fn first_use, void *first_use_context,
    r1_retained_log_write_fn write, void *write_context,
    r1_retained_log_result *result) {
    if (log == NULL || result == NULL ||
        (rendered == NULL && rendered_length != 0u)) {
        return R1_ERROR_ARGUMENT;
    }

    *result = (r1_retained_log_result){
        .first_use_error = R1_OK,
        .transport_error = R1_OK,
    };
    if (rendered == NULL) {
        return R1_OK;
    }

    if (!log->initialized) {
        log->initialized = true;
        log->length = 0u;
        clear_bytes(log->bytes, sizeof(log->bytes));
        result->initialized_now = true;
        if (first_use != NULL) {
            result->first_use_error = first_use(first_use_context);
        }
    }

    if (rendered_length == 0u) {
        return R1_OK;
    }
    if (log->length >= R1_RETAINED_LOG_APPEND_LIMIT) {
        result->truncated = true;
        return R1_OK;
    }

    const size_t available =
        R1_RETAINED_LOG_PAYLOAD_LIMIT - (size_t)log->length;
    if (available == 0u) {
        result->truncated = true;
        return R1_OK;
    }
    const size_t captured = rendered_length < available
        ? rendered_length : available;
    const size_t start = (size_t)log->length;
    for (size_t index = 0u; index < captured; ++index) {
        log->bytes[start + index] = rendered[index];
    }
    log->bytes[start + captured] = (uint8_t)'\n';
    log->length = (uint16_t)(start + captured + 1u);

    result->appended = true;
    result->truncated = captured != rendered_length;
    result->captured_length = captured;
    if (write != NULL) {
        result->transport_error = write(
            write_context, log->bytes + start, captured + 1u);
    }
    return R1_OK;
}
