#include "openr1/r1_persistence.h"

typedef struct {
    r1_sleep_history *history;
    r1_error error;
} restore_context;

r1_error r1_sleep_persist(r1_sleep_db *database, const r1_sleep_session *session) {
    if (database == NULL || session == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    uint8_t body[R1_SLEEP_STORED_MAX_BYTES];
    size_t written = 0u;
    r1_error error = r1_sleep_encode_compact(session, body, sizeof body, &written);
    if (error != R1_OK) {
        return error;
    }
    return r1_sleep_db_append(database, body, written);
}

r1_error r1_sleep_persist_tracked(r1_sleep_db *database, r1_sleep_session *session) {
    if (database == NULL || session == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    uint8_t body[R1_SLEEP_STORED_MAX_BYTES];
    size_t written = 0u;
    r1_error error = r1_sleep_encode_compact(session, body, sizeof body, &written);
    if (error != R1_OK) {
        return error;
    }
    uint32_t header_offset = 0u;
    error = r1_sleep_db_append_tracked(database, body, written, &header_offset);
    if (error == R1_OK) {
        session->has_storage_record = true;
        session->storage_header_offset = header_offset;
    }
    return error;
}

static bool restore_record(void *opaque, const r1_sleep_db_record *record,
                           const uint8_t *body, size_t length) {
    restore_context *context = opaque;
    r1_sleep_session session;
    context->error = r1_sleep_decode_compact(body, length, record->synchronized, &session);
    if (context->error != R1_OK) {
        return false;
    }
    context->error = r1_sleep_store(context->history, &session);
    if (context->error != R1_OK) {
        return false;
    }
    const size_t stored = ((size_t)context->history->read_index +
                           context->history->count - 1u) % R1_SLEEP_SESSION_MAX;
    context->history->sessions[stored].synchronized = record->synchronized;
    context->history->sessions[stored].has_storage_record = true;
    context->history->sessions[stored].storage_header_offset = record->header_offset;
    return true;
}

r1_error r1_sleep_commit_synchronized(void *context,
                                      const r1_sleep_session *session) {
    if (context == NULL || session == NULL || !session->has_storage_record) {
        return R1_ERROR_ARGUMENT;
    }
    r1_sleep_db *database = context;
    return r1_sleep_db_mark_synchronized(database, session->storage_header_offset,
                                         session->start_timestamp,
                                         session->end_timestamp);
}

r1_error r1_sleep_restore(r1_sleep_db *database, r1_sleep_history *history) {
    if (database == NULL || history == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *history = (r1_sleep_history){0};
    restore_context context = {history, R1_OK};
    size_t visited = 0u;
    const r1_error error = r1_sleep_db_iterate(database, false, restore_record,
                                                &context, &visited);
    (void)visited;
    return error == R1_OK ? context.error : error;
}
